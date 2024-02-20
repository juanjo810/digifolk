import pathlib
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.orm import configure_mappers

sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))


from app.core.config import DATABASE_URL  # isort:skip

print('DB path: ' + str(DATABASE_URL))

config = context.config

fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", str(DATABASE_URL))

from app.models.base import Base

# Each Model Has To Be Here
#from app.models.gen_model import GenModel
from app.models.piece import Piece
from app.models.user import User
from app.models.collection import PieceCol
from app.models.items import ListItem

target_metadata = Base.metadata

configure_mappers()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            compare_type=True,
            #process_revision_directives=process_revision_directives,
            render_as_batch=True)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()