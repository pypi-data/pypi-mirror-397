# Publicar robin-logs en PyPI

## Requisitos Previos

1. Cuenta en PyPI: https://pypi.org/account/register/
2. Cuenta en TestPyPI (opcional): https://test.pypi.org/account/register/

## Paso 1: Instalar herramientas de build

```bash
pip install build twine
```

## Paso 2: Construir el paquete

```bash
# Limpiar builds anteriores (si existen)
rm -rf dist/ build/ *.egg-info

# Construir el paquete
python -m build
```

Esto creará:
- `dist/robin-logs-0.1.0.tar.gz` (código fuente)
- `dist/robin_logs-0.1.0-py3-none-any.whl` (wheel)

## Paso 3: Probar en TestPyPI (Opcional pero recomendado)

### 3.1 Configurar API token para TestPyPI

1. Ve a https://test.pypi.org/manage/account/token/
2. Crea un nuevo token con scope "Entire account"
3. Guarda el token (solo lo verás una vez)

### 3.2 Subir a TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

Username: `__token__`
Password: `pypi-...` (tu token de TestPyPI)

### 3.3 Probar instalación desde TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ robin-logs
```

## Paso 4: Publicar en PyPI (Producción)

### 4.1 Configurar API token para PyPI

1. Ve a https://pypi.org/manage/account/token/
2. Crea un nuevo token con scope "Entire account"
3. Guarda el token

### 4.2 Subir a PyPI

```bash
python -m twine upload dist/*
```

Username: `__token__`
Password: `pypi-...` (tu token de PyPI)

## Paso 5: Verificar

```bash
# Instalar desde PyPI
pip install robin-logs

# Verificar versión
python -c "import robin_logs; print(robin_logs.__version__)"
```

## Actualizar Versión

Para publicar una nueva versión:

1. Actualiza la versión en:
   - `setup.py` (línea `version="0.1.1"`)
   - `pyproject.toml` (línea `version = "0.1.1"`)
   - `robin_logs/__init__.py` (línea `__version__ = "0.1.1"`)

2. Reconstruye y publica:
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   python -m twine upload dist/*
   ```

## Configurar pypirc (Opcional)

Para evitar escribir credenciales cada vez:

```bash
# Crear archivo ~/.pypirc
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-your-token-here

[testpypi]
username = __token__
password = pypi-your-testpypi-token-here
EOF

chmod 600 ~/.pypirc
```

Luego solo necesitas:
```bash
python -m twine upload dist/*
```

## Verificar antes de publicar

```bash
# Verificar contenido del paquete
tar tzf dist/robin-logs-0.1.0.tar.gz

# Verificar metadata
python -m twine check dist/*
```

## Comandos Rápidos

```bash
# Build + Upload a TestPyPI
rm -rf dist/ build/ *.egg-info && python -m build && python -m twine upload --repository testpypi dist/*

# Build + Upload a PyPI
rm -rf dist/ build/ *.egg-info && python -m build && python -m twine upload dist/*
```

## Notas

- La primera vez que publiques, necesitarás crear el proyecto en PyPI
- El nombre `robin-logs` debe estar disponible en PyPI
- Si el nombre está tomado, considera: `robin-logging`, `robin-logger`, `robinlogs`
- Puedes verificar disponibilidad en: https://pypi.org/project/robin-logs/
