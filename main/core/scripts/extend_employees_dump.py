import re, os, random, csv, io

EXT_RATIO  = 5          # פי-3 מהגודל המקורי
RNG_SEED   = 42
CHUNK_SIZE = 1000

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
src      = os.path.join(base_dir, "employee-data-extended.sql")
dest     = os.path.join(base_dir, "employees-data-extra-chunked-full.sql")

#insert_re = re.compile(r"INSERT INTO (\w+) VALUES\s*((\(.+?\))(?:,\s*\(.+?\))*)\s*;", re.S)
insert_re = re.compile(
    r"INSERT\s+INTO\s+`?(\w+)`?\s+VALUES\s*((\(.+?\))(?:\s*,\s*\(.+?\))*)\s*;",
    re.S | re.I
)

def rows_from_block(block: str):
    body = block[1:-2]             # מוותר על '('  … ');'
    return list(csv.reader(io.StringIO(body.replace("),(", "\n"))))

def clean(v):  return v[1:-1] if v.startswith("'") and v.endswith("'") else v.strip()
def quote(v):  return v if v.isdigit() else "'" + v.replace("'", "''") + "'"
to_tuple = lambda row: "(" + ",".join(quote(clean(c)) for c in row) + ")"

with open(src, encoding="utf-8", errors="ignore") as f:
    dump = f.read()

tables = {}
for tbl, block, _ in insert_re.findall(dump):
    tables.setdefault(tbl.lower(), []).extend(rows_from_block(block))

print("found tables: ", list(tables))      # עכשיו אמור לכלול 'employees'
employees = tables["employees"]             # לא יזרוק KeyError
random.seed(RNG_SEED)

extra_n   = int(len(employees) * (EXT_RATIO-1))    # כמה *חדשים* נוסיף
sampled   = random.choices(employees, k=extra_n)   # בחירה עם חזרות

max_emp = max(int(r[0]) for r in employees)
emp_map, new_emp = {}, []
for i, row in enumerate(sampled, 1):
    new_no            = str(max_emp + i)
    emp_map[row[0]]   = new_no
    new_emp.append([new_no] + row[1:])

related = ["salaries", "titles", "dept_emp", "dept_manager"]
new_rows = {t: [] for t in related}
for t in related:
    for row in tables[t]:
        if row[0] in emp_map:
            new_rows[t].append([emp_map[row[0]]] + row[1:])

with open(dest, "w", encoding="utf-8") as f:
    f.write("-- EXTRA DATA, chunked\n\n")
    def write_chunked(table, rows):
        if not rows: return
        f.write(f"LOCK TABLES {table} WRITE;\n")
        for i in range(0, len(rows), CHUNK_SIZE):
            f.write(f"INSERT INTO {table} VALUES\n")
            f.write(",\n".join(to_tuple(r) for r in rows[i:i+CHUNK_SIZE]))
            f.write(";\n")
        f.write("UNLOCK TABLES;\n\n")

    write_chunked("employees", new_emp)
    for t in related:
        write_chunked(t, new_rows[t])

print(f"✅  wrote {extra_n:,} extra employees → {dest}")
