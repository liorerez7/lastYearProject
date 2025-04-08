import subprocess
import os

def run_pgloader_script():
    print("🚀 Running pgloader migration script via WSL...")

    script_path = "/mnt/c/Users/Lior/Desktop/Lior/שנה 3/סדנה/LastYearProject/engine/DBconvertor/newScript.sh"
    postgres_conn_string = "postgresql://postgres:postgres@172.24.128.1:5432/sakila"

    command = [
        "wsl",
        "bash",
        script_path,
        "root",
        "rootpass",
        postgres_conn_string,
        "sakila-schema.sql",
        "sakila-data.sql"
    ]

    subprocess.run(command, check=True)
    print("✅ pgloader migration completed.")

def export_pg_dump_from_windows():
    print("📦 Exporting PostgreSQL database to output.sql using Windows pg_dump...")

    # הנתיב המלא לקובץ output.sql בתוך DBconvertor (כמו שעובד לך)
    output_path = r"C:\Users\Lior\Desktop\Lior\שנה 3\סדנה\LastYearProject\engine\DBconvertor\output.sql"

    # נתיב מלא לקובץ pg_dump לפי הגרסה שלך
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


def main():
    run_pgloader_script()
    export_pg_dump_from_windows()

if __name__ == "__main__":
    main()
