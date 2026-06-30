#!/bin/bash
# Genera un archivo .html desde un .md usando Marp CLI con la configuración local.
# Uso: ./build.sh archivo.md

if [ $# -eq 0 ]; then
    echo "Uso: $0 <archivo.md>"
    echo ""
    echo "Para construir todos los archivos .md de la carpeta:"
    echo "  for f in *.md; do [ \"\$f\" != \"index.md\" ] && ./build.sh \"\$f\"; done"
    exit 1
fi

MD="$1"
HTML="${MD%.md}.html"

npx @marp-team/marp-cli "$MD" --config marp.config.js -o "$HTML"
