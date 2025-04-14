import pymysql
import psycopg2

# Replace with your actual credentials
host = "postgres-dest-db.cr6a6e6uczdi.us-east-1.rds.amazonaws.com"
port = 5432
user = "pgadmin"
password = "StrongPassword456"
database = "sakila_migrated"

try:
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    print("✅ Successfully connected to PostgreSQL RDS!")
    connection.close()
except Exception as e:
    print("❌ Failed to connect to PostgreSQL RDS:")
    print(e)