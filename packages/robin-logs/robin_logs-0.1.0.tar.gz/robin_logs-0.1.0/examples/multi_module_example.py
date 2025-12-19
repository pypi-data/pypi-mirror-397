"""
Ejemplo de integración con múltiples módulos (WhatsApp, Instagram, Email)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from robin_logs import setup_logging, register_log_routes, get_logger, LogConfig
from typing import Optional
import random

# Crear aplicación
app = FastAPI(title="Robin Logs - Multi-Módulo")

# Configurar logs
config = LogConfig(
    log_directory="./logs",
    retention_hours=72,
    enable_api=True,
    api_prefix="/api/logs"
)

setup_logging(config)
register_log_routes(app, config)

# Loggers para cada módulo
whatsapp_logger = get_logger("whatsapp")
instagram_logger = get_logger("instagram")
email_logger = get_logger("email")


# Modelos
class WhatsAppMessage(BaseModel):
    phone: str
    message: str

class InstagramPost(BaseModel):
    username: str
    caption: str
    image_url: str

class Email(BaseModel):
    to: str
    subject: str
    body: str


# Endpoints de WhatsApp
@app.post("/whatsapp/send")
async def send_whatsapp(msg: WhatsAppMessage):
    """Enviar mensaje de WhatsApp"""
    whatsapp_logger.info("Iniciando envío de WhatsApp", extra={
        "phone": msg.phone,
        "message_length": len(msg.message)
    })
    
    # Simular envío
    success = random.choice([True, True, True, False])  # 75% éxito
    
    if success:
        whatsapp_logger.info("Mensaje de WhatsApp enviado", extra={
            "phone": msg.phone,
            "message_id": f"wa_{random.randint(1000, 9999)}",
            "status": "delivered"
        })
        return {"status": "sent", "phone": msg.phone}
    else:
        whatsapp_logger.error("Error al enviar WhatsApp", extra={
            "phone": msg.phone,
            "error_code": "TIMEOUT",
            "retry_count": 1
        })
        raise HTTPException(status_code=500, detail="Error al enviar mensaje")


# Endpoints de Instagram
@app.post("/instagram/post")
async def create_instagram_post(post: InstagramPost):
    """Crear post en Instagram"""
    instagram_logger.info("Creando post de Instagram", extra={
        "username": post.username,
        "caption_length": len(post.caption)
    })
    
    success = random.choice([True, True, True, False])
    
    if success:
        instagram_logger.info("Post de Instagram creado", extra={
            "username": post.username,
            "post_id": f"ig_{random.randint(1000, 9999)}",
            "likes": 0
        })
        return {"status": "posted", "username": post.username}
    else:
        instagram_logger.error("Error al crear post de Instagram", extra={
            "username": post.username,
            "error": "API rate limit exceeded"
        })
        raise HTTPException(status_code=429, detail="Rate limit excedido")


# Endpoints de Email
@app.post("/email/send")
async def send_email(email: Email):
    """Enviar email"""
    email_logger.info("Enviando email", extra={
        "to": email.to,
        "subject": email.subject
    })
    
    success = random.choice([True, True, True, False])
    
    if success:
        email_logger.info("Email enviado exitosamente", extra={
            "to": email.to,
            "message_id": f"email_{random.randint(1000, 9999)}"
        })
        return {"status": "sent", "to": email.to}
    else:
        email_logger.error("Error al enviar email", extra={
            "to": email.to,
            "error": "SMTP connection failed"
        })
        raise HTTPException(status_code=500, detail="Error SMTP")


# Endpoint de estadísticas
@app.get("/stats")
async def get_stats():
    """Obtener estadísticas de uso"""
    return {
        "message": "Ver logs de cada módulo",
        "endpoints": {
            "whatsapp": "/api/logs/whatsapp",
            "instagram": "/api/logs/instagram",
            "email": "/api/logs/email",
            "all": "/api/logs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
