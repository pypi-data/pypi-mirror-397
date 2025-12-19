# Schema Evolution Package

A reusable Python package for handling schema evolution in Spark/Hive tables.

## Installation

The package is located in the `schema_evolution` directory. To use it, ensure the directory is in your Python path or import it directly.

## Quick Start

### Recommended Approach (Returns ALTER statements and transformed DataFrame)

```python
from schema_evolution import evolve_dataframe_schema
import logging

logger = logging.getLogger(__name__)

# Your DataFrame
df = spark.read.csv("path/to/data.csv", header=True, inferSchema=True)

# Evolve schema and get transformed DataFrame
alter_statements, transformed_df, column_mappings, schema_changed = evolve_dataframe_schema(
    df=df,
    spark=spark,
    database_name="gold_test",
    table_name="evolution_test",
    logger=logger
)

# Conditional processing based on schema changes
if schema_changed:
    print(f"⚠️  Schema changes detected! Executed {len(alter_statements)} ALTER TABLE statements:")
    for stmt in alter_statements:
        print(f"  - {stmt}")
    # Optionally: send notification, update metadata, etc.
else:
    print("✓ No schema changes - table schema matches DataFrame")

# Write the transformed DataFrame
transformed_df.write \
    .mode("append") \
    .format("parquet") \
    .option("path", "/user/rfhcdev/prod/warehouse/gold_test/evolution_test") \
    .option("mergeSchema", "true") \
    .saveAsTable("gold_test.evolution_test")
```

### Convenience Approach (Directly writes)

```python
from schema_evolution import evolve_and_write_dataframe
import logging

logger = logging.getLogger(__name__)

# Your DataFrame
df = spark.read.csv("path/to/data.csv", header=True, inferSchema=True)

# Evolve schema and write (all in one)
evolve_and_write_dataframe(
    df=df,
    spark=spark,
    database_name="gold_test",
    table_name="evolution_test",
    hdfs_location="/user/rfhcdev/prod/warehouse",
    logger=logger,
    write_mode="append"
)
```

## Main Functions

### `evolve_dataframe_schema()` (Recommended)

The main function that handles schema evolution and returns ALTER statements and transformed DataFrame.

**Parameters:**

- `df` (DataFrame): PySpark DataFrame to evolve
- `spark` (SparkSession): SparkSession instance
- `database_name` (str): Name of the Hive/Spark SQL database
- `table_name` (str): Name of the target Hive table
- `logger` (Logger): Logger instance for logging

**Returns:**

- `tuple`: (alter_statements, transformed_df, column_mappings, schema_changed)
  - `alter_statements`: List of ALTER TABLE statements that were executed
  - `transformed_df`: DataFrame with schema aligned to table
  - `column_mappings`: Dictionary mapping old column names to new column names (for renamed columns)
  - `schema_changed`: Boolean flag indicating if schema changes were made (True if any ALTER TABLE statements were executed)

**Raises:**

- `Exception`: If schema evolution fails

### `evolve_and_write_dataframe()` (Convenience Function)

Convenience function that calls `evolve_dataframe_schema()` and then writes the DataFrame.

**Parameters:**

- `df` (DataFrame): PySpark DataFrame to write
- `spark` (SparkSession): SparkSession instance
- `database_name` (str): Name of the Hive/Spark SQL database
- `table_name` (str): Name of the target Hive table
- `hdfs_location` (str): Base HDFS path for external table data
- `logger` (Logger): Logger instance for logging
- `write_mode` (str): Write mode - 'append', 'overwrite', or 'ignore' (default: 'append')

**Returns:**

- `bool`: True if successful

**Raises:**

- `Exception`: If schema evolution or write fails

## Features

- ✅ Automatic detection of new columns
- ✅ Automatic type change handling (compatible and incompatible)
- ✅ Fallback to new columns when ALTER TABLE CHANGE COLUMN fails
- ✅ DataFrame schema alignment with table schema
- ✅ Missing column handling (adds as null)
- ✅ Comprehensive logging

## Schema Evolution Scenarios

### 1. New Columns

When new columns are detected, they are automatically added using `ALTER TABLE ADD COLUMNS`.

### 2. Compatible Type Changes

For compatible type changes (e.g., `int` → `string`), the pipeline attempts to change the column type using `ALTER TABLE CHANGE COLUMN`.

### 3. Incompatible Type Changes / Failed ALTER TABLE

When type changes fail or are incompatible, the pipeline creates a new column with `_v2` suffix (e.g., `age_v2`) to preserve existing data.

## Utility Functions

The package also exports utility functions:

- `get_table_schema()`: Get current table schema
- `get_dataframe_schema_dict()`: Convert DataFrame schema to dictionary
- `map_spark_type_to_hive_type()`: Map Spark types to Hive types
- `is_type_change_compatible()`: Check if type change is compatible
- `normalize_hive_type()`: Normalize Hive type strings
- `map_hive_type_to_spark_type()`: Map Hive types to Spark types

## Example Usage in Your Code

```python
from pyspark.sql import SparkSession
from schema_evolution import evolve_dataframe_schema
import logging

# Setup
spark = SparkSession.builder.enableHiveSupport().getOrCreate()
logger = logging.getLogger("my_app")

# Process your data
df = spark.read.json("data.json")

# Evolve schema and get transformed DataFrame
alter_statements, transformed_df, column_mappings, schema_changed = evolve_dataframe_schema(
    df=df,
    spark=spark,
    database_name="my_database",
    table_name="my_table",
    logger=logger
)

# Conditional processing based on schema changes
if schema_changed:
    logger.warning(f"Schema changes detected! Applied {len(alter_statements)} ALTER TABLE statements")
    for stmt in alter_statements:
        logger.info(f"  {stmt}")
    # Optionally: send notification, update metadata, trigger downstream processes, etc.
else:
    logger.info("No schema changes - proceeding with normal write")

# Write the transformed DataFrame
transformed_df.write \
    .mode("append") \
    .format("parquet") \
    .option("path", "/user/myuser/warehouse/my_database/my_table") \
    .option("mergeSchema", "true") \
    .saveAsTable("my_database.my_table")
```

## Package Structure

```
schema_evolution/
├── __init__.py          # Package initialization and exports
├── schema_evolution.py  # Core evolution logic
├── schema_utils.py      # Utility functions
└── README.md           # This file
```

## Version

Current version: 1.0.0
