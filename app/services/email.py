import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv


load_dotenv()

# Configuración de conexión con Gmail usando variables del .env
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=465,          # Cambiamos al puerto 465
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,    # Desactivamos STARTTLS
    MAIL_SSL_TLS=True,      # Activamos SSL/TLS directo
    USE_CREDENTIALS=True
)



async def enviar_correo_recuperacion(email_destinatario: str, token: str):
    enlace = (
        f"http://127.0.0.1:8000/auth/reset-password"
        f"?token={token}"
    )

    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2 style="color: #7a3038;">VENDORA - Recuperación de Contraseña</h2>
        <p>Has solicitado restablecer tu contraseña.</p>
        <a href="{enlace}"
           style="background-color: #7a3038; color: white;
           padding: 10px 20px; text-decoration: none;
           border-radius: 5px; display: inline-block;">
           Restablecer contraseña
        </a>
        <p>Si no solicitaste esto, puedes ignorar el mensaje.</p>
    </div>
    """

    message = MessageSchema(
        subject="Recupera tu contraseña de Vendora",
        recipients=[email_destinatario],
        body=html,
        subtype=MessageType.html
    )

    print("Intentando enviar correo mediante Gmail SMTP...")

    fm = FastMail(conf)

    # Enviar una sola vez
    await fm.send_message(message)

    print("Correo enviado correctamente.")
