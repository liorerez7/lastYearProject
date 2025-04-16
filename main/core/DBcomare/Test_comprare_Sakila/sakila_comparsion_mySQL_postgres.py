import time
import uuid
import argparse
import psycopg2
import mysql.connector

# List of test queries
queries_all = {
    "simple_select": "SELECT * FROM customer WHERE active = TRUE;",

    "order_by_limit": "SELECT * FROM film ORDER BY rental_rate DESC LIMIT 10;",

    "join_film_language": """
        SELECT f.title, l.name AS language
        FROM film f
        JOIN language l ON f.language_id = l.language_id;
    """,

    "agg_rentals_per_customer": """
        SELECT customer_id, COUNT(*) AS rental_count
        FROM rental
        GROUP BY customer_id
        ORDER BY rental_count DESC
        LIMIT 10;
    """,

    "multi_join_film_actor_category": """
        SELECT f.title, a.first_name, c.name AS category
        FROM film f
        JOIN film_actor fa ON f.film_id = fa.film_id
        JOIN actor a ON fa.actor_id = a.actor_id
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        LIMIT 50;
    """,

    "subquery_inventory": """
        SELECT title
        FROM film
        WHERE film_id IN (
            SELECT film_id FROM inventory WHERE store_id = 1
        );
    """,

    "count_films_per_category": """
        SELECT c.name AS category, COUNT(f.film_id) AS film_count
        FROM category c
        JOIN film_category fc ON c.category_id = fc.category_id
        JOIN film f ON f.film_id = fc.film_id
        GROUP BY c.name;
    """,

    "film_length_over_100": "SELECT title FROM film WHERE length > 100;",

    "longest_films": "SELECT title, length FROM film ORDER BY length DESC LIMIT 5;",

    "top_actors_by_film": """
        SELECT a.actor_id, a.first_name, a.last_name, COUNT(*) AS films
        FROM actor a
        JOIN film_actor fa ON a.actor_id = fa.actor_id
        GROUP BY a.actor_id
        ORDER BY films DESC
        LIMIT 10;
    """,

    "top_paying_customers": """
        SELECT customer_id, SUM(amount) AS total_paid
        FROM payment
        GROUP BY customer_id
        ORDER BY total_paid DESC
        LIMIT 5;
    """,

    "rentals_per_month": """
        SELECT DATE_TRUNC('month', rental_date) AS month, COUNT(*) AS total
        FROM rental
        GROUP BY month
        ORDER BY month;
    """,

    "active_staff": "SELECT staff_id, first_name FROM staff WHERE active = TRUE;",

    "inventory_per_store": """
        SELECT store_id, COUNT(*) AS inventory_count
        FROM inventory
        GROUP BY store_id;
    """,

    "most_rented_films": """
        SELECT f.title, COUNT(*) AS times_rented
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film f ON i.film_id = f.film_id
        GROUP BY f.title
        ORDER BY times_rented DESC
        LIMIT 10;
    """,

    "duplicate_customer_lastnames": """
        SELECT last_name, COUNT(*) AS count
        FROM customer
        GROUP BY last_name
        HAVING COUNT(*) > 1
        ORDER BY count DESC;
    """,

    "last_5_payments": "SELECT * FROM payment ORDER BY payment_date DESC LIMIT 5;",

    "films_not_in_inventory": """
        SELECT f.title
        FROM film f
        WHERE f.film_id NOT IN (SELECT DISTINCT film_id FROM inventory);
    """,

    "customers_no_rentals": """
        SELECT c.first_name, c.last_name
        FROM customer c
        LEFT JOIN rental r ON c.customer_id = r.customer_id
        WHERE r.rental_id IS NULL;
    """,

    "actor_film_categories": """
        SELECT a.first_name, a.last_name, COUNT(DISTINCT fc.category_id) AS categories
        FROM actor a
        JOIN film_actor fa ON a.actor_id = fa.actor_id
        JOIN film_category fc ON fa.film_id = fc.film_id
        GROUP BY a.actor_id;
    """,

    "top_grossing_actor": """
        SELECT a.actor_id, a.first_name, a.last_name, SUM(p.amount) AS total_revenue
        FROM actor a
        JOIN film_actor fa ON a.actor_id = fa.actor_id
        JOIN inventory i ON fa.film_id = i.film_id
        JOIN rental r ON i.inventory_id = r.inventory_id
        JOIN payment p ON r.rental_id = p.rental_id
        GROUP BY a.actor_id, a.first_name, a.last_name
        ORDER BY total_revenue DESC
        LIMIT 1;
    """,

    "rented_all_in_category": """
        SELECT c.customer_id, c.first_name, c.last_name
        FROM customer c
        WHERE NOT EXISTS (
            SELECT 1
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            WHERE fc.category_id = 1
            AND NOT EXISTS (
                SELECT 1
                FROM rental r
                JOIN inventory i ON r.inventory_id = i.inventory_id
                WHERE i.film_id = f.film_id AND r.customer_id = c.customer_id
            )
        );
    """,

    "most_rented_monthly": """
        SELECT *
        FROM (
            SELECT f.title,
                   DATE_TRUNC('month', r.rental_date) AS rental_month,
                   COUNT(*) AS rental_count,
                   RANK() OVER (PARTITION BY DATE_TRUNC('month', r.rental_date) ORDER BY COUNT(*) DESC) AS rank
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            GROUP BY f.title, rental_month
        ) ranked
        WHERE rank = 1;
    """
    ,"better for mySQL":"""SELECT payment_id, amount, payment_date
    FROM payment
    WHERE customer_id = 1
    ORDER BY payment_date DESC
    LIMIT 10;
    """
}

# === Configuration ===
SUPABASE_DB_CONFIG = {
    "host": "db.nsfhfmkgwhcfoezuhqpp.supabase.co",
    "port": 6543,
    "user": "postgres",
    "password": "Khturer7",
    "dbname": "postgres"
}
PG_CONFIG = {
    "host": "postgres-dest-db.cdg0qswm8uxu.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "user": "pgadmin",
    "password": "StrongPassword456",
    "dbname": "sakila_migrated"
}
MYSQL_CONFIG = {
    "host": "mysql-source-db2.cdg0qswm8uxu.us-east-1.rds.amazonaws.com",
    "port": 3306,
    "user": "admin",
    "password": "StrongPassword123",
    "database": "sakila"
}

queries = {
    "simple_select": "SELECT * FROM customer WHERE active = TRUE;",
    "top_actors_by_film": """
        SELECT a.actor_id, a.first_name, a.last_name, COUNT(*) AS films
        FROM actor a
        JOIN film_actor fa ON a.actor_id = fa.actor_id
        GROUP BY a.actor_id
        ORDER BY films DESC
        LIMIT 10;
    """
}

# === Supabase Insert Helpers ===
def connect_to_supabase():
    return psycopg2.connect(**SUPABASE_DB_CONFIG)

def insert_database(cursor, user_id, db_type, host, port, version):
    cursor.execute("""
        INSERT INTO databases (user_id, db_type, host, port, version)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (user_id, db_type, host, port, version))
    return cursor.fetchone()[0]

def insert_session(cursor, user_id, source_db_id, dest_db_id, description):
    cursor.execute("""
        INSERT INTO sessions (user_id, source_db_id, dest_db_id, description)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (user_id, source_db_id, dest_db_id, description))
    return cursor.fetchone()[0]

def insert_test_query(cursor, name, query_text):
    cursor.execute("""
        INSERT INTO test_queries (name, query_text)
        VALUES (%s, %s)
        ON CONFLICT (name) DO UPDATE SET query_text = EXCLUDED.query_text
        RETURNING id;
    """, (name, query_text))
    return cursor.fetchone()[0]

def insert_query_result(cursor, session_id, test_query_id, db_role, avg_time, success, error=None):
    cursor.execute("""
        INSERT INTO query_results (session_id, test_query_id, db_role, execution_time_ms, success, error_message)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (session_id, test_query_id, db_role, avg_time, success, error))
    return cursor.fetchone()[0]

def insert_query_run(cursor, query_result_id, run_number, exec_time, success, error=None):
    cursor.execute("""
        INSERT INTO query_runs (query_result_id, run_number, execution_time_ms, success, error_message)
        VALUES (%s, %s, %s, %s, %s);
    """, (query_result_id, run_number, exec_time, success, error))

# === Benchmarking ===
def connect_to_databases():
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cursor = pg_conn.cursor()

    pg_cursor.execute("SET search_path TO sakila;")

    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor()
    return pg_conn, pg_cursor, mysql_conn, mysql_cursor

def run_benchmark_with_supabase(
    db_cursor, db_label, conn,
    supabase_cursor, session_id,
    db_role, queries_dict
):
    print(f"\n🚀 Benchmarking: {db_label} ({db_role})")
    for query_name, query_text in queries_dict.items():
        print(f"▶️ {query_name}")
        test_query_id = insert_test_query(supabase_cursor, query_name, query_text)
        run_times, success, error_msg = [], True, None

        for i in range(100):
            try:
                start = time.time()
                db_cursor.execute(query_text)
                _ = db_cursor.fetchall()
                duration = (time.time() - start) * 1000
                run_times.append(duration)
            except Exception as e:
                conn.rollback()
                success = False
                error_msg = str(e)
                break

        avg_time = sum(run_times) / len(run_times) if run_times else None
        result_id = insert_query_result(
            supabase_cursor, session_id, test_query_id,
            db_role, avg_time, success, error_msg
        )

        if success:
            for i, t in enumerate(run_times):
                insert_query_run(supabase_cursor, result_id, i, t, True)
        else:
            insert_query_run(supabase_cursor, result_id, 0, 0.0, False, error_msg)

        print(f"{'✅' if success else '❌'} {query_name} | Avg: {avg_time:.2f} ms" if success else f"❌ Failed: {error_msg}")

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="Run DB benchmark and upload to Supabase.")
    parser.add_argument("--user-id", required=True, help="Your Supabase user UUID")
    parser.add_argument("--desc", default="Sakila benchmark run", help="Session description")
    args = parser.parse_args()

    supa_conn = connect_to_supabase()
    supa_cursor = supa_conn.cursor()
    pg_conn, pg_cursor, mysql_conn, mysql_cursor = connect_to_databases()

    source_db_id = insert_database(supa_cursor, args.user_id, 'MySQL', MYSQL_CONFIG["host"], MYSQL_CONFIG["port"], '8.0')
    dest_db_id = insert_database(supa_cursor, args.user_id, 'PostgreSQL', PG_CONFIG["host"], PG_CONFIG["port"], '15')
    session_id = insert_session(supa_cursor, args.user_id, source_db_id, dest_db_id, args.desc)

    run_benchmark_with_supabase(pg_cursor, "PostgreSQL", pg_conn, supa_cursor, session_id, "destination", queries)
    run_benchmark_with_supabase(mysql_cursor, "MySQL", mysql_conn, supa_cursor, session_id, "source", queries)

    supa_conn.commit()
    supa_cursor.close()
    supa_conn.close()
    pg_cursor.close()
    pg_conn.close()
    mysql_cursor.close()
    mysql_conn.close()
    print("\n✅ Benchmark session uploaded to Supabase!")

# Entry point
if __name__ == "__main__":
    main()

