from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def init_db():
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
