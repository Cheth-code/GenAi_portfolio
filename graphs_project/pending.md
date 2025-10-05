DB Manager AI — LangGraph Flow (MySQL)

START

⬇️

Node 1 — Read CSV & generate SQL queries (SYSTEM_PROMPT + pandas)

Purpose: Read CSV headers only and craft a SYSTEM_PROMPT that instructs the LLM to produce safe, ordered MySQL CREATE and INSERT statements matching the CSV schema.
Requirements:

Use pandas to read the CSV headers and preserve header order.

Build a SYSTEM_PROMPT that: lists columns in order, requests a CREATE TABLE input_table (...) with sensible MySQL types, requests INSERT statements (or parameterized INSERT), and explicitly whitelists allowed statements (CREATE, INSERT, SELECT).
Output: sql_queries (plain SQL text or a list of statements) → passed to Node 2.

Code snippet (illustrative, no LLM call included):

# Node1: read headers and prepare SYSTEM_PROMPT
import pandas as pd

df = pd.read_csv("input.csv", nrows=0)
columns = list(df.columns)  # preserve header order

sys_prompt = f"""
You are an expert that converts CSV headers to MySQL DDL/DML.
Columns in order: {columns}
- Produce a single CREATE TABLE statement named `input_table` (use sensible MySQL types).
- Produce INSERT statements or parameterized INSERT examples.
- Allowed SQL: CREATE TABLE, INSERT INTO, SELECT. No DROP/ALTER/EXEC.
Return only SQL statements in plain text.
"""
# send sys_prompt to the LLM; receive sql_queries (list or text)


⬇️

Node 2 — Execute queries on MySQL (Docker + VS Code) and retrieve rows

Purpose: Apply the SQL from Node 1 to a MySQL instance running in Docker, then retrieve table rows for Node 3.
Requirements:

Run MySQL in Docker and manage/edit via VS Code.

Validate and sanitize sql_queries against the whitelist before execution.

Execute statements inside transactions; perform a validation pass (e.g., BEGIN; … ROLLBACK;) before committing.
Output: retrieved_rows (tabular data as list of dicts or DataFrame) → passed to Node 3.

Docker (quick start):

docker run --name mysql-local \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=mydb \
  -p 3306:3306 -d mysql:8


Code snippet (safe execution pattern, illustrative):

# Node2: validate & execute SQL, then retrieve rows
from sqlalchemy import create_engine, text

# example connection string (adjust credentials in env in production)
engine = create_engine("mysql+mysqlconnector://root:rootpass@localhost:3306/mydb")

def is_allowed(sql: str) -> bool:
    allowed_prefixes = ("CREATE", "INSERT", "SELECT")
    s = sql.strip().upper()
    return any(s.startswith(p) for p in allowed_prefixes)

def safe_execute(sql_statements):
    # Basic programmatic whitelist validation (extend in prod)
    for sql in sql_statements:
        if not is_allowed(sql):
            raise ValueError("Disallowed SQL statement detected")
    # Execute in a transaction (example)
    with engine.begin() as conn:
        # validation pass: run but rollback in dev if desired
        for sql in sql_statements:
            conn.execute(text(sql))
        rows = conn.execute(text("SELECT * FROM input_table")).mappings().all()
    return rows  # list[dict]


⬇️

Node 3 — Recreate CSV using original headers + retrieved rows (pandas)

Purpose: Using the original CSV headers (and order) plus the retrieved_rows, produce an output.csv that matches the input CSV format exactly.
Requirements:

Preserve original header order and column names.

Fill missing columns consistently and apply type/format conversions as inferred earlier if needed.
Output: output.csv (same header order & format as input).

Code snippet (pandas reindex & export):

# Node3: create output CSV from retrieved rows and original columns
import pandas as pd

# `columns` from Node1, `retrieved_rows` from Node2
df_out = pd.DataFrame(retrieved_rows)

# preserve original header order and names
df_out = df_out.reindex(columns=columns)

# Optional: cast types based on inferred type hints
# e.g., df_out['age'] = df_out['age'].astype('Int64')

df_out.to_csv("output.csv", index=False)


⬇️

END — output.csv produced and validated.