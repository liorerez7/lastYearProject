import re
import os
import random

# ------------------------------------
# תצורה
# ------------------------------------
EXT_RATIO = 0.25   # מוסיפים +25 %
RNG_SEED  = 42     # לשחזור

# ------------------------------------
# נתיבים (יחסית למיקום הקובץ)
# ------------------------------------
base_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
original_path = os.path.join(base_dir, "employees-data.sql")
output_path   = os.path.join(base_dir, "employees-data-extra-fixed.sql")

# ------------------------------------
# קריאת ה‑dump המקורי
# ------------------------------------
insert_re = re.compile(r"INSERT INTO `(\w+)` VALUES\s*(\(.*?\));", re.S)

with open(original_path, "r", encoding="utf-8", errors="ignore") as f:
    dump = f.read()

tables = {}
for tbl, values_block in insert_re.findall(dump):
    rows_str = values_block[1:-2]                      # בלי '(' ו‑');
    rows = ['(' + r + ')' for r in re.split(r"\),\s*\(", rows_str)]
    tables.setdefault(tbl, []).extend(rows)

employees_rows = tables["employees"]
random.seed(RNG_SEED)
extra_n = int(len(employees_rows) * EXT_RATIO)
sampled = random.sample(employees_rows, extra_n)

# ------------------------------------
# בניית מזהים חדשים ומיפוי
# ------------------------------------
def first_val(row: str) -> str:
    return row[1:row.find(',')]

max_emp = max(int(first_val(r)) for r in employees_rows)
emp_map, new_emp_rows = {}, []

for i, row in enumerate(sampled, start=1):
    new_no = max_emp + i
    old_no = first_val(row)
    emp_map[old_no] = str(new_no)
    new_emp_rows.append('(' + str(new_no) + row[row.find(','):])

# ------------------------------------
# טבלאות תלויות
# ------------------------------------
related = ["salaries", "titles", "dept_emp", "dept_manager"]
new_rows = {t: [] for t in related}

for tbl in related:
    for row in tables.get(tbl, []):
        old_no = first_val(row)
        if old_no in emp_map:
            new_rows[tbl].append('(' + emp_map[old_no] + row[row.find(','):])

# ------------------------------------
# כתיבה לקובץ חדש
# ------------------------------------
with open(output_path, "w", encoding="utf-8") as out:
    out.write("-- GENERATED – adds {:.0%} employees\n\n".format(EXT_RATIO))

    def write_block(table, rows):
        if not rows:
            return
        out.write(f"LOCK TABLES `{table}` WRITE;\n")
        out.write(f"INSERT INTO `{table}` VALUES\n")
        out.write(",\n".join(rows))
        out.write(";\nUNLOCK TABLES;\n\n")

    write_block("employees", new_emp_rows)
    for t in related:
        write_block(t, new_rows[t])

print(f"✅  {extra_n} extra employees written to: {output_path}")
