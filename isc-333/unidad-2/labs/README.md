# Laboratorio: Procesos vs Hilos

Material del laboratorio de procesos e hilos (Unidad 2), en Linux (pthreads) y Windows (Win32 API).

## Archivos

| Archivo | Descripción |
|---|---|
| `lab-hilos-linux.md` / `.tex` / `.pdf` | Laboratorio para Linux (pthreads) |
| `lab-hilos-windows.md` / `.tex` / `.pdf` | Laboratorio para Windows (Win32 API) |

## Regenerar los PDF

Los `.pdf` se generan a partir de los `.tex` con [Tectonic](https://tectonic-typesetting.github.io/) (motor LaTeX autocontenido, no requiere instalar TeX Live completo):

```bash
brew install tectonic
tectonic lab-hilos-linux.tex
tectonic lab-hilos-windows.tex
```

**No usar `pandoc` para esta conversión**: pandoc reinterpreta el `.tex` como su propio AST antes de generar el PDF, lo que rompe los paquetes `listings`/`fontspec` usados en estos documentos (error `Undefined control sequence`). Compilar con `tectonic` directamente sobre el `.tex` evita ese problema.
