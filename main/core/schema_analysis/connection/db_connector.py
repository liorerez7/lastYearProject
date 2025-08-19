from typing import Optional, Dict, Tuple
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from main.config.db_config import POSTGRES_CONFIG, MYSQL_CONFIG


class DBConnector:
    def __init__(self, db_type: str, db_url: Optional[str] = None, config: Optional[Dict] = None):
        self.db_type = db_type.lower()
        self.db_url = db_url
        self.config = config or self._get_default_config()
        self.engine: Optional[Engine] = None
        self.metadata: MetaData = MetaData()

    def _get_default_config(self) -> Dict:
        if self.db_type == "mysql":
            return MYSQL_CONFIG
        elif self.db_type == "postgres":
            return POSTGRES_CONFIG
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")

    def build_db_url(self) -> str:
        if self.db_url:
            return self.db_url
        cfg = self.config
        if self.db_type == "mysql":
            return f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"
        elif self.db_type == "postgres":
            # שים לב: אנחנו מתחברים ל-DB בשם mydb2 (cfg['dbname'])
            return f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
        else:
            raise ValueError("Unsupported db type")

    def test_connection(self) -> bool:
        try:
            engine = create_engine(self.build_db_url(), pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except OperationalError as e:
            print(f"❌ Connection failed: {e}")
            return False

    def connect(self, schema: Optional[str] = None) -> Tuple[Engine, MetaData]:
        """
        MySQL: schema == database name (mydb)
        Postgres: connect to database (mydb2) and set search_path to the given schema (e.g., mydb).
        Reflect explicitly against that schema.
        """
        db_url = self.build_db_url()

        if self.db_type == "postgres":
            # קובע search_path כבר בשכבת ה-connection, כדי שכל הרפלקציה/שאילתות יראו את הסכמה
            search_path = f"{schema},public" if schema else "public"
            self.engine = create_engine(
                db_url,
                pool_pre_ping=True,
                connect_args={"options": f"-csearch_path={search_path}"}
            )
            # דיאגנוסטיקה – נראה בדיוק איפה אנחנו ומה רואים
            with self.engine.connect() as conn:
                curr_db = conn.execute(text("SELECT current_database()")).scalar()
                sp = conn.execute(text("SHOW search_path")).scalar()
                curr_schema = conn.execute(text("SELECT current_schema()")).scalar()
                print(f"[PG] current_database={curr_db}, current_schema={curr_schema}, search_path={sp}")

                rows = conn.execute(text("""
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_schema = :s
                    ORDER BY 1,2
                """), {"s": schema or "public"}).fetchall()
                print(f"[PG] tables in schema '{schema or 'public'}': {[f'{r[0]}.{r[1]}' for r in rows]}")

            # חשוב: להשתמש באובייקט MetaData נקי לכל חיבור/שיקוף
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine, schema=schema)

        elif self.db_type == "mysql":
            self.engine = create_engine(db_url, pool_pre_ping=True)
            self.metadata = MetaData()
            # ב-MySQL 'schema' הוא שם ה-DB (mydb)
            self.metadata.reflect(bind=self.engine, schema=schema)

        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")

        return self.engine, self.metadata

    def get_engine(self) -> Engine:
        if not self.engine:
            raise RuntimeError("Engine not initialized. Call connect() first.")
        return self.engine

    def get_metadata(self) -> MetaData:
        if not self.metadata.tables:
            raise RuntimeError("Metadata not loaded. Call connect() first.")
        return self.metadata
