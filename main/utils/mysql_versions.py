import re


def downgrade_mysql_8_to_5_7(sql_text: str) -> str:
    """
    Downgrades a MySQL 8.0 SQL schema to 5.7 compatible syntax.
    """

    # 1. Fix utf8mb4 collations
    sql_text = re.sub(
        r"utf8mb4_0900_ai_ci",
        "utf8mb4_general_ci",
        sql_text,
        flags=re.IGNORECASE
    )

    # 2. Remove CHECK constraints
    sql_text = re.sub(
        r"\s*CHECK\s*\(.*?\),?",  # Remove CHECK constraints inside CREATE TABLE
        "",
        sql_text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # 3. Replace JSON columns with LONGTEXT (approximation)
    sql_text = re.sub(
        r"\bJSON\b",
        "LONGTEXT",
        sql_text,
        flags=re.IGNORECASE
    )

    # 4. Remove invisible indexes (not supported in 5.7)
    sql_text = re.sub(
        r"\s+VISIBLE",
        "",
        sql_text,
        flags=re.IGNORECASE
    )

    # 5. Optional: fix DEFAULT expressions with functions not supported
    # Example: DEFAULT (CURRENT_TIMESTAMP()) → DEFAULT CURRENT_TIMESTAMP
    sql_text = re.sub(
        r"DEFAULT\s*\(\s*(CURRENT_TIMESTAMP|NOW)\s*\)",
        r"DEFAULT \1",
        sql_text,
        flags=re.IGNORECASE
    )

    return sql_text
