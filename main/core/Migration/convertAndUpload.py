import subprocess
import os
from main.core.uploader.awsUploader import awsUploader
from main.config.aws_config import aws_config
from main.config.paths_config import SCHEMA_SQL, DATA_SQL, OUTPUT_SQL, MIGRATION_SCRIPT

def run_pgloader_script():
    print("🚀 Running pgloader migration script via WSL...")

    # Convert Windows paths to WSL paths using wslpath
    def to_wsl_path(path):
        path = path.replace("\\", "/") # Make sure it's using Unix-style slashes
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

    # IMPORTANT: Replace this IP with the output of `ipconfig` under "WSL" section on your computer
    postgres_conn_string = "postgresql://postgres:postgres@192.168.1.206:5432/sakila"

    command = [
        "wsl",
        "bash",   ## IMPORTANT - USED TO BE BASH NOW SH
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
def export_pg_dump_from_windows():
    print("📦 Exporting PostgreSQL database to output.sql using Windows pg_dump...")

    pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" # Adjust if PostgreSQL version/path differs

    command = [
        pg_dump_path,
        "-U", "postgres",
        "-h", "localhost",
        "-p", "5432",
        "-d", "sakila",
        "-f", OUTPUT_SQL
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = "postgres" #Replace with your local PostgreSQL password

    subprocess.run(command, env=env, check=True)
    print(f"✅ Export completed successfully: {OUTPUT_SQL}")

def upload_to_postgres_rds():
    print("🚀 Uploading output.sql to AWS RDS PostgreSQL...")

    uploader = awsUploader()
    uploader.set_postgres_connection_details(
        "postgres-dest-db.cr6a6e6uczdi.us-east-1.rds.amazonaws.com",
        aws_config["destination"]
    )

    uploader.upload_postgres(OUTPUT_SQL)
    print("✅ Upload to RDS completed successfully.")

def main():
    # if session is over run :
    #uploader = awsUploader()
    #uploader.get_or_create_endpoints(aws_config)
    run_pgloader_script()
    export_pg_dump_from_windows()
    upload_to_postgres_rds()
if __name__ == "__main__":
    main()
