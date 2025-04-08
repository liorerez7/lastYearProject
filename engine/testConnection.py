import pymysql

# Replace with your actual credentials
host = "mysql-source-db2.cdg0qswm8uxu.us-east-1.rds.amazonaws.com"
port = 3306
user = "admin"
password = "StrongPassword123"
database = "sakila"

try:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=database
    )
    print("✅ Successfully connected to MySQL RDS!")
    connection.close()
except Exception as e:
    print("❌ Failed to connect to MySQL RDS:")
    print(e)
