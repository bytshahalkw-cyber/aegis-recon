from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url
        # استخراج مسار الملف من رابط الـ sqlite لتجنب مشاكل الـ string
        if "sqlite+aiosqlite:///" in db_url:
            raw_path = db_url.replace("sqlite+aiosqlite:///", "")
            db_path = Path(raw_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_async_engine(db_url, echo=False)
        self.async_session_maker = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def init(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get_session(self) -> AsyncSession:
        return self.async_session_maker()
