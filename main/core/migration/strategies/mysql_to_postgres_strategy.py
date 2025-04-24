import subprocess
import os
from main.core.uploader.awsUploader import awsUploader
from main.config.aws_config import aws_config
from main.config.paths_config import SCHEMA_SQL, DATA_SQL, OUTPUT_SQL, MIGRATION_SCRIPT
from main.core.migration.strategies.base_migration_strategy import BaseMigrationStrategy
from main.utils.network_utils import get_windows_host_ip

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
load_dotenv()


class MySQLToPostgresStrategy(BaseMigrationStrategy):
    def run(self, source_endpoint, destination_endpoint, schema_name):
        self.source_endpoint = source_endpoint
        self.destination_endpoint = destination_endpoint
        self.run_pgloader_script(schema_name)
        self.export_pg_dump_from_windows(schema_name)
        self.upload_to_postgres_rds()
        self.upload_to_mysql_rds()
    def run_pgloader_script(self, schema_name):
        print("🚀 Running pgloader migration script via WSL...")

        def to_wsl_path(path):
            path = path.replace("\\", "/")
            completed = subprocess.run(
                ["wsl", "wslpath", "-a", "-u", path],
                capture_output=True,
                text=True
            )
            if completed.returncode != 0:
                print("❌ Failed to convert path:", path)
                print(completed.stderr)
                raise Exception("wslpath failed")
            return completed.stdout.strip()

        schema_path_wsl = to_wsl_path(SCHEMA_SQL)
        data_path_wsl = to_wsl_path(DATA_SQL)
        script_path_wsl = to_wsl_path(MIGRATION_SCRIPT)

        # Use the source endpoint dynamically (e.g., MySQL)
        # IMPORTANT: Replace this IP with the output of `ipconfig` under "WSL" section on your computer
        host_ip = get_windows_host_ip()

        postgres_conn_string = f"postgresql://postgres:postgres@{host_ip}:5432/{self.schema_name}"
        self.create_postgres_database_if_not_exists(host_ip, self.schema_name)
        command = [
            "wsl",
            "bash",
            script_path_wsl,
            "root",
            "rootpass",
            postgres_conn_string,
            schema_name,
            schema_path_wsl,
            data_path_wsl,
        ]

        print("Running command:", " ".join(command))
        subprocess.run(command, check=True)
        print("✅ pgloader migration completed.")

    def export_pg_dump_from_windows(self, schema_name):
        print("📦 Exporting PostgreSQL database to output.sql...")

        pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"

        command = [
            pg_dump_path,
            "-U", "postgres",
            "-h", "localhost",
            "-p", "5432",
            "-d", f"{schema_name}",
            "-f", OUTPUT_SQL
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = os.getenv("PGPASSWORD")
        # before it was: env["PGPASSWORD"] = "postgres"
        #TODO: important!! my PGPASSWORD is: "lior" and Niv's is: "postgres"

        subprocess.run(command, env=env, check=True)
        print(f"✅ Export completed successfully: {OUTPUT_SQL}")

    def upload_to_postgres_rds(self):
        print("🚀 Uploading output.sql to AWS RDS PostgreSQL...")

        uploader = awsUploader()
        uploader.set_postgres_connection_details(
            self.destination_endpoint,  # ← dynamic endpoint!
            aws_config["destination"]
        )
        uploader.upload_postgres(OUTPUT_SQL)
        print("✅ Upload to RDS completed.")

    def upload_to_mysql_rds(self):
        print("🚀 Uploading schema and data to AWS RDS MySQL...")

        uploader = awsUploader()
        uploader.set_mysql_connection_details(
            self.source_endpoint,
            aws_config["source"]
        )

        # נתחיל עם schema
        uploader.upload(SCHEMA_SQL)
        print("✅ Schema uploaded to MySQL.")

        # ואז נוסיף את הנתונים
        uploader.upload(DATA_SQL)
        print("✅ Data uploaded to MySQL.")

    def  create_postgres_database_if_not_exists(self, host, dbname, user="postgres", password="postgres", port=5432):
        try:
            # Connect to the default 'postgres' database
            conn = psycopg2.connect(
                dbname="postgres",
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()

            # Create the database if it doesn't exist
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
            exists = cur.fetchone()
            if not exists:
                print(f"🛠️ Creating PostgreSQL database '{dbname}'...")
                cur.execute(f'CREATE DATABASE "{dbname}";')
            else:
                print(f"✅ Database '{dbname}' already exists.")

            cur.close()
            conn.close()
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            raise


if __name__ == '__main__':
    MySQLToPostgresStrategy(shcema_name="employees").create_postgres_database_if_not_exists(get_windows_host_ip(), "employees")
