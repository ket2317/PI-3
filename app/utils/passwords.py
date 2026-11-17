import re

from fastapi import HTTPException

REGLAS_PASSWORD = "Mínimo 8 caracteres, con al menos una mayúscula, una minúscula y un número"

# Contraseñas que aparecen primero en cualquier lista de contraseñas filtradas
PASSWORDS_COMUNES = {
    "password", "password1", "password123", "contraseña", "contrasena", "contrasena1",
    "12345678", "123456789", "1234567890", "qwerty123", "qwertyui", "abc12345",
    "abcd1234", "admin123", "administrador", "bienvenido", "bienvenido1", "vendora1",
    "vendora123", "iloveyou", "11111111", "00000000", "asdf1234", "mexico123",
}


def revisar_password(password: str, usuario: str | None = None) -> None:
    """Rechaza contraseñas fáciles. Se usa al crear usuarios y al cambiar o recuperar la contraseña."""
    problema = None

    if len(password) < 8:
        problema = "La contraseña debe tener al menos 8 caracteres"
    elif len(password) > 72:
        # bcrypt solo toma en cuenta los primeros 72 bytes
        problema = "La contraseña no puede tener más de 72 caracteres"
    elif not re.search(r"[a-záéíóúñ]", password):
        problema = "La contraseña debe tener al menos una letra minúscula"
    elif not re.search(r"[A-ZÁÉÍÓÚÑ]", password):
        problema = "La contraseña debe tener al menos una letra mayúscula"
    elif not re.search(r"\d", password):
        problema = "La contraseña debe tener al menos un número"
    elif password.lower() in PASSWORDS_COMUNES:
        problema = "Esa contraseña es demasiado común; elige otra"
    elif re.search(r"(.)\1{3,}", password):
        problema = "La contraseña no puede repetir el mismo carácter 4 veces seguidas"
    elif usuario and len(usuario) >= 3 and usuario.lower() in password.lower():
        problema = "La contraseña no puede contener el nombre de usuario"

    if problema:
        raise HTTPException(status_code=422, detail=problema)
