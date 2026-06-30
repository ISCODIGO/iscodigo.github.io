#!/bin/bash
# Convierte todos los archivos PPT/PPTX de esta carpeta a Marp Markdown.
# Requiere: python-pptx (instalado en /tmp/pptx_venv)
# Para el formato .PPT antiguo requiere LibreOffice para conversión intermedia.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="/tmp/pptx_venv/bin/python3"
CONVERTER="/tmp/pptx_venv/convert_pptx_to_marp.py"

if [ ! -f "$VENV_PYTHON" ] || [ ! -f "$CONVERTER" ]; then
    echo "Error: El script convert_pptx_to_marp.py no se encuentra."
    echo "Ejecuta primero: python3 -m venv /tmp/pptx_venv && /tmp/pptx_venv/bin/pip install python-pptx"
    exit 1
fi

cd "$SCRIPT_DIR"

for file in *.ppt *.pptx; do
    [ -f "$file" ] || continue
    
    ext="${file##*.}"
    basename_noext="${file%.*}"
    
    if [ "$ext" = "ppt" ]; then
        # Convert old PPT to PPTX first using LibreOffice
        echo "📄 Convirtiendo $file a PPTX (formato antiguo)..."
        if command -v soffice &>/dev/null; then
            soffice --headless --convert-to pptx --outdir "$SCRIPT_DIR" "$file" 2>/dev/null
            if [ -f "${basename_noext}.pptx" ]; then
                echo "   → Convertido a PPTX. Ahora a Marp..."
                "$VENV_PYTHON" "$CONVERTER" "${basename_noext}.pptx"
                rm "${basename_noext}.pptx"  # Clean up intermediate file
            fi
        else
            echo "   ⚠️  LibreOffice no está instalado. Instálalo con: brew install --cask libreoffice"
        fi
    elif [ "$ext" = "pptx" ]; then
        echo "📄 Convirtiendo $file a Marp..."
        "$VENV_PYTHON" "$CONVERTER" "$file"
    fi
done

echo "✅ Conversión completa."
