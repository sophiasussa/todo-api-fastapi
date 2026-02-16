from sqlalchemy.orm import declarative_base

Base = declarative_base()

# IMPORTA TODOS OS MODELS AQUI
from app.models import task
