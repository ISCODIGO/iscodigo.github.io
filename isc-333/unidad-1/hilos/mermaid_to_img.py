#!/usr/bin/env python3
"""Convierte bloques mermaid de mos.md a imágenes PNG en img/ y actualiza las referencias."""

import re
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(BASE_DIR, "mos.md")
IMG_DIR = os.path.join(BASE_DIR, "img")
CFG_PATH = os.path.join(BASE_DIR, "mermaid.config.json")

# Nombre de cada diagrama en el orden en que aparecen en el archivo
NAMES = [
    "procesador-texto",
    "servidor-web-arch",
    "servidor-web-workers",
    "recursos-proceso-hilo",
    "estados-hilo",
    "hilos-user-space",
    "hilos-kernel",
    "hilos-hibrido",
    "popup-threads",
    "resumen-mindmap",
]

MERMAID_CONFIG = """{
  "theme": "base",
  "themeVariables": {
    "background": "#ffffff",
    "mainBkg": "#e8f0fe",
    "nodeBorder": "#0055b3",
    "clusterBkg": "#f0f4ff",
    "titleColor": "#0055b3",
    "edgeLabelBackground": "#ffffff",
    "lineColor": "#0055b3",
    "primaryColor": "#e8f0fe",
    "primaryBorderColor": "#0055b3",
    "primaryTextColor": "#1e1e2e",
    "secondaryColor": "#f4f6f8",
    "fontFamily": "Segoe UI, Arial, sans-serif"
  }
}
"""

def main():
    os.makedirs(IMG_DIR, exist_ok=True)

    # Escribir config de mermaid
    with open(CFG_PATH, "w") as f:
        f.write(MERMAID_CONFIG)

    with open(MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
    matches = list(pattern.finditer(content))
    print(f"Bloques mermaid encontrados: {len(matches)}")

    errors = []
    for i, match in enumerate(matches):
        name = NAMES[i] if i < len(NAMES) else f"diagram-{i+1}"
        mmd_file = os.path.join(IMG_DIR, f"{name}.mmd")
        png_file = os.path.join(IMG_DIR, f"{name}.png")

        with open(mmd_file, "w", encoding="utf-8") as f:
            f.write(match.group(1))

        print(f"  Renderizando {name}.png ...", end=" ", flush=True)
        result = subprocess.run(
            [
                "npx", "--yes", "@mermaid-js/mermaid-cli",
                "-i", mmd_file,
                "-o", png_file,
                "-c", CFG_PATH,
                "-b", "white",
                "--width", "1200",
                "--height", "800",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓")
        else:
            print("✗")
            errors.append((name, result.stderr.strip()))

    if errors:
        print("\nErrores:")
        for name, msg in errors:
            print(f"  {name}: {msg}")

    # Reemplazar bloques mermaid con referencias a imágenes
    counter = [0]
    def repl(m):
        i = counter[0]
        name = NAMES[i] if i < len(NAMES) else f"diagram-{i+1}"
        counter[0] += 1
        return f"![{name}](img/{name}.png)"

    new_content = pattern.sub(repl, content)

    # Eliminar el bloque <script> de mermaid (ya no es necesario)
    new_content = re.sub(
        r"\n<script type=\"module\">.*?</script>\n",
        "\n",
        new_content,
        flags=re.DOTALL,
    )

    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\nmos.md actualizado con {len(matches)} referencias a imágenes.")

if __name__ == "__main__":
    main()
