#!/bin/bash
# Genera un archivo .html desde un .md usando Marp CLI con la configuración local.
# Uso: ./build.sh archivo.md

if [ $# -eq 0 ]; then
    echo "Uso: $0 <archivo.md>"
    exit 1
fi

MD="$1"
HTML="${MD%.md}.html"

npx @marp-team/marp-cli "$MD" --config marp.config.js -o "$HTML"
