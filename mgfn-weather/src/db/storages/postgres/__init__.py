"""PostgreSQL storage. Contains it's settings and logic."""

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.config import settings


engine = create_async_engine(settings.DATABASE_URL.unicode_string())
# engine.echo = True
async_session = async_sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
    expire_on_commit=False,
)


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_`%(constraint_name)s`",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=naming_convention)
Base: DeclarativeBase = declarative_base(metadata=metadata)
