---
marp: true
theme: default
paginate: true
math: katex
backgroundColor: #ffffff
color: #1e1e2e
style: |
  section {
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 40px 60px;
    background: #ffffff;
    color: #1e1e2e;
  }
  h1 {
    color: #0055b3;
    font-size: 2em;
    border-bottom: 3px solid #0055b3;
    padding-bottom: 10px;
  }
  h2 {
    color: #0055b3;
    font-size: 1.5em;
  }
  h3 {
    color: #0077cc;
    font-size: 1.1em;
    margin-bottom: 4px;
  }
  h4 {
    color: #555;
  }
  ul, ol {
    margin-top: 8px;
  }
  li {
    margin-bottom: 6px;
    font-size: 0.88em;
  }
  code {
    background: #e8f0fe;
    color: #0055b3;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.85em;
  }
  pre {
    background: #f4f6f8;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 12px;
  }
  pre code {
    background: none;
    color: #1e1e2e;
  }
  blockquote {
    border-left: 4px solid #0055b3;
    padding-left: 14px;
    color: #444;
    font-style: italic;
    background: #f0f4ff;
    border-radius: 0 6px 6px 0;
    padding: 8px 14px;
  }
  table {
    font-size: 0.8em;
    border-collapse: collapse;
    width: 100%;
  }
  th {
    background: #0055b3;
    color: #ffffff;
    padding: 8px 10px;
    border: 1px solid #0055b3;
  }
  td {
    padding: 6px 10px;
    border: 1px solid #d0d7de;
  }
  tr:nth-child(even) td {
    background: #f4f6f8;
  }
  section.titulo {
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    background: linear-gradient(135deg, #e8f0fe 0%, #ffffff 100%);
  }
  section.titulo h1 {
    font-size: 2.4em;
    border: none;
    color: #003d99;
  }
  section.titulo h2 {
    color: #0055b3;
    font-size: 1.2em;
  }
  section.titulo h3 {
    color: #0077cc;
  }
  section.titulo h4 {
    color: #666;
  }
  section.dark {
    background: #1a2332;
    color: #ffffff;
  }
  section.dark h1, section.dark h2 {
    color: #66b0ff;
    border-color: #66b0ff;
  }
  section.dark code {
    background: #2a3a50;
    color: #88ccff;
  }
---

<!-- _class: titulo -->

# Capítulo 7: Administración de Memoria
## *Memory Management*
### Sistemas Operativos: Fundamentos y Diseño
#### William Stallings, 9.ª Edición — Parte 3

---

# Contenido del Capítulo 7

| Sección | Tema |
|---------|------|
| **7.1** | Requisitos de la Administración de Memoria |
| **7.2** | Particionamiento de Memoria |
| **7.3** | Paginación (*Paging*) |
| **7.4** | Segmentación (*Segmentation*) |
| **7.5** | Resumen |
| **7.6** | Términos Clave, Preguntas y Problemas |
| **Ap. 7A** | Carga y Enlace (*Loading and Linking*) |

> La administración de memoria es la tarea dinámica de subdividir la memoria de usuario para acomodar múltiples procesos en un sistema multiprogramado.

---

<!-- _class: titulo -->

# 7.1
## Requisitos de la Administración de Memoria

---

# Conceptos fundamentales

| Término | Definición |
|---------|-----------|
| **Frame** (Marco) | Bloque de longitud fija de **memoria principal**. |
| **Page** (Página) | Bloque de datos de longitud fija que reside en **memoria secundaria** (como un disco). Una página de datos puede copiarse temporalmente a un frame de memoria principal. |
| **Segment** (Segmento) | Bloque de datos de **longitud variable** que reside en memoria secundaria. Un segmento completo puede copiarse a una región disponible de memoria principal (segmentación), o dividirse en páginas que pueden copiarse individualmente (segmentación y paginación combinadas). |

---

```
Memoria Secundaria (Disco)          Memoria Principal (RAM)
┌─────────────────────────┐         ┌───────┬───────┐
│  Segmento (long. variable)        │ Frame │ Frame │
│  ┌──────┬──────┬──────┐ │  copia  │   0   │   1   │
│  │Page 0│Page 1│Page 2│ │ ──────→ ├───────┼───────┤
│  └──────┴──────┴──────┘ │         │ Frame │ Frame │
└─────────────────────────┘         │   2   │   3   │
                                    └───────┴───────┘

Segment → puede copiarse completo, o dividirse en Pages
Page    → bloque fijo que se copia a un Frame
Frame   → bloque fijo de memoria principal
```

---

# Cinco requisitos fundamentales

| # | Requisito | Descripción |
|---|-----------|-------------|
| 1 | **Relocación** (Reubicación) | Poder mover procesos a diferentes áreas de memoria |
| 2 | **Protección** | Aislar procesos entre sí y del SO |
| 3 | **Compartición** (*Sharing*) | Permitir acceso controlado a regiones comunes |
| 4 | **Organización Lógica** | Soporte para programas modulares (segmentos) |
| 5 | **Organización Física** | Gestión del flujo entre memoria principal y secundaria |

---

## 7.1a — Relocación

**Problema:** No sabemos de antemano dónde se cargará un proceso en memoria.

- Los procesos se intercambian (*swapping*) entre disco y RAM
- Al recargar, pueden quedar en **diferentes direcciones físicas**

**Solución:** Direcciones **relativas** (lógicas) traducidas a **absolutas** (físicas) por hardware en tiempo de ejecución.

<!--
En un sistema multiprogramado, la memoria principal se comparte entre varios procesos y el programador no puede saber de antemano qué otros programas estarán residentes al momento de ejecutar el suyo. Además, se necesita poder intercambiar (swap) procesos activos entre disco y RAM para maximizar el uso del procesador, lo que implica que un proceso puede volver a cargarse en una región de memoria distinta a la original. El SO conoce fácilmente las direcciones de control, pila y punto de entrada del proceso porque es quien lo carga en memoria; el verdadero desafío es que el procesador debe resolver las referencias a memoria dentro del propio código del programa sin conocer su ubicación final de antemano.
-->

---

![Relocación](img/fig_1_7.png)

<!--
La figura muestra la imagen de un proceso en memoria. El SO ubica fácilmente el control, la pila y el punto de entrada, porque es quien carga el proceso. Lo difícil es otra cosa: las instrucciones de salto y de datos dentro del propio código traen direcciones, y el hardware (procesador) junto con el SO deben traducirlas a direcciones físicas reales según dónde quedó cargado el programa.
-->

---

### 7.1a — Soporte Hardware para Relocación

![Base + Límite](img/fig_hardware_support.svg)
<!--
Nota para el relator: Este es el soporte de hardware mínimo para la relocación dinámica. Cada dirección que genera el proceso es relativa (relativa al inicio de su propio programa, empieza en 0). El Base Register guarda la dirección física donde realmente inicia el proceso en RAM; el hardware (el sumador) suma automáticamente esa base a cada dirección relativa para obtener la dirección absoluta real, en el momento mismo de la ejecución (no antes). Esto es lo que permite mover un proceso de lugar en memoria (por swapping) sin tener que reescribir ni una sola dirección dentro de su código: basta con actualizar el valor del Base Register cuando el proceso se recarga en una posición distinta.
-->

---

- **Base Register:** contiene la dirección de inicio del proceso en memoria
- **Bounds Register:** contiene la dirección final (límite)
- Cada dirección relativa → se suma la base → se compara con el límite
- Si excede el límite → **interrupción** (violación de memoria)

---

### 7.1a — Esquema de Base y Límite
```
Proceso A en memoria (ejemplo):
┌─────────────────────────────────┐
│      SO (sistema operativo)     │ ← 0x00000000
├─────────────────────────────────┤
│  Bloque de Control (PCB)        │
│  Programa                       │
│  Datos                          │
│  Pila                           │ ← Proceso A
├─────────────────────────────────┤
│  ... otros procesos ...         │
└─────────────────────────────────┘
```

<!--
Nota para el relator: Este esquema muestra cómo luce la memoria física en un momento dado: el SO ocupa la parte baja, y el Proceso A ocupa un bloque contiguo que incluye su bloque de control (PCB), su código, sus datos y su pila. El Base Register apuntará al inicio de este bloque (donde comienza A) y el Bounds Register al final del mismo. Cualquier dirección relativa que genere el proceso A se traduce sumándole la base, y se valida contra el límite antes de permitir el acceso.
-->

---

```
  Base Register → 0x00100000 (inicio de A)
  Bounds Register → 0x00104000 (fin de A)

  Dirección relativa 0x00000200
  → Dirección absoluta = 0x00100000 + 0x00000200 = 0x00100200
  → ¿Está dentro de [0x00100000, 0x00104000]? Sí → OK
```

---

## 7.1b — Protección

**Cada proceso debe estar aislado de los demás.**

- No puede leer/escribir memoria de otro proceso sin permiso
- No puede acceder al código/datos del SO
- No puede bifurcar (*branch*) a otro proceso

**¿Quién implementa la protección?**

| Componente | Rol |
|------------|-----|
| **Hardware** (CPU/MMU) | Verifica cada referencia en tiempo de ejecución |
| **SO** | Establece los límites al cambiar de contexto |

> La protección debe ser implementada por el **procesador**, no por el SO, porque el SO no puede anticipar todas las referencias que hará un programa.

---

## 7.1c — Compartición (*Sharing*)

**Varios procesos accediendo a la misma región de memoria.**

```
  ┌──────────────┐
  │  Editor de   │◄────── Proceso A
  │  Texto       │
  │  (única      │◄────── Proceso B
  │   copia)     │
  │              │◄────── Proceso C
  └──────────────┘
```

**Ejemplos:**
- Múltiples usuarios ejecutando el **mismo editor/programa**
- Procesos cooperativos compartiendo una **estructura de datos común**
- Bibliotecas compartidas (DLLs en Windows, .so en Linux)

**Requisito:** Mecanismos de protección **flexibles** que permitan acceso compartido controlado.

---

## 7.1d — Organización Lógica

La memoria física es un espacio **lineal/unidimensional**, pero los programas son **modulares**:

```
Programa típico:
┌─────────────────────┐
│ Módulo: main()      │ ← código ejecutable
├─────────────────────┤
│ Módulo: funciones   │ ← código reutilizable
├─────────────────────┤
│ Datos globales      │ ← modificable
├─────────────────────┤
│ Pila (stack)        │ ← crece/decrece
├─────────────────────┤
│ Heap (montículo)    │ ← asignación dinámica
└─────────────────────┘
```

---

**Ventajas de la organización modular:**
- Módulos compilados **independientemente**
- Diferentes niveles de protección (solo lectura, solo ejecución)
- Compartición a nivel de **módulo** (más natural para el usuario)

---

## 7.1e — Organización Física

**Dos niveles de memoria:**

| Nivel | Velocidad | Costo | Volatilidad | Capacidad |
|-------|-----------|-------|-------------|-----------|
| **Principal** (RAM) | Rápida | Alto | Volátil | Pequeña (GB) |
| **Secundaria** (Disco) | Lenta | Bajo | Persistente | Grande (TB) |

---

**El flujo entre niveles debe ser organizado por el SO:**

```
              ┌──────────────┐
              │   Memoria    │
              │   Principal  │
              │   (RAM)      │
              └──────┬───────┘
                     │ swap in / swap out
                     │ page in / page out
              ┌──────▼───────┐
              │   Memoria    │
              │  Secundaria  │
              │   (Disco)    │
              └──────────────┘
```

---

<!-- _class: titulo -->

# 7.2
## Particionamiento de Memoria
### *Memory Partitioning*

---

# 7.2 — Técnicas de Particionamiento

Tres esquemas históricos:

| Esquema | Descripción | Fragmentación |
|---------|-------------|---------------|
| **Partición Fija** | Tamaños predeterminados en boot | **Interna** (espacio desperdiciado dentro de la partición) |
| **Partición Dinámica** | Tamaños según necesidad | **Externa** (huecos entre particiones) |
| **Buddy System** | Bloques de tamaño $2^K$ | Híbrido (compromiso) |

<!--
Nota para el relator (Stallings, Cap. 7): Tanto la partición fija como la dinámica tienen desventajas: la fija limita el número de procesos activos y desperdicia espacio si no hay buen ajuste entre el tamaño de las particiones y el de los procesos (fragmentación interna); la dinámica es más compleja de mantener y añade el costo de la compactación (fragmentación externa). El Buddy System es un compromiso interesante entre ambas: mantiene bloques de tamaño 2^K, con 2^L como el bloque más pequeño asignable y 2^U como el bloque más grande (normalmente toda la memoria disponible). Al pedir memoria, se divide recursivamente el bloque más pequeño disponible en dos "compañeros" (buddies) iguales hasta llegar al tamaño necesario; al liberar, dos buddies libres se funden (coalescen) de nuevo en un bloque mayor. Es un compromiso razonable, aunque en sistemas modernos la memoria virtual (paginación/segmentación) lo supera; aun así se sigue usando, por ejemplo, en la asignación de memoria del kernel de UNIX.
-->

---

# 7.2a — Partición Fija

**Memoria dividida en particiones de tamaño fijo en tiempo de boot.**

```
┌─────────────────────────────────┐                             PROBLEMA
│          SO (OS)                │ ← 0 MB              - Un proceso de 3 MB en una partición de
├─────────────────────────────────┤                       8 MB → desperdicia 5 MB.
│  Partición 1:  8 MB             │ ← Proceso A.        
├─────────────────────────────────┤                     - Se define la partición para el proceso más 
│  Partición 2:  16 MB            │ ← Proceso B           grande esperado.
├─────────────────────────────────┤
│  Partición 3:  32 MB            │ ← Proceso C
├─────────────────────────────────┤
│  Partición 4:  64 MB            │ ← Proceso D
├─────────────────────────────────┤
│  ...                            │
└─────────────────────────────────┘ ← 256 MB
```

---

# 7.2a — Cola de Particiones Fijas

Dos estrategias de organización:

**a) Cola única por partición:**

```
         ┌─────────┐
  Procs  │ 8 MB    │ ─── Proceso A
         ├─────────┤
         │ 16 MB   │ ─── Proceso B
         ├─────────┤
         │ 32 MB   │ ─── Proceso C
         ├─────────┤
         │ 64 MB   │ ─── Proceso D
         └─────────┘
```

---

**b) Cola única global:**
- Todos los procesos esperan en una cola
- Se asigna a la partición más pequeña que pueda contenerlos
- Maximiza el uso de memoria pero aumenta la planificación

---

# 7.2b — Partición Dinámica

**Las particiones se crean según la demanda de los procesos.**

```
Ejemplo (Figura 7.4):
(a) SO ──── [8M] ────
(b) SO | A(8M) | ──[8M]──
(c) SO | A(8M) | B(14M) | ──[22M]──
(d) SO | A(8M) | B(14M) | C(18M) | ─[4M]─
(e) SO | ─[8M]─ | B(14M) | C(18M) | ─[4M]─
(f) SO | D(8M) | B(14M) | C(18M) | ─[4M]─
(g) SO | D(8M) | ─[14M]─ | C(18M) | ─[4M]─
(h) SO | D(8M) | ─[8M]─ | C(18M) | E(6M) | ─[4M]─
```

**Problema: Fragmentación Externa**
- Aparecen **huecos** (agujeros) entre particiones activas
- El espacio total libre es suficiente pero no contiguo

---

# 7.2b — Fragmentación Externa

```
Fragmentación Externa:
┌──────────┬──────────┬──────────┬──────────┐
│  A(8M)   │          │  B(14M)  │          │
│          │  hueco   │          │  hueco   │
│          │   6M     │          │   4M     │
└──────────┴──────────┴──────────┴──────────┘

Total libre = 10 MB, pero ningún bloque ≥ 8 MB contiguo.
→ No se puede cargar un proceso de 8 MB aunque haya espacio libre.
```

**Solución: Compactación**
- Reorganizar procesos para juntar todo el espacio libre
- Costosa en tiempo de CPU
- Requiere capacidad de **relocación dinámica**

---

# 7.2b — Algoritmos de Colocación (Placement)

Tres algoritmos para elegir dónde colocar un proceso:

| Algoritmo | Descripción | Fragmento resultante |
|-----------|-------------|---------------------|
| **First-Fit** | Primer bloque suficientemente grande | Fragmento variable |
| **Best-Fit** | Bloque más ajustado al tamaño solicitado | Fragmento **más pequeño** posible |
| **Next-Fit** | Siguiente bloque desde la última asignación | Fragmento al final |

```
Memoria: [8M libre][12M usado][22M libre][6M usado][18M libre]

Solicitud de 16M:
  First-Fit: usa 22M → deja 6M
  Best-Fit:  usa 18M → deja 2M (peor fragmentación a largo plazo)
  Next-Fit:  usa 22M → deja 6M (como first-fit pero desde última posición)
```

---

# 7.2b — Comparación de Algoritmos de Colocación

**Conclusión general ([Bren89], [Shor75], [Bays77]):**

| Algoritmo | Rendimiento |
|-----------|-------------|
| **First-Fit** | ✅ **Generalmente el mejor y más rápido** |
| **Next-Fit** | ⚠️ Peor que first-fit; fragmenta el final de memoria |
| **Best-Fit** | ❌ El peor a largo plazo (deja fragmentos inutilizables) |

**¿Por qué Best-Fit es el peor?**
- Aunque desperdicia menos en cada asignación...
- ...crea muchos **fragmentos pequeños** que no sirven para nada
- Obliga a compactar **más frecuentemente**

---

# 7.2c — Buddy System (Sistema de Compañeros)

**Compromiso entre partición fija y dinámica.**

**Reglas:**
- Bloques disponibles de tamaño $2^K$ (potencias de 2)
- Rango: $2^L$ (mínimo) a $2^U$ (máximo = memoria total)
- Al solicitar: dividir el bloque más pequeño que quepa
- Al liberar: **coalescer** (fusionar) si ambos "compañeros" (*buddies*) están libres

```
Ejemplo con 1 MB inicial:
           ┌───────────────────────────────┐
           │          1 MB                 │
           └──────────────┬────────────────┘
                          │ split
              ┌───────────┴───────────┐
              │ 512K                  │ 512K
              └────────┬──────────────┘
                       │ split
                  ┌────┴────┐
                  │ 256K    │ 256K
                  └────┬────┘
                       │ split
                    ┌──┴──┐
                    │128K │128K  ← Un buddy se asigna
                    └─────┘
```

---

# 7.2c — Buddy System — Ejemplo Completo (Figura 7.6)

```
Secuencia de asignaciones/liberaciones en 1 MB:

1. Solicitud A=100K → asigna 128K       ┌─128K─┬─128K─┬─256K─┬─────512K─────┐
2. Solicitud B=240K → asigna 256K       ┌─128K─┬─128K─┬─256K─┬─────512K─────┐
                                          A=128K         B=256K
3. Solicitud C=64K  → asigna 64K        ┌──64K──┬─64K──┬─256K─┬─────512K────┐
                                          C=64K
4. Solicitud D=256K → asigna 256K       ┌──64K──┬─64K──┬─256K─┬─256K─┬─256K─┐
                                          C=64K         B=256K D=256K
5. Libera B → coalesce 256K + 256K=512K ┌──64K──┬─64K──┬─────────512K────────┐
                                          C=64K                 D=256K
6. Solicitud E=75K → asigna 128K...
```

**Aplicación:** Usado en kernels UNIX para asignación de memoria del kernel.

---

# 7.2d — Relocación (Base + Límite)

```
       ┌─────────────┐
       │  Dirección   │
       │  Relativa    │────┐
       └─────────────┘    │
                          ▼
                  ┌───────────────┐
     Base Reg ───→│    Sumador    │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  Dirección    │
     Bounds Reg──→│  ¿Dentro de   │──Sí──→ Acceso permitido
                  │  límites?     │
                  └───────┬───────┘
                          │ No
                          ▼
                   Interrupción al SO
                   (violación de segmento)
```

- **Base Register:** dirección de inicio del proceso
- **Bounds Register:** dirección final (o tamaño máximo)
- Permite **swapping** sin cambiar direcciones en el código

---

<!-- _class: titulo -->

# 7.3
## Paginación
### *Paging*

---

# 7.3 — Paginación: Concepto

**Idea central:** Dividir la memoria en fragmentos pequeños de **tamaño fijo**.

```
Proceso en disco:                    Memoria Principal:
┌──────┐ Page 0                     ┌──┬──┬──┬──┬──┬──┬──┬──┐
│ Pág 0│─────┐                     │  │A0│  │A1│  │A2│  │A3│
├──────┤     │                     ├──┼──┼──┼──┼──┼──┼──┼──┤
│ Pág 1│     └────────────────────→│0 │1 │2 │3 │4 │5 │6 │7 │
├──────┤                           └──┴──┴──┴──┴──┴──┴──┴──┘
│ Pág 2│─────→ Frame 4
├──────┤
│ Pág 3│─────→ Frame 6
└──────┘
```

**Ventaja:** No hay fragmentación externa. Solo fragmentación interna en la última página.

---

# 7.3 — Asignación de Procesos a Frames (Fig. 7.9)

```
(a) 15 frames libres    (b) Carga A (4 págs)     (c) Carga B (3 págs)

┌──┬──┬──┬──┬──┬──┐    ┌──┬──┬──┬──┬──┬──┐    ┌──┬──┬──┬──┬──┬──┐
│0 │1 │2 │3 │4 │5 │    │A0│A1│A2│A3│  │  │    │A0│A1│A2│A3│B0│B1│
├──┼──┼──┼──┼──┼──┤    ├──┼──┼──┼──┼──┼──┤    ├──┼──┼──┼──┼──┼──┤
│6 │7 │8 │9 │10│11│    │  │  │  │  │  │  │    │B2│  │  │  │  │  │
├──┼──┼──┼──┼──┼──┤    ├──┼──┼──┼──┼──┼──┤    ├──┼──┼──┼──┼──┼──┤
│12│13│14│  │  │  │    │  │  │  │  │  │  │    │  │  │  │  │  │  │
└──┴──┴──┴──┴──┴──┘    └──┴──┴──┴──┴──┴──┘    └──┴──┴──┴──┴──┴──┘

(d) Carga C (4 págs)    (e) Swap out B           (f) Carga D (5 págs)

┌──┬──┬──┬──┬──┬──┐    ┌──┬──┬──┬──┬──┬──┐    ┌──┬──┬──┬──┬──┬──┐
│A0│A1│A2│A3│B0│B1│    │A0│A1│A2│A3│  │  │    │A0│A1│A2│A3│D0│D1│
├──┼──┼──┼──┼──┼──┤    ├──┼──┼──┼──┼──┼──┤    ├──┼──┼──┼──┼──┼──┤
│B2│C0│C1│C2│C3│  │    │  │C0│C1│C2│C3│  │    │D2│C0│C1│C2│C3│  │
├──┼──┼──┼──┼──┼──┤    ├──┼──┼──┼──┼──┼──┤    ├──┼──┼──┼──┼──┼──┤
│  │  │  │  │  │  │    │  │  │  │  │  │  │    │D3│D4│  │  │  │  │
└──┴──┴──┴──┴──┴──┘    └──┴──┴──┴──┴──┴──┘    └──┴──┴──┴──┴──┴──┘
```

**Observación:** Las páginas de un proceso NO necesitan estar en frames contiguos.

---

# 7.3 — Tabla de Páginas (Figura 7.10)

**Cada proceso tiene su propia tabla de páginas.**

```
Proceso A (4 págs)          Proceso D (5 págs)
┌──────┬───────┐            ┌──────┬───────┐
│ Pág  │ Frame │            │ Pág  │ Frame │
├──────┼───────┤            ├──────┼───────┤
│  0   │   0   │            │  0   │   4   │
│  1   │   1   │            │  1   │   5   │
│  2   │   2   │            │  2   │   6   │
│  3   │   3   │            │  3   │  11   │
└──────┴───────┘            │  4   │  12   │
                            └──────┴───────┘
Lista de frames libres: [13, 14, ...]
```

**Traducción de dirección lógica:**
```
Dirección lógica = (página 1, offset 478)
  → Buscar página 1 en la tabla → frame 5
  → Dirección física = frame 5 + offset 478
```

---

# 7.3 — Dirección Lógica en Paginación

**El tamaño de página debe ser potencia de 2.**

```
Ejemplo: direcciones de 16 bits, página de 1K = 1024 bytes = 2^10

Dirección relativa: 1502 = 0000010111011110

  6 bits             10 bits
┌──────────┐    ┌──────────────┐
│ Página 1 │    │ Offset 478   │
│ (000001) │    │ (0111011110) │
└──────────┘    └──────────────┘
```

**Traducción (Figura 7.12a):**
```
  Logical: 000001 0111011110
           ↓       ↓
  Pág 1 → Frame 6 (000110)
           ↓       ↓
  Physical: 000110 0111011110 = Frame 6, offset 478
```

---

# 7.3 — Traducción de Direcciones (Paginación)

```
        Dirección Lógica (n+m bits)
        ┌──────────────────────┐
        │  Page #  │  Offset   │
        │  (n bits)│  (m bits) │
        └─────┬────┴─────┬────┘
              │          │
              ▼          │
        ┌──────────┐     │
        │Page Table│     │
        │[pág]→frame│    │
        └─────┬────┘     │
              │          │
       Frame  │          │  Offset
         #    │          │
              ▼          ▼
        ┌──────────────────────┐
        │  Dirección Física    │
        │  Frame #  |  Offset  │
        └──────────────────────┘
```

**Pasos:**
1. Extraer #página (bits más significativos)
2. Indexar en la tabla de páginas → obtener #frame
3. Concatenar frame + offset = dirección física

---

# 7.3 — Resumen de Paginación Simple

**Ventajas:**
- ✅ Sin fragmentación externa
- ✅ No requiere compactación
- ✅ Los frames no necesitan ser contiguos
- ✅ Transparente al programador/compilador

**Desventajas:**
- ❌ Fragmentación interna (última página parcialmente usada)
- ❌ Overhead de la tabla de páginas (memoria)
- ❌ Dos accesos a memoria por cada referencia (uno a la tabla, otro al dato)

> La paginación simple requiere que **todas** las páginas de un proceso estén en memoria para ejecutarse. La **memoria virtual** (Cap. 8) elimina esta limitación.

---

<!-- _class: titulo -->

# 7.4
## Segmentación
### *Segmentation*

---

# 7.4 — Segmentación: Concepto

**División del programa en segmentos de tamaño variable según su función lógica.**

```
Programa:
┌──────────────────────┐
│ Segmento: main()     │ ← código principal
├──────────────────────┤
│ Segmento: funciones  │ ← bibliotecas/módulos
├──────────────────────┤
│ Segmento: datos      │ ← variables globales
├──────────────────────┤
│ Segmento: pila       │ ← stack
├──────────────────────┤
│ Segmento: heap       │ ← memoria dinámica
└──────────────────────┘
```

**Dirección lógica:** (segmento #, offset)

---

# 7.4 — Segmentación vs. Partición Dinámica vs. Paginación

| Característica | Paginación | Segmentación | Partición Dinámica |
|---------------|------------|-------------|-------------------|
| Tamaño de bloque | Fijo (page/frame) | Variable (segmento) | Variable (proceso completo) |
| Visibilidad al programador | Transparente | **Visible** (explícita) | Transparente |
| Fragmentación | Interna (mínima) | **Externa** | Externa |
| Organización | Lineal | **Lógica** (modular) | Lineal |
| Tabla | Tabla de páginas | Tabla de segmentos | — |

---

# 7.4 — Dirección Lógica en Segmentación (Figura 7.11c)

```
Dirección lógica 16 bits: 4 bits segmento + 12 bits offset

Ejemplo: (segmento 1, offset 752)
  0001 001011110000

  4 bits         12 bits
┌──────┐    ┌──────────────┐
│Seg 1 │    │ Offset 752   │
│(0001)│    │(001011110000)│
└──┬───┘    └──────┬───────┘
   │               │
   ▼               │
┌──────────┐       │
│Tabla de  │       │
│Segmentos │       │
│[seg]→base│       │
│       len│       │
└─────┬────┘       │
      │            │
  Base ────────────┤
      │            │
      ▼            ▼
   ┌─────────────────────┐
   │ Dirección Física    │
   │ (base + offset)     │
   └─────────────────────┘
```

---

# 7.4 — Traducción en Segmentación (Figura 7.12b)

```
Dirección lógica: segmento 1, offset 752

Tabla de segmentos del proceso:
┌──────┬──────────────┬──────────────────┐
│ Seg  │ Longitud      │ Base (dirección) │
├──────┼──────────────┼──────────────────┤
│  0   │  750 bytes   │  0x00010000      │
│  1   │  1950 bytes  │  0x00020000      │
│  2   │  1024 bytes  │  0x00080000      │
│  3   │  512 bytes   │  0x000A0000      │
└──────┴──────────────┴──────────────────┘

¿Offset 752 < Longitud 1950? → Sí ✓
Dirección física = 0x00020000 + 752 = 0x000202F0
```

**Protección por segmento:**
- Segmento 0: solo lectura (código)
- Segmento 1: lectura/escritura (datos)
- Segmento 2: solo ejecución

---

# 7.4 — Ventajas de la Segmentación

```
Organización modular del programa:
┌──────────────────────┐
│  main()              │ ← solo ejecución (RX)
├──────────────────────┤
│  lib-matemáticas     │ ← compartible entre procesos
├──────────────────────┤
│  datos-personales    │ ← privado (RW)
├──────────────────────┤
│  datos-compartidos   │ ← compartido (RW)
├──────────────────────┤
│  pila                │ ← privado (RW)
└──────────────────────┘
```

**Ventajas:**
- ✅ Compilación **independiente** de módulos
- ✅ Diferentes niveles de **protección** por segmento
- ✅ **Compartición** a nivel de módulo (segmento)
- ✅ Adecuado para la **organización lógica** del programa

---

# 7.4 — Segmentación vs. Paginación: Comparación

| Aspecto | Paginación | Segmentación |
|---------|-----------|-------------|
| **Tamaño** | Fijo (determinado por HW) | Variable (definido por programador) |
| **Visible al programador?** | No | Sí |
| **Fragmentación** | Interna (mínima) | Externa |
| **Protección granular** | Por página (mismo nivel) | **Por segmento** (distintos niveles) |
| **Compartición** | Difícil (páginas no lógicas) | **Natural** (segmento = módulo) |
| **Uso principal** | Memoria virtual (Cap. 8) | Organización de programas |

> **Observación:** Los sistemas modernos (x86, ARM) usan **segmentación + paginación combinadas**. La segmentación organiza lógicamente; la paginación maneja la memoria física.

---

<!-- _class: titulo -->

# Resumen del Capítulo 7

---

# Resumen — Administración de Memoria

**Requisitos (§7.1):** Relocación, Protección, Compartición, Org. Lógica, Org. Física

**Técnicas de particionamiento (§7.2):**
| Técnica | Característica | Fragmentación |
|---------|---------------|---------------|
| Partición Fija | Tamaños predefinidos | Interna |
| Partición Dinámica | Tamaños variables según proceso | Externa |
| Buddy System | Bloques $2^K$ | Híbrida |

**Algoritmos de colocación:** First-Fit (mejor) → Next-Fit → Best-Fit (peor)

**Paginación (§7.3):**
- Memoria dividida en **frames**; procesos en **pages**
- Tabla de páginas por proceso
- Sin fragmentación externa

**Segmentación (§7.4):**
- Memoria dividida en **segmentos** lógicos
- Tabla de segmentos con base + límite
- Soporte natural para protección y compartición

---

# Términos Clave

| Término | Definición |
|---------|-----------|
| **Frame** | Bloque de tamaño fijo en memoria principal |
| **Page** | Bloque de tamaño fijo en memoria secundaria |
| **Segment** | Bloque de tamaño variable con significado lógico |
| **Fragmentación Interna** | Espacio desperdiciado dentro de un bloque asignado |
| **Fragmentación Externa** | Huecos entre bloques asignados |
| **Compactación** | Reorganización de memoria para eliminar fragmentación externa |
| **Relocación** | Capacidad de mover procesos en memoria sin invalidar referencias |
| **Base Register** | Registro HW con la dirección base del proceso |
| **Bounds Register** | Registro HW con el límite del proceso |
| **Page Table** | Tabla que mapea páginas lógicas a frames físicos |
| **Segment Table** | Tabla que mapea segmentos lógicos a direcciones base |

---

# Preguntas de Repaso

1. ¿Cuáles son los **cinco requisitos** que debe satisfacer la administración de memoria?

2. ¿Cuál es la diferencia entre fragmentación **interna** y **externa**?

3. ¿Por qué **Best-Fit** suele ser peor que **First-Fit** a largo plazo?

4. ¿Cómo funciona el **Buddy System**? Da un ejemplo con asignación y liberación.

5. En paginación, ¿cómo se traduce una dirección lógica `(página 3, offset 150)` a física si la página 3 está en el frame 12 y el tamaño de página es 1 KB?

6. ¿Cuál es la principal ventaja de la **segmentación** sobre la paginación? ¿Y la principal desventaja?

7. ¿Por qué la **protección** debe ser implementada por el hardware y no por el SO?

8. ¿Qué rol cumplen los registros **Base** y **Bounds** en la relocación?

---

<!-- _class: titulo -->

# Apéndice 7A
## Carga y Enlace
### *Loading and Linking*

---

# Ap. 7A — Carga y Enlace

**Proceso de preparación de un programa para ejecución:**

```
Código Fuente
     │
     ▼ Compilación
Código Objeto (módulo .o/.obj)
     │
     ▼ Enlace (Linking)
Módulo Cargable (ejecutable)
     │
     ▼ Carga (Loading)
Proceso en Memoria (ejecución)
```

---

# Ap. 7A — Tipos de Enlace

| Tipo | Momento | Descripción |
|------|---------|-------------|
| **Enlace Estático** | Antes de ejecución | Todas las bibliotecas se incluyen en el ejecutable |
| **Enlace Dinámico** | Durante ejecución | Bibliotecas compartidas cargadas bajo demanda |

**Ventajas del enlace dinámico:**
- Menor tamaño de ejecutables
- Actualización de bibliotecas sin recompilar
- Compartición de código entre procesos (una copia en RAM)

**Desventaja:**
- Dependencia de la presencia de las DLLs/.so
- Posible fragmentación de versiones (*DLL Hell*)

---

# Ap. 7A — Tipos de Carga

| Tipo | Descripción |
|------|-------------|
| **Carga Absoluta** | Carga en dirección fija; requiere reensamblado si cambia |
| **Carga Relocalizable** | El cargador ajusta direcciones (usa base register) |

**Relocación dinámica:**
- Los programas usan direcciones relativas
- El hardware (MMU) + SO traducen en tiempo real
- Permite swapping y carga en cualquier dirección disponible

> Los sistemas modernos combinan **enlace dinámico** + **carga relocalizable** para máxima flexibilidad.

---

<!-- _class: titulo -->

# Fin del Capítulo 7
## Administración de Memoria
### *"Memory Management"*
#### Stallings — Operating Systems: Internals and Design Principles, 9.ª Ed.
