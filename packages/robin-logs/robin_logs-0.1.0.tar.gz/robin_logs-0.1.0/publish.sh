#!/bin/bash
# Script para publicar robin-logs en PyPI

echo "🚀 Publicando robin-logs en PyPI"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "setup.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio robin-local-logs"
    exit 1
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf dist/ build/ *.egg-info
echo "✓ Limpieza completada"
echo ""

# Construir el paquete
echo "📦 Construyendo paquete..."
python -m build
if [ $? -ne 0 ]; then
    echo "❌ Error al construir el paquete"
    exit 1
fi
echo "✓ Paquete construido exitosamente"
echo ""

# Verificar el paquete
echo "🔍 Verificando paquete..."
python -m twine check dist/*
if [ $? -ne 0 ]; then
    echo "❌ Error en la verificación del paquete"
    exit 1
fi
echo "✓ Paquete verificado"
echo ""

# Preguntar si publicar en TestPyPI o PyPI
echo "¿Dónde quieres publicar?"
echo "1) TestPyPI (pruebas)"
echo "2) PyPI (producción)"
read -p "Selecciona (1 o 2): " choice

case $choice in
    1)
        echo ""
        echo "📤 Publicando en TestPyPI..."
        python -m twine upload --repository testpypi dist/*
        ;;
    2)
        echo ""
        echo "⚠️  ¡Vas a publicar en PyPI PRODUCCIÓN!"
        read -p "¿Estás seguro? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "📤 Publicando en PyPI..."
            python -m twine upload dist/*
        else
            echo "❌ Publicación cancelada"
            exit 0
        fi
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════"
    echo "✅ ¡Publicación exitosa!"
    echo "════════════════════════════════════════════"
    echo ""
    echo "🎉 robin-logs está ahora disponible en PyPI"
    echo ""
    echo "Para instalar:"
    echo "  pip install robin-logs"
    echo ""
else
    echo ""
    echo "❌ Error en la publicación"
    exit 1
fi
