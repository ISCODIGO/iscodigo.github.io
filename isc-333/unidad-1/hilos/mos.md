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
---

<!-- _class: titulo -->

# Capítulo 2: Hilos
## Sección 2.2 (Threads)
### Modern Operating Systems
#### Andrew S. Tanenbaum · Herbert Bos

---

# 2.2 Hilos: idea central

En sistemas tradicionales, un proceso tiene:
- su propio espacio de direcciones
- **un solo hilo de control**

La sección 2.2 introduce múltiples hilos de control dentro del mismo espacio de direcciones, ejecutándose en cuasi-paralelo.

> Los hilos permiten mantener ejecución secuencial por actividad, pero compartiendo memoria y datos del proceso.

---

# 2.2.1 ¿Por qué usar hilos?

Razones principales:
- En muchas aplicaciones ocurren **múltiples actividades simultáneas**.
- Los hilos son más ligeros que los procesos: creación/destrucción mucho más rápida.
- Permiten superponer **cómputo + E/S** cuando una actividad se bloquea.
- En sistemas con múltiples CPU habilitan paralelismo real.

Limitación:
- Si todas las actividades son puramente CPU-bound, los hilos no aportan mejora de rendimiento por sí solos.

---

# Ejemplo 1: procesador de texto (Fig. 2-7)

### Modelo de tres hilos:

![procesador-texto](img/procesador-texto.png)

---

# Procesador de texto: beneficios del modelo multihilo

- Mejor respuesta al usuario sin programación basada en interrupciones complejas.
- Compartir memoria del proceso permite operar sobre el mismo documento.

---

# Ejemplo 2: servidor Web multihilo (Fig. 2-8)

### Arquitectura:

![servidor-web-arch](img/servidor-web-arch.png)

---

# Servidor Web multihilo: ventaja

- Mientras un worker espera disco, otros continúan procesando solicitudes.
- Se conserva un modelo de programación secuencial por hilo.

---

# Servidor Web multihilo (Fig. 2-9)

![servidor-web-workers](img/servidor-web-workers.png)

---

# Tres modelos para construir un servidor (Fig. 2-10)

| Modelo | Características | Paralelismo | Simplicidad |
|---|---|---|---|
| **Hilos** | Paralelismo + llamadas bloqueantes | ✅ | ✅ |
| **Proceso monohilo** | Sin paralelismo + llamadas bloqueantes | ❌ | ✅ |
| **Máquina de estados finitos** | Paralelismo + llamadas no bloqueantes + interrupciones | ✅ | ❌ |

Conclusión:
- Hilos combinan **simplicidad** de llamadas bloqueantes con mejor **rendimiento** por solapamiento.

---

# 2.2.2 Modelo clásico de hilos

El modelo de proceso contiene dos conceptos:
1. **Agrupación de recursos** (espacio de direcciones, archivos, señales, etc.).
2. **Ejecución** (hilo con PC, registros y pila).

Separación conceptual:
- **Proceso** = unidad de recursos.
- **Hilo** = unidad planificable en CPU.

Múltiples hilos dentro de un proceso comparten recursos, pero cada hilo mantiene su contexto de ejecución privado.

---

# Recursos por proceso vs por hilo (Fig. 2-12)

![recursos-proceso-hilo](img/recursos-proceso-hilo.png)

---

# Estados clásicos de un hilo

![estados-hilo](img/estados-hilo.png)

---

# Operaciones básicas de hilos

- `thread_create` — crear hilo
- `thread_exit` — terminar hilo
- `thread_join` — esperar a otro hilo
- `thread_yield` — ceder CPU voluntariamente

---

# Complicaciones del modelo multihilo

Problemas que aparecen al usar hilos:
- **Interacción con `fork`**
  - ¿Cuándo se duplican todos los hilos?
  - ¿Solo se duplica el hilo que invocó `fork`?
- **Acceso concurrente a estructuras compartidas**
  - Requiere sincronización (mutex, semáforos).
- **Cierre de recursos usados por otro hilo**
  - Un hilo cierra un archivo que otro hilo está usando.
  - Requiere conteo de referencias o cuidado en diseño.

---

# 2.2.3 POSIX Threads (Pthreads)

IEEE 1003.1c define un estándar portable de hilos.

Llamadas destacadas:

| Función | Descripción |
|---|---|
| `pthread_create` | Crea un nuevo hilo |
| `pthread_exit` | Termina el hilo actual |
| `pthread_join` | Espera a que otro hilo termine |
| `pthread_yield` | Cede voluntariamente la CPU |
| `pthread_attr_init` | Inicializa atributos de hilo |
| `pthread_attr_destroy` | Libera atributos de hilo |

La sección muestra un ejemplo de programa que crea 10 hilos, cada uno imprime su identificador y termina.

---

# 2.2.4 Hilos en espacio de usuario (Fig. 2-16a)

![hilos-user-space](img/hilos-user-space.png)

---

# Ventajas: hilos en espacio de usuario

- No requiere soporte de hilos en el kernel.
- Cambio de hilo muy rápido (sin llamada al sistema).
- Planificación personalizable por proceso.

---

# Problemas de hilos en espacio de usuario

Problemas:
- **Llamadas bloqueantes** pueden bloquear todo el proceso.
  - Ejemplo: `read()` bloquea el proceso, no solo el hilo.
- **Fallos de página** bloquean el proceso completo.
- **Sin interrupción de reloj por hilo**, puede faltar equidad.
  - Un hilo CPU-bound monopoliza el proceso.

Solución: **jacketing** — envolver llamadas bloqueantes en wrappers que verifican si bloquearían y cambian de hilo en su lugar.

---

# 2.2.5 Hilos en el kernel (Fig. 2-16b)

![hilos-kernel](img/hilos-kernel.png)

---

# Hilos en el kernel: ventajas y desventaja

## Ventajas:
- Si un hilo bloquea, el kernel puede ejecutar otro hilo listo.
- No requiere wrappers para evitar bloqueos de llamadas.
- Manejo más natural de page faults por hilo.

## Desventaja:
- Operaciones de hilo implican llamadas al sistema (más costo).

---

# 2.2.6 Implementaciones híbridas (Fig. 2-17)

![hilos-hibrido](img/hilos-hibrido.png)

---

# Implementaciones híbridas: análisis

## Idea:
- Combinar flexibilidad y bajo costo en user space con capacidad de bloqueo/planificación en kernel.

## Resultado:
- El kernel planifica hilos de kernel.
- El runtime de usuario planifica hilos de usuario sobre ellos.

---

# 2.2.7 Activaciones del planificador

## Objetivo:
- Aproximar ventajas de hilos de kernel con rendimiento/flexibilidad de user space.

## Mecanismo clave:
- El kernel asigna **procesadores virtuales** por proceso.
- Cuando un hilo bloquea o se desbloquea, el kernel notifica al runtime mediante **upcalls**.
- El runtime decide qué hilo ejecutar después.

## Punto crítico:
- `upcall` rompe el patrón clásico estratificado (capa inferior invocando superior).

---

# 2.2.8 Pop-up threads

## Concepto:
Al llegar un mensaje, el sistema crea un hilo nuevo para atenderlo inmediatamente.

![popup-threads](img/popup-threads.png)

---

# Pop-up threads: ventajas y consideraciones

## Ventaja principal:
- Muy baja latencia entre llegada del mensaje e inicio de procesamiento.

## Consideraciones:
- Puede ejecutarse en contexto de kernel (más rápido, acceso directo).
- Un bug en kernel thread es más peligroso que en user thread.

---

# 2.2.9 Convertir código monohilo a multihilo

## Dificultades destacadas:

| Problema | Ejemplo | Solución |
|---|---|---|
| Variables globales | `errno` (variable global de error) | Hacer `errno` privada por hilo |
| Bibliotecas no reentrantes | `strtok`, `malloc` no thread-safe | Wrappers/jackets para serializar |
| Señales | ¿Qué hilo recibe `SIGINT`? | Señales por proceso o hilo específico |
| Gestión de pilas | Múltiples pilas por proceso | Stack guard pages, crecimiento automático |

---

# Técnicas para conversión a multihilo

- Variables globales privadas por hilo (TLS — Thread-Local Storage).
- Wrappers/jackets para serializar secciones no seguras.

---

# Resumen: Modelos de implementación de hilos

| Característica | User space | Kernel | Híbrido |
|---|---|---|---|
| **Cambio de hilo** | Rápido (no syscall) | Lento (syscall) | Medio |
| **Bloqueo de llamada** | Bloquea proceso | Solo bloquea hilo | Depende |
| **Paralelismo en MP** | No | Sí | Sí (si hay KLTs >= CPUs) |
| **Flexibilidad** | Alta | Baja | Media |
| **Ejemplo** | GNU Portable Threads | Windows/Linux nativo | Solaris, NPTL |

---

# Resumen: conceptos clave de la sección 2.2

![resumen-mindmap](img/resumen-mindmap.png)

---

<!-- _class: titulo -->

# Fin de la sección 2.2
## Hilos = concurrencia con memoria compartida

- Simplifican varios modelos interactivos y de servidor.
- Exigen diseño cuidadoso de sincronización y recursos compartidos.
- La implementación (usuario, kernel o híbrida) define el compromiso entre rendimiento y complejidad.

> *«Un hilo es una unidad de ejecución que comparte el espacio de direcciones del proceso con otros hilos, pero tiene su propio contador de programa, registros y pila.»*
> — Tanenbaum & Bos, Modern Operating Systems

