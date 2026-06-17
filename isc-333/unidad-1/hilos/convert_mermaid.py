#!/usr/bin/env python3
import re
import os
import subprocess
import sys

BASE = '/Users/enrique/Documents/GitHub/senquevila/iscodigo.github.io/isc-333/unidad-1/hilos'
MD_FILE = os.path.join(BASE, 'osid.md')
IMG_DIR = os.path.join(BASE, 'img')

os.makedirs(IMG_DIR, exist_ok=True)

with open(MD_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Nombres descriptivos para cada diagrama (en orden de aparición)
names = [
    'renderizado-modulo',
    'windows-estados-hilo',
    'solaris-4-niveles',
    'solaris-estados-hilo',
    'linux-estados-proceso',
    'android-estados-activity',
    'amdahl-ley',
    'valve-estrategias',
    'windows-jerarquia-objetos',
    'windows-ciclo-hilo',
    'solaris-4-niveles-detalle',
    'solaris-interrupciones',
    'linux-fork-clone',
    'linux-namespaces',
    'android-pila-activities',
    'gcd-colas',
    'capitulo4-mindmap',
]

pattern = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)
matches = list(pattern.finditer(content))

print(f'Diagramas encontrados: {len(matches)}')

errors = []
replacements = []  # (start, end, replacement_text)

for i, match in enumerate(matches):
    diagram_code = match.group(1)
    name = names[i] if i < len(names) else f'diagram-{i+1}'
    mmd_file = f'/tmp/{name}.mmd'
    png_file = os.path.join(IMG_DIR, f'{name}.png')

    with open(mmd_file, 'w', encoding='utf-8') as f:
        f.write(diagram_code)

    print(f'  [{i+1}/{len(matches)}] Generando {name}.png ...', end=' ', flush=True)

    result = subprocess.run(
        ['npx', '--yes', '@mermaid-js/mermaid-cli',
         '-i', mmd_file,
         '-o', png_file,
         '-b', 'white',
         '--width', '900',
         '--height', '600'],
        capture_output=True, text=True, timeout=60
    )

    if result.returncode == 0 and os.path.exists(png_file):
        print('OK')
        img_ref = f'![{name}](img/{name}.png)'
        replacements.append((match.start(), match.end(), img_ref))
    else:
        print(f'ERROR\n  stderr: {result.stderr[:300]}')
        errors.append(name)

# Aplicar reemplazos de atrás hacia adelante para no desplazar índices
new_content = content
for start, end, img_ref in reversed(replacements):
    new_content = new_content[:start] + img_ref + new_content[end:]

with open(MD_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'\nCompletado: {len(replacements)} reemplazos realizados.')
if errors:
    print(f'Errores en: {errors}')
    sys.exit(1)
