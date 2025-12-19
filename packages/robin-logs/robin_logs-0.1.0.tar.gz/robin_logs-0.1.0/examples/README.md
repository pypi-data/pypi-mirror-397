# Ejemplos de Robin Logs

Esta carpeta contiene ejemplos de integración de `robin-logs` con FastAPI.

## Ejemplos Disponibles

### 1. `basic_example.py` - Integración Básica

Ejemplo simple que muestra la configuración mínima:

```bash
cd examples
python basic_example.py
```

Luego visita:
- http://localhost:8000 - Endpoint principal
- http://localhost:8000/test-log - Generar log de prueba
- http://localhost:8000/logs - Ver todos los logs
- http://localhost:8000/docs - Documentación interactiva

### 2. `multi_module_example.py` - Múltiples Módulos

Demuestra cómo usar diferentes módulos (WhatsApp, Instagram, Email):

```bash
python multi_module_example.py
```

APIs disponibles:
- POST /whatsapp/send - Enviar mensaje de WhatsApp
- POST /instagram/post - Crear post de Instagram
- POST /email/send - Enviar email
- GET /api/logs/whatsapp - Ver logs de WhatsApp
- GET /api/logs/instagram - Ver logs de Instagram
- GET /api/logs/email - Ver logs de Email

### 3. `secure_example.py` - Con Autenticación

Muestra cómo proteger los endpoints de logs:

```bash
python secure_example.py
```

**Credenciales de prueba:**
- Para endpoints propios: `Authorization: Bearer mi-token-de-prueba`
- Para endpoints de logs: `X-API-Key: mi-super-clave-secreta-123`

Ejemplo de uso:
```bash
# Consultar logs (requiere API Key)
curl -H "X-API-Key: mi-super-clave-secreta-123" \
     http://localhost:8000/api/logs

# Acceder a endpoint protegido
curl -H "Authorization: Bearer mi-token-de-prueba" \
     http://localhost:8000/protected
```

### 4. `middleware_example.py` - Logging Automático

Demuestra cómo registrar automáticamente todas las peticiones HTTP:

```bash
python middleware_example.py
```

Cada petición HTTP se registra automáticamente con:
- Método y ruta
- IP del cliente
- User-Agent
- Código de respuesta
- Duración en milisegundos

Ver logs: http://localhost:8000/logs/requests

## Instalar Dependencias

```bash
# Desde la raíz del proyecto
pip install -e .

# O instalar dependencias manualmente
pip install fastapi uvicorn python-json-logger
```

## Probar los Ejemplos

### Opción 1: Ejecutar directamente

```bash
cd examples
python basic_example.py
```

### Opción 2: Con uvicorn

```bash
uvicorn basic_example:app --reload
```

## Consultar Logs

Todos los ejemplos exponen endpoints para consultar logs. Ejemplos:

```bash
# Todos los logs
GET http://localhost:8000/logs

# Logs de un módulo
GET http://localhost:8000/logs/whatsapp

# Filtrar por nivel
GET http://localhost:8000/logs?level=ERROR

# Últimas 2 horas
GET http://localhost:8000/logs?last=2h

# Rango específico
GET http://localhost:8000/logs?from=2025-12-17T00:00:00&to=2025-12-17T23:59:59

# Combinar filtros
GET http://localhost:8000/logs/whatsapp?level=ERROR&last=1h&limit=50
```

## Generar Logs de Prueba

Usa los endpoints de cada ejemplo para generar logs:

```bash
# Ejemplo básico
curl http://localhost:8000/test-log
curl http://localhost:8000/test-error

# Multi-módulo
curl -X POST http://localhost:8000/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "+573001234567", "message": "Hola mundo"}'

# Con middleware
curl http://localhost:8000/users/123
curl http://localhost:8000/slow
```

## Ver Archivos de Logs

Los logs se guardan en `./logs/`:

```bash
# Ver estructura
ls -lh logs/

# Leer un archivo de log
cat logs/whatsapp.log | jq .

# Ver últimas líneas
tail -f logs/api.log | jq .
```

## Troubleshooting

### Error: "Sistema de logs no inicializado"

Asegúrate de llamar `setup_logging(config)` antes de `register_log_routes()`.

### Logs no aparecen

Verifica que:
1. El directorio de logs existe y tiene permisos de escritura
2. El nivel de log está correctamente configurado
3. Los logs se están escribiendo (verifica los archivos en `./logs/`)

### API devuelve 401/403

Si usas `require_auth=True`, asegúrate de incluir el header:
```bash
curl -H "X-API-Key: tu-api-key" http://localhost:8000/logs
```
