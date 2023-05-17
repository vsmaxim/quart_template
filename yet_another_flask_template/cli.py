from alembic.config import Config as AlembicConfig
import click


def make_alembic_config() -> AlembicConfig:
    alembic_cfg = AlembicConfig()
    alembic_cfg.set_main_option("script_location", "app:module") # Uses app/module.py
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlalchemy-url")
    alembic_cfg.set_main_option("version_table_schema", "public")
    return alembic_cfg


@click.group()
def cli():
    pass

