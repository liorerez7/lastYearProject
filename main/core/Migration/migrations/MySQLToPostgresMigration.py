import subprocess
import os
from main.core.uploader.awsUploader import awsUploader
from main.config.aws_config import aws_config
from main.config.paths_config import SCHEMA_SQL, DATA_SQL, OUTPUT_SQL, MIGRATION_SCRIPT
from main.core.Migration.migrations.base_strategy import MigrationStrategy
from main.utils.network_utils import get_windows_host_ip

class MySQLToPostgresMigration(MigrationStrategy):
    def run(self, source_endpoint, destination_endpoint):
        self.destination_endpoint = destination_endpoint
        self.run_pgloader_script()
        self.export_pg_dump_from_windows()
        self.upload_to_postgres_rds()

    def run_pgloader_script(self):
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
        postgres_conn_string = f"postgresql://postgres:postgres@{host_ip}:5432/sakila"

        command = [
            "wsl",
            "bash",
            script_path_wsl,
            "root",
            "rootpass",
            postgres_conn_string,
            schema_path_wsl,
            data_path_wsl
        ]

        print("Running command:", " ".join(command))
        subprocess.run(command, check=True)
        print("✅ pgloader migration completed.")

    def export_pg_dump_from_windows(self):
        print("📦 Exporting PostgreSQL database to output.sql...")

        pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"

        command = [
            pg_dump_path,
            "-U", "postgres",
            "-h", "localhost",
            "-p", "5432",
            "-d", "sakila",
            "-f", OUTPUT_SQL
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = "postgres"

        subprocess.run(command, env=env, check=True)
        print(f"✅ Export completed successfully: {OUTPUT_SQL}")

    def upload_to_postgres_rds(self):
        print("🚀 Uploading output.sql to AWS RDS PostgreSQL...")

        uploader = awsUploader()
        uploader.set_postgres_connection_details(
            self.destination_endpoint,   # ← dynamic endpoint!
            aws_config["destination"]
        )
        uploader.upload_postgres(OUTPUT_SQL)
        print("✅ Upload to RDS completed.")