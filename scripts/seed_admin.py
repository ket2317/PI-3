import os
import bcrypt
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import engine
from app.models.user import User, Role
from app.models import branch, category, product, inventory

load_dotenv()

ADMIN_NOMBRE = os.getenv("ADMIN_NOMBRE")
ADMIN_CORREO = os.getenv("ADMIN_CORREO")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


def crear_admin():
    if not ADMIN_NOMBRE or not ADMIN_CORREO or not ADMIN_PASSWORD:
        raise ValueError("Faltan las variables del administrador en el .env")

    with Session(engine) as db:
        rol_admin = db.query(Role).filter(Role.nombre == "ADMIN").first()

        if not rol_admin:
            rol_admin = Role(nombre="ADMIN")
            db.add(rol_admin)
            db.flush()

        admin_existente = db.query(User).filter(
            User.correo == ADMIN_CORREO
        ).first()

        if admin_existente:
            print("El administrador ya existe")
            return

        password_hash = bcrypt.hashpw(
            ADMIN_PASSWORD.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        admin = User(
            nombre=ADMIN_NOMBRE,
            correo=ADMIN_CORREO,
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