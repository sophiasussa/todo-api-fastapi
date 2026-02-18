from sqlalchemy.orm import declarative_base

#: SQLAlchemy declarative base.
#:
#: All ORM model classes in the project must inherit from this base.
#: This object is used by Alembic to automatically discover
#: table metadata during migration generation and execution.
Base = declarative_base()

# IMPORT ALL MODELS HERE
# -------------------------------------------------
# These imports are intentional.
# They ensure that all models are registered
# in the Base metadata, allowing Alembic
# to correctly detect tables and schema changes.
from app.models import task
