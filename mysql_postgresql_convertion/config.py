# mysql_postgresql_convertion/config.py

MYSQL_CONFIG = {
    "host": "mysql-source-db2.cdg0qswm8uxu.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "StrongPassword123",
    "database": "sakila",
    "port": 3306
}

POSTGRES_CONFIG = {
    "host": "postgres-dest-db.cdg0qswm8uxu.us-east-1.rds.amazonaws.com",  # ← שים כאן את ה־endpoint של PostgreSQL RDS
    "user": "pgadmin",
    "password": "StrongPassword456",
    "dbname": "sakila_migrated",
    "port": 5432
}
