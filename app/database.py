import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Carga las variables guardadas en el archivo .env
load_dotenv()

# Obtiene la URL de PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No se encontró DATABASE_URL en el archivo .env")


# Crea la conexión con PostgreSQL
engine = create_engine(DATABASE_URL)


# Crea sesiones para trabajar con la base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base que utilizaremos para nuestros modelos
Base = declarative_base()


# Abre y cierra una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()