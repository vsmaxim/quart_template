"""Database management related functionality."""
from returns.pipeline import flow
from returns.result import safe

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from yet_another_flask_template.config import Config


@safe
def create_engine(config: Config) -> AsyncEngine:
    return flow(
        config.db_url(),
        create_async_engine,
    )


