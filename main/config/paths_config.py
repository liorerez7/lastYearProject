import os

# Root project path (main package)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Data files (SQLs and output)
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_SQL = os.path.join(DATA_DIR, "output.sql")
SCHEMA_SQL = os.path.join(DATA_DIR, "sakila-schema.sql")
DATA_SQL = os.path.join(DATA_DIR, "sakila-data.sql")

# Scripts
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
MIGRATION_SCRIPT = os.path.join(SCRIPTS_DIR, "mysql_to_postgres.sh.sh")

