from sqlalchemy import select
from app.db.engine import connection
from app.db.models import File


@connection()
async def add(new_file: File, session):
    session.add(new_file)
    await session.flush()
    return new_file


@connection(commit=False)
async def get_all(session):
    result = await session.execute(select(File))
    documents = result.scalars().all()
    return documents


@connection(commit=False)
async def is_unique(_hash: str, session):
    result = await session.execute(select(File).filter_by(hash=_hash))
    document = result.scalars().first()
    return document
