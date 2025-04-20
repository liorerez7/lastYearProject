
import psycopg2
from main.sakila_benchmark.sakila_comparsion_mySQL_postgres import (
    SUPABASE_DB_CONFIG,
    PG_CONFIG,
    MYSQL_CONFIG,
    connect_to_databases,
    insert_database,
    insert_session,
    run_benchmark_with_supabase,
    queries
)
def connect_to_supabase():
    return psycopg2.connect(**SUPABASE_DB_CONFIG)


def main():
    # Step 1: Connect to Supabase and databases
    supabase_conn = connect_to_supabase()
    supabase_cursor = supabase_conn.cursor()

    pg_conn, pg_cursor, mysql_conn, mysql_cursor = connect_to_databases()

    # Step 2: Add dummy user (or use existing)
    user_id = "00000000-0000-0000-0000-000000000001"  # Replace with a real user UUID

    # Step 3: Insert DBs and session
    source_db_id = insert_database(
        supabase_cursor, user_id,
        db_type='MySQL',
        host=MYSQL_CONFIG["host"],
        port=MYSQL_CONFIG["port"],
        version='8.0'
    )

    dest_db_id = insert_database(
        supabase_cursor, user_id,
        db_type='PostgreSQL',
        host=PG_CONFIG["host"],
        port=PG_CONFIG["port"],
        version='15'
    )

    session_description = "Benchmark comparison on sakila - local run"
    session_id = insert_session(
        supabase_cursor, user_id,
        source_db_id, dest_db_id,
        session_description
    )

    # Step 4: Run PostgreSQL and MySQL benchmarks
    run_benchmark_with_supabase(pg_cursor, "PostgreSQL", pg_conn, supabase_cursor, session_id, 'destination', queries)
    run_benchmark_with_supabase(mysql_cursor, "MySQL", mysql_conn, supabase_cursor, session_id, 'source', queries)

    # Step 5: Commit and close all
    supabase_conn.commit()

    supabase_cursor.close()
    supabase_conn.close()
    pg_cursor.close()
    pg_conn.close()
    mysql_cursor.close()
    mysql_conn.close()

    print("🎉 Benchmarking session complete and data saved to Supabase!")

# Run the main function
main()
