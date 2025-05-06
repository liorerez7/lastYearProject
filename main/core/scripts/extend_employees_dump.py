import re, os, random, csv, io

# ------------------------ CONFIG ------------------------
EXT_RATIO   = 1       # +25 %
RNG_SEED    = 42
CHUNK_SIZE  = 700
# --------------------------------------------------------

base_dir  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
src       = os.path.join(base_dir, "employees-data.sql")
dest      = os.path.join(base_dir, "employees-data-extra-chunked-full.sql")

insert_re = re.compile(r"INSERT INTO `(\w+)` VALUES\s*(\(.*?\));", re.S)

# ---------- helpers ----------
def rows_from_block(block: str):
    body  = block[1:-2]                 # drop '('  … ');
    csv_s = body.replace("),(", "\n")
    return [r for r in csv.reader(io.StringIO(csv_s))]

def clean(v: str) -> str:
    v = v.strip()
    return v[1:-1] if v.startswith("'") and v.endswith("'") else v

def quote(v: str) -> str:
    return v if v.isdigit() else "'" + v.replace("'", "''") + "'"

def to_tuple(row):
    return "(" + ",".join(quote(clean(c)) for c in row) + ")"

# ---------- read ----------
with open(src, encoding="utf-8", errors="ignore") as f:
    dump = f.read()

tables = {}
for tbl, block in insert_re.findall(dump):
    tables.setdefault(tbl, []).extend(rows_from_block(block))

employees = tables["employees"]
random.seed(RNG_SEED)
extra_n   = int(len(employees) * EXT_RATIO)
sampled   = random.sample(employees, extra_n)

max_emp = max(int(r[0]) for r in employees)
emp_map, new_emp = {}, []
for i, row in enumerate(sampled, 1):
    new_no = str(max_emp + i)
    emp_map[row[0]] = new_no
    new_emp.append([new_no] + row[1:])

related = ["salaries", "titles", "dept_emp", "dept_manager"]
new_rows = {t: [] for t in related}
for t in related:
    for row in tables[t]:
        if row[0] in emp_map:
            new_rows[t].append([emp_map[row[0]]] + row[1:])

# ---------- write (chunked) ----------
with open(dest, "w", encoding="utf-8") as f:
    f.write("-- CHUNKED +25% (500 rows per INSERT; syntax‑safe)\n\n")

    def write_chunked(table, rows):
        if not rows: return
        f.write(f"LOCK TABLES `{table}` WRITE;\n")
        for i in range(0, len(rows), CHUNK_SIZE):
            chunk = rows[i:i+CHUNK_SIZE]
            f.write(f"INSERT INTO `{table}` VALUES\n")
            f.write(",\n".join(to_tuple(r) for r in chunk))
            f.write(";\n")
        f.write("UNLOCK TABLES;\n\n")

    write_chunked("employees", new_emp)
    for t in related:
        write_chunked(t, new_rows[t])

print(f"✅  wrote {extra_n} rows in chunks → {dest}")
