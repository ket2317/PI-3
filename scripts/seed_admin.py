import os
import bcrypt
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import engine
from app.models.user import User, Role
from app.models import branch, category, product, inventory

load_dotenv()

ADMIN_NAME = os.getenv("ADMIN_NAME")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


def crear_admin():
    if not ADMIN_NAME or not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise ValueError("Faltan las variables del administrador en el .env")

    with Session(engine) as db:
        rol_admin = db.query(Role).filter(Role.nombre == "ADMIN").first()

        if not rol_admin:
            raise ValueError("El rol ADMIN no existe. Ejecuta primero las migraciones de Alembic.")
            #rol_admin = Role(nombre="ADMIN")
            #db.add(rol_admin)
            #db.flush()

        admin_existente = db.query(User).filter(
            User.correo == ADMIN_EMAIL
        ).first()

        if admin_existente:
            print("El administrador ya existe")
            return

        password_hash = bcrypt.hashpw(
            ADMIN_PASSWORD.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        admin = User(
            nombre=ADMIN_NAME,
            correo=ADMIN_EMAIL,
            password_hash=password_hash,
            rol_id=rol_admin.id,
            sucursal_id=None,
            activo=True
        )

        db.add(admin)
        db.commit()

        print("Administrador creado correctamente")


if __name__ == "__main__":
    crear_admin()