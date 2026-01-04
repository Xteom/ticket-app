from pathlib import Path
from src.config import load_config
from src.log import setup_logging
from src.db.db import connect, init_db
from src.bot.telegram_bot import build_app


def main() -> None:
    setup_logging()
    cfg = load_config("config.yaml")

    cfg.app.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.app.downloads_dir.mkdir(parents=True, exist_ok=True)

    conn = connect(cfg.app.db_path)

    schema_path = Path(__file__).parent / "db" / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")
    init_db(conn, schema_sql)

    from src.db.repo import Repo
    repo = Repo(conn)

    app = build_app(cfg.telegram.bot_token, repo, cfg.app.downloads_dir)
    app.run_polling(allowed_updates=[])
    # NOTE: allowed_updates=[] means "all"; you can tighten later.


if __name__ == "__main__":
    main()
