import subprocess
import os
from engine.awsUploader import awsUploader
from engine.aws_upload_config import aws_config

def run_pgloader_script():
    print("🚀 Running pgloader migration script via WSL...")

    script_path = "/mnt/c/Users/Lior/Desktop/Lior/שנה 3/סדנה/LastYearProject/engine/DBconvertor/newScript.sh"
    postgres_conn_string = "postgresql://postgres:postgres@172.24.128.1:5432/sakila"

    schema_path = "/mnt/c/Users/Lior/Desktop/Lior/שנה 3/סדנה/LastYearProject/engine/DBconvertor/sakila-schema.sql"
    data_path = "/mnt/c/Users/Lior/Desktop/Lior/שנה 3/סדנה/LastYearProject/engine/DBconvertor/sakila-data.sql"

    command = [
        "wsl",
        "bash",
        script_path,
        "root",
        "rootpass",
        postgres_conn_string,
        schema_path,
        data_path
    ]

    subprocess.run(command, check=True)
    print("✅ pgloader migration completed.")

def export_pg_dump_from_windows():
    print("📦 Exporting PostgreSQL database to output.sql using Windows pg_dump...")

    output_path = r"C:\Users\Lior\Desktop\Lior\שנה 3\סדנה\LastYearProject\output.sql"
    pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"

    command = [
        pg_dump_path,
        "-U", "postgres",
        "-h", "localhost",
        "-p", "5432",
        "-d", "sakila",
        "-f", output_path
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = "lior"

    subprocess.run(command, env=env, check=True)
    print(f"✅ Export completed successfully: {output_path}")

def upload_to_postgres_rds():
    print("🚀 Uploading output.sql to AWS RDS PostgreSQL...")

    uploader = awsUploader()
    uploader.set_postgres_connection_details(
        "postgres-dest-db.cdg0qswm8uxu.us-east-1.rds.amazonaws.com",
        aws_config["destination"]
    )

    uploader.upload_postgres("output.sql")
    print("✅ Upload to RDS completed successfully.")

def main():
    run_pgloader_script()
    export_pg_dump_from_windows()
    upload_to_postgres_rds()

if __name__ == "__main__":
    main()
