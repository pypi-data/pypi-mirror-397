"""
Core schema evolution logic for Spark DataFrames and Hive tables.
"""

from pyspark.sql.functions import lit
from .schema_utils import (
    get_table_schema,
    get_dataframe_schema_dict,
    map_spark_type_to_hive_type,
    is_type_change_compatible,
    normalize_hive_type,
    map_hive_type_to_spark_type
)


def evolve_schema(spark, database_name, table_name, new_schema_dict, logger):
    """Apply schema evolution by adding new columns or changing column types
    
    Args:
        spark: SparkSession
        database_name: Name of the database
        table_name: Name of the table
        new_schema_dict: Dictionary of new schema (column_name -> data_type)
        logger: Logger instance
        
    Returns:
        tuple: (alter_statements, fallback_column_mappings)
            - alter_statements: List of ALTER TABLE statements executed
            - fallback_column_mappings: Dict mapping old column names to new column names (for fallback columns)
    """
    try:
        fully_qualified_name = f"{database_name}.{table_name}"
        existing_schema = get_table_schema(spark, database_name, table_name)
        
        if existing_schema is None:
            logger.info(f"Table {fully_qualified_name} does not exist. Will be created on first write.")
            return [], {}
        
        alter_statements = []
        type_changes = []
        new_columns = []
        
        # Check for new columns and type changes
        for col_name, new_col_type in new_schema_dict.items():
            new_hive_type = map_spark_type_to_hive_type(new_col_type)
            
            if col_name not in existing_schema:
                # New column
                new_columns.append((col_name, new_hive_type))
                logger.info(f"New column detected: {col_name} ({new_col_type} -> {new_hive_type})")
            else:
                # Existing column - check for type change
                existing_hive_type = existing_schema[col_name]
                existing_normalized = normalize_hive_type(existing_hive_type)
                new_normalized = normalize_hive_type(new_hive_type)
                
                if existing_normalized != new_normalized:
                    if is_type_change_compatible(existing_hive_type, new_hive_type):
                        # Compatible type change (e.g., int -> string)
                        type_changes.append((col_name, existing_hive_type, new_hive_type))
                        logger.info(f"Type change detected: {col_name} ({existing_hive_type} -> {new_hive_type}) - Compatible change")
                    else:
                        # Incompatible type change - create new column with suffix
                        new_col_name = f"{col_name}_v2"
                        new_columns.append((new_col_name, new_hive_type))
                        logger.warning(f"Incompatible type change for {col_name}: {existing_hive_type} -> {new_hive_type}")
                        logger.info(f"Creating new column {new_col_name} with type {new_hive_type} to preserve existing data")
        
        # Track columns that need to be renamed in DataFrame (fallback columns)
        fallback_column_mappings = {}
        
        # Apply ALTER TABLE statements for type changes
        for col_name, old_type, new_type in type_changes:
            try:
                alter_sql = f"ALTER TABLE {fully_qualified_name} CHANGE COLUMN {col_name} {col_name} {new_type}"
                logger.info(f"Executing: {alter_sql}")
                spark.sql(alter_sql)
                alter_statements.append(alter_sql)
                logger.info(f"Successfully changed column {col_name} type from {old_type} to {new_type}")
            except Exception as e:
                logger.error(f"Failed to change column {col_name} type: {e}")
                # Try to create a new column instead
                new_col_name = f"{col_name}_v2"
                new_columns.append((new_col_name, new_type))
                fallback_column_mappings[col_name] = new_col_name
                logger.info(f"Falling back to creating new column {new_col_name}")
        
        # Apply ALTER TABLE statements for new columns
        for col_name, hive_type in new_columns:
            try:
                alter_sql = f"ALTER TABLE {fully_qualified_name} ADD COLUMNS ({col_name} {hive_type})"
                logger.info(f"Executing: {alter_sql}")
                spark.sql(alter_sql)
                alter_statements.append(alter_sql)
                logger.info(f"Successfully added column {col_name} to {fully_qualified_name}")
            except Exception as e:
                logger.error(f"Failed to add column {col_name}: {e}")
                # Continue with other columns even if one fails
                continue
        
        return alter_statements, fallback_column_mappings
    except Exception as e:
        logger.error(f"Error during schema evolution: {e}", exc_info=True)
        return [], {}


def align_dataframe_with_table(df, spark, database_name, table_name, column_mappings, logger):
    """Align DataFrame schema with table schema by adding missing columns and renaming columns
    
    Args:
        df: PySpark DataFrame
        spark: SparkSession
        database_name: Name of the database
        table_name: Name of the table
        column_mappings: Dictionary mapping old column names to new column names
        logger: Logger instance
        
    Returns:
        PySpark DataFrame: DataFrame with aligned schema
    """
    # Apply column name mappings if needed (for incompatible type changes or fallback columns)
    if column_mappings:
        for old_name, new_name in column_mappings.items():
            if old_name in df.columns:
                df = df.withColumnRenamed(old_name, new_name)
                logger.info(f"Renamed column {old_name} to {new_name} in DataFrame")
    
    # Get updated table schema to check for missing columns
    existing_schema = get_table_schema(spark, database_name, table_name)
    if existing_schema:
        updated_schema = get_table_schema(spark, database_name, table_name)
        if updated_schema:
            # Get list of columns that were renamed
            renamed_from_columns = set(column_mappings.keys())
            renamed_to_columns = set(column_mappings.values())
            
            # Add missing columns from table to DataFrame (as null)
            for table_col, table_col_type in updated_schema.items():
                # Skip if column already exists in DataFrame
                if table_col in df.columns:
                    continue
                
                # If this is a renamed column (old name), we need to add it back as null
                # because the table still has the old column
                if table_col in renamed_from_columns:
                    spark_type = map_hive_type_to_spark_type(table_col_type)
                    df = df.withColumn(table_col, lit(None).cast(spark_type))
                    logger.info(f"Added old column {table_col} back to DataFrame (as null, type: {spark_type}) - table still has this column")
                # If this is a new column that wasn't renamed, add it
                elif table_col not in renamed_to_columns:
                    spark_type = map_hive_type_to_spark_type(table_col_type)
                    df = df.withColumn(table_col, lit(None).cast(spark_type))
                    logger.info(f"Added missing column {table_col} to DataFrame (as null, type: {spark_type})")
    
    return df


def evolve_dataframe_schema(
    df,
    spark,
    database_name,
    table_name,
    logger
):
    """Evolve table schema and return ALTER statements and transformed DataFrame
    
    This is the main function to use for schema evolution. It:
    1. Detects schema changes between DataFrame and table
    2. Applies ALTER TABLE statements for new columns and type changes
    3. Aligns DataFrame schema with table schema
    4. Returns ALTER statements, transformed DataFrame, and schema change flag
    
    Args:
        df: PySpark DataFrame to evolve
        spark: SparkSession
        database_name: Name of the Hive/Spark SQL database
        table_name: Name of the target Hive table
        logger: Logger instance
        
    Returns:
        tuple: (alter_statements, transformed_df, column_mappings, schema_changed)
            - alter_statements: List of ALTER TABLE statements that were executed
            - transformed_df: DataFrame with schema aligned to table
            - column_mappings: Dictionary mapping old column names to new column names (for renamed columns)
            - schema_changed: Boolean flag indicating if schema changes were made (True if any ALTER TABLE statements were executed)
        
    Raises:
        Exception: If schema evolution fails
        
    Example:
        from schema_evolution import evolve_dataframe_schema
        import logging
        
        logger = logging.getLogger(__name__)
        alter_statements, transformed_df, column_mappings, schema_changed = evolve_dataframe_schema(
            df=my_dataframe,
            spark=spark,
            database_name="gold_test",
            table_name="evolution_test",
            logger=logger
        )
        
        # Conditional processing based on schema changes
        if schema_changed:
            logger.warning("Schema changes detected! Sending notification...")
            send_notification(alter_statements)
        
        # Inspect the changes
        for stmt in alter_statements:
            print(f"Executed: {stmt}")
        
        # Write the transformed DataFrame
        transformed_df.write.mode("append").saveAsTable("gold_test.evolution_test")
    """
    try:
        # Get new schema
        new_schema_dict = get_dataframe_schema_dict(df)
        
        # Apply schema evolution
        fully_qualified_name = f"{database_name}.{table_name}"
        existing_schema = get_table_schema(spark, database_name, table_name)
        
        column_mappings = {}  # Track column name changes for incompatible type changes
        alter_statements = []
        schema_changed = False
        
        if existing_schema:
            logger.info(f"Table {fully_qualified_name} exists. Checking for schema changes...")
            
            # Check for incompatible type changes that require new columns (before ALTER TABLE attempt)
            for col_name, new_col_type in new_schema_dict.items():
                if col_name in existing_schema:
                    existing_hive_type = existing_schema[col_name]
                    new_hive_type = map_spark_type_to_hive_type(new_col_type)
                    existing_normalized = normalize_hive_type(existing_hive_type)
                    new_normalized = normalize_hive_type(new_hive_type)
                    
                    if existing_normalized != new_normalized and not is_type_change_compatible(existing_hive_type, new_hive_type):
                        # Map old column name to new column name with suffix
                        new_col_name = f"{col_name}_v2"
                        column_mappings[col_name] = new_col_name
                        logger.info(f"Will map column {col_name} to {new_col_name} due to incompatible type change")
            
            alter_statements, fallback_mappings = evolve_schema(spark, database_name, table_name, new_schema_dict, logger)
            
            # Merge fallback mappings (from failed ALTER TABLE CHANGE COLUMN) with incompatible type change mappings
            column_mappings.update(fallback_mappings)
            
            # Set schema_changed flag if any ALTER TABLE statements were executed
            schema_changed = len(alter_statements) > 0
            
            if alter_statements:
                logger.info(f"Schema evolution completed. Applied {len(alter_statements)} ALTER TABLE statements.")
            else:
                logger.info("No schema changes detected.")
        else:
            logger.info(f"Table {fully_qualified_name} does not exist. Will be created on first write.")
            # Table doesn't exist, so no schema changes (table will be created on first write)
            schema_changed = False
        
        # Align DataFrame schema with table schema
        transformed_df = align_dataframe_with_table(df, spark, database_name, table_name, column_mappings, logger)
        
        return alter_statements, transformed_df, column_mappings, schema_changed
        
    except Exception as e:
        logger.error(f"Error processing DataFrame with schema evolution: {e}", exc_info=True)
        raise


def evolve_and_write_dataframe(
    df,
    spark,
    database_name,
    table_name,
    hdfs_location,
    logger,
    write_mode="append"
):
    """Evolve table schema and write DataFrame with schema evolution support
    
    Convenience function that calls evolve_dataframe_schema() and then writes the DataFrame.
    
    Args:
        df: PySpark DataFrame to write
        spark: SparkSession
        database_name: Name of the Hive/Spark SQL database
        table_name: Name of the target Hive table
        hdfs_location: Base HDFS path for external table data
        logger: Logger instance
        write_mode: Write mode - 'append', 'overwrite', or 'ignore' (default: 'append')
        
    Returns:
        bool: True if successful
        
    Raises:
        Exception: If schema evolution or write fails
        
    Example:
        from schema_evolution import evolve_and_write_dataframe
        import logging
        
        logger = logging.getLogger(__name__)
        evolve_and_write_dataframe(
            df=my_dataframe,
            spark=spark,
            database_name="gold_test",
            table_name="evolution_test",
            hdfs_location="/user/rfhcdev/prod/warehouse",
            logger=logger,
            write_mode="append"
        )
    """
    try:
        # Evolve schema and get transformed DataFrame
        alter_statements, transformed_df, column_mappings, schema_changed = evolve_dataframe_schema(
            df=df,
            spark=spark,
            database_name=database_name,
            table_name=table_name,
            logger=logger
        )
        
        # Prepare target path and table name
        target_path = f"{hdfs_location}/{database_name}/{table_name}"
        fully_qualified_table_name = f"{database_name}.{table_name}"
        
        logger.info(f"Writing DataFrame to {fully_qualified_table_name}")
        logger.info(f"Target HDFS path: {target_path}")
        
        # Write with mergeSchema option to handle any remaining schema differences
        transformed_df.write \
            .mode(write_mode) \
            .format("parquet") \
            .option("path", target_path) \
            .option("mergeSchema", "true") \
            .saveAsTable(fully_qualified_table_name)
        
        logger.info(f"Successfully wrote data to {fully_qualified_table_name}")
        
        # Log final schema
        logger.info("Final table schema:")
        final_df = spark.table(fully_qualified_table_name)
        final_df.printSchema()
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing DataFrame with schema evolution: {e}", exc_info=True)
        raise

