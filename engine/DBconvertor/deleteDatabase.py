import boto3
import pymysql
from engine.aws_upload_config import aws_config

def drop_all_tables(endpoint, config):
    connection = pymysql.connect(
        host=endpoint,
        user=config["MasterUsername"],
        password=config["MasterUserPassword"],
        db=config["DBName"],
        port=config.get("Port", 3306),
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # Get all foreign key constraints to disable
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            # Get all table names
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()

            for row in tables:
                table_name = list(row.values())[0]
                print(f"🧨 Dropping table: {table_name}")
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            connection.commit()
            print("✅ All tables dropped successfully.")

    except Exception as e:
        print(f"❌ Error while dropping tables: {e}")
    finally:
        connection.close()
        print("🔒 Connection closed.")

def main():
    rds = boto3.client("rds")
    instance_id = aws_config["source"]["DBInstanceIdentifier"]
    response = rds.describe_db_instances(DBInstanceIdentifier=instance_id)
    endpoint = response["DBInstances"][0]["Endpoint"]["Address"]

    drop_all_tables(endpoint, aws_config["source"])

if __name__ == "__main__":
    main()
