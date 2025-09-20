import logging
from functools import wraps
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
from app.db.models import Base


if os.name == "nt":
    DB_DIR = Path("data")
else:
    DB_DIR = Path.home() / ".local" / "share" / "HADSA"

DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "HADSA.db"
DB_URI = f"sqlite+aiosqlite:///{DB_PATH}"

engine = create_async_engine(DB_URI, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


def connection(commit: bool = True):
    def decorator(method):
        @wraps(method)
        async def wrapper(*args, **kwargs):
            async with async_session_maker() as session:
                try:
                    kwargs["session"] = session
                    result = await method(*args, **kwargs)
                    if commit:
                        await session.commit()
                    return result
                except Exception as e:
                    logging.error(e)
                    await session.rollback()
                finally:
                    await session.close()
        return wrapper
    return decorator


async def init_db():
    from app.storage import BASE_PATH

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    os.makedirs(BASE_PATH, exist_ok=True)
