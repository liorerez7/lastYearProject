# transform_mysql8_to_mysql57.py
import os, re, sys, pathlib

base_dir = pathlib.Path(__file__).resolve().parents[2]   # .../LastYearProject
data_dir = base_dir / "data"

FILES = [
    ("employee-schema-extended.sql", "employee-schema-extended-fixed.sql"),
    ("employee-data-extended.sql",   "employee-data-extended-fixed.sql"),
]

def fix(text: str, is_schema: bool) -> str:
    # 1) collation
    text = re.sub(r"utf8mb4_0900_ai_ci", "utf8mb4_general_ci", text)
    # 2) תאריך אפס  →  '1970-01-01'
    if not is_schema:
        text = text.replace("'0000-00-00'", "'1970-01-01'")
    return text

for in_name, out_name in FILES:
    src = data_dir / in_name
    dst = data_dir / out_name
    with open(src, encoding="utf-8") as f:
        content = f.read()
    fixed = fix(content, "schema" in in_name)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(fixed)
    print("✅ wrote", dst)

