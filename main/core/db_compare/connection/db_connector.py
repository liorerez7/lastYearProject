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
        self.metadata = MetaData()

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
            return f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
        else:
            raise ValueError("Unsupported db type")

    def test_connection(self) -> bool:
        try:
            engine = create_engine(self.build_db_url())
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except OperationalError as e:
            print(f"❌ Connection failed: {e}")
            return False

    def connect(self, schema: Optional[str] = None) -> Tuple[Engine, MetaData]:
        self.engine = create_engine(self.build_db_url())
        self.metadata.reflect(bind=self.engine, schema=schema)
        return self.engine, self.metadata

    def get_engine(self) -> Engine:
        if not self.engine:
            raise RuntimeError("Engine not initialized. Call connect() first.")
        return self.engine

    def get_metadata(self) -> MetaData:
        if not self.metadata.tables:
            raise RuntimeError("Metadata not loaded. Call connect() first.")
        return self.metadata
