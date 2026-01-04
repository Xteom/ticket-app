from pathlib import Path
from src.db.db import connect, init_db


def main():
    db_path = Path("./data/app.db")
    conn = connect(db_path)
    schema_sql = Path("./src/db/schema.sql").read_text(encoding="utf-8")
    init_db(conn, schema_sql)
    print("DB initialized at", db_path)


if __name__ == "__main__":
    main()
