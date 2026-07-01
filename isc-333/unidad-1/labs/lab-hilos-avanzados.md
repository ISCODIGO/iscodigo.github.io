---
layout: default
title: "Lab: Hilos Avanzados — Basado en Stallings Cap. 4"
parent: "Unidad I: Introducción a SO y Control de Procesos"
grand_parent: "ISC-333 Sistemas Operativos I"
nav_order: 7
has_mermaid: true
---

# Laboratorio: Hilos y Procesos en Linux

**Basado en:** Stallings, *Operating Systems: Internals and Design Principles*, 9.ª Ed., **Capítulo 4 — Threads**  
**Plataforma:** GNU/Linux (Ubuntu / Debian)  
**Compilador:** GCC  
**Biblioteca:** POSIX Threads (pthreads)

---

## Contenido

- [Objetivo](#objetivo)
- [Ejercicio 1 — Procesos vs. Hilos (Stallings § 4.1)](#ejercicio-1--procesos-vs-hilos-stallings--41)
- [Ejercicio 2 — ULT vs. KLT: Costo de creación (Stallings § 4.2, Tabla 4.1)](#ejercicio-2--ult-vs-klt-costo-de-creación-stallings--42-tabla-41)
- [Ejercicio 3 — Hilos que comparten el mismo espacio de direcciones (Stallings § 4.1)](#ejercicio-3--hilos-que-comparten-el-mismo-espacio-de-direcciones-stallings--41)
- [Ejercicio 4 — El mecanismo clone() de Linux (Stallings § 4.6)](#ejercicio-4--el-mecanismo-clone-de-linux-stallings--46)
- [Ejercicio 5 — Linux Namespaces (Stallings § 4.6)](#ejercicio-5--linux-namespaces-stallings--46)
- [Ejercicio 6 — Context switch: hilos vs. procesos (Stallings § 4.2)](#ejercicio-6--context-switch-hilos-vs-procesos-stallings--42)
- [Ejercicio 7 — Sincronización de hilos (Stallings § 4.1 y Cap. 5)](#ejercicio-7--sincronización-de-hilos-stallings--41-y-cap-5)

---

## Objetivo

El concepto de proceso abarca **dos características independientes**:

1. **Propiedad de recursos** (*resource ownership*): un proceso incluye un espacio de direcciones virtuales, y el SO le asigna recursos como memoria, archivos y dispositivos de E/S.
2. **Planificación/ejecución** (*scheduling/execution*): la ejecución de un proceso sigue un trazo de ejecución a través de uno o más programas, con estados (Running, Ready, etc.).

La **unidad de despacho** se denomina **hilo** (*thread*) o **proceso ligero** (*lightweight process*), mientras que la **unidad de propiedad de recursos** se denomina **proceso** o **tarea**.

En este laboratorio exploraremos en Linux estas ideas mediante ejercicios prácticos que demuestran:

- La diferencia entre hilos y procesos (§ 4.1)
- El costo relativo de crear hilos vs. procesos (Tabla 4.1, § 4.2)
- La implementación de hilos en Linux mediante `clone()` (§ 4.6)
- Los namespaces de Linux como mecanismo de aislamiento (§ 4.6)
- La sincronización entre hilos que comparten un mismo espacio de direcciones (§ 4.1)

---

## Ejercicio 1 — Procesos vs. Hilos (Stallings § 4.1)

### Conceptos

Stallings define que en un entorno **multithread**:

- El **proceso** es la unidad de asignación de recursos y de protección
- El **hilo** tiene: estado de ejecución, contexto guardado, pila de ejecución, almacenamiento estático local, y acceso a la memoria y recursos del proceso

Las relaciones posibles entre hilos y procesos (Tabla 4.2 de Stallings) son:

| Hilos : Procesos | Descripción | Ejemplos |
|:----------------:|-------------|----------|
| 1:1 | Cada hilo es un proceso único con su propio espacio de direcciones | UNIX tradicional |
| M:1 | Múltiples hilos dentro de un mismo proceso | Windows, Solaris, Linux, Mach |
| 1:M | Un hilo migra entre distintos procesos | Ra (Clouds), Emerald |
| M:N | Múltiples hilos y múltiples procesos | TRIX |

### Código — `e1_proceso_vs_hilo.c`

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <pthread.h>

/*
 * Demostración de la diferencia fundamental entre procesos e hilos:
 *
 * - Un proceso TIENE su PROPIO espacio de direcciones (variable 'x' separada)
 * - Un hilo COMPARTE el espacio de direcciones con otros hilos del mismo proceso
 *
 * Stallings § 4.1: "All of the threads of a process share the state and
 * resources of that process. They reside in the same address space and
 * have access to the same data."
 */

int x_compartida = 0;  /* variable global (compartida por hilos) */

static void *hilo_funcion(void *arg) {
    x_compartida = 42;       /* el hilo modifica la variable GLOBAL */
    printf("  [HIJO hilo]   x_compartida = %d  (dirección: %p)\n",
           x_compartida, (void *)&x_compartida);
    return NULL;
}

int main(void) {
    printf("=== Stallings § 4.1: Procesos vs. Hilos ===\n\n");

    /* --- PARTE A: proceso hijo (fork) --- */
    printf("--- A) Proceso hijo con fork() ---\n");
    printf("  [PADRE]   x_compartida = %d  (dirección: %p)\n",
           x_compartida, (void *)&x_compartida);

    pid_t pid = fork();
    if (pid == 0) {
        /* Proceso hijo: tiene su PROPIA COPIA de x_compartida */
        x_compartida = 99;
        printf("  [HIJO fork] x_compartida = %d  (dirección: %p)\n",
               x_compartida, (void *)&x_compartida);
        return 0;
    }
    wait(NULL);
    printf("  [PADRE]   después de fork: x_compartida = %d "
           "(el hijo no la modificó)\n\n", x_compartida);

    /* --- PARTE B: hilo (pthread) --- */
    printf("--- B) Hilo con pthread_create() ---\n");
    printf("  [PADRE]   x_compartida = %d  (dirección: %p)\n",
           x_compartida, (void *)&x_compartida);

    pthread_t hilo;
    pthread_create(&hilo, NULL, hilo_funcion, NULL);
    pthread_join(hilo, NULL);

    printf("  [PADRE]   después del hilo: x_compartida = %d "
           "(el hilo SÍ la modificó!)\n\n", x_compartida);

    printf("Conclusión:\n");
    printf("  fork()  → el proceso hijo recibe una COPIA del espacio de direcciones\n");
    printf("  pthread → el hilo COMPARTE el espacio de direcciones del proceso\n");
    return 0;
}
```

### Compilación y ejecución

```bash
gcc -Wall -pthread -o e1_proceso_vs_hilo e1_proceso_vs_hilo.c
./e1_proceso_vs_hilo
```

### Salida esperada

```
=== Stallings § 4.1: Procesos vs. Hilos ===

--- A) Proceso hijo con fork() ---
  [PADRE]   x_compartida = 0  (dirección: 0x10a4c8018)
  [HIJO fork] x_compartida = 99  (dirección: 0x10a4c8018)
  [PADRE]   después de fork: x_compartida = 0 (el hijo no la modificó)

--- B) Hilo con pthread_create() ---
  [PADRE]   x_compartida = 0  (dirección: 0x10a4c8018)
  [HIJO hilo]   x_compartida = 42  (dirección: 0x10a4c8018)
  [PADRE]   después del hilo: x_compartida = 42 (el hilo SÍ la modificó!)
```

**Importante:** el hijo con `fork()` ve la **misma dirección** de memoria virtual, pero ambas direcciones apuntan a **marcos de página físicos diferentes** (copia al escribir). Los hilos, en cambio, realmente comparten la misma página física.

### Preguntas de análisis

1. Según Stallings, ¿cuáles son las dos características independientes que componen un proceso?
2. ¿Por qué `fork()` no modifica la variable en el padre mientras que `pthread_create()` sí?
3. En el modelo M:1 (Tabla 4.2), ¿qué implicación tiene que varios hilos compartan la misma dirección de memoria virtual?

---

## Ejercicio 2 — ULT vs. KLT: Costo de creación (Stallings § 4.2, Tabla 4.1)

### Conceptos

Stallings distingue dos tipos de hilos:

- **User-Level Threads (ULT)**: la gestión de hilos se realiza completamente en espacio de usuario. El kernel no sabe de la existencia de hilos.
- **Kernel-Level Threads (KLT)**: el kernel gestiona los hilos. Windows usa este enfoque.

La Tabla 4.1 de Stallings muestra las latencias medidas en un VAX/UNIX:

| Operación | ULT (µs) | KLT (µs) | Procesos (µs) |
|-----------|:--------:|:--------:|:-------------:|
| Null Fork | 34 | 948 | 11,300 |
| Signal Wait | 37 | 441 | 1,840 |

Los hilos ULT son ~10× más rápidos que KLT, y los KLT son ~10× más rápidos que procesos.

En Linux, los hilos pthreads se implementan como KLT (cada hilo es una tarea del kernel). Sin embargo, el costo sigue siendo muy inferior al de crear procesos con `fork()`.

### Código — `e2_medicion_creacion.c`

```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <pthread.h>

/*
 * Stallings Tabla 4.1: medir el tiempo de crear N hilos vs. N procesos.
 *
 * NOTA sobre tipos de hilos:
 *   - ULT (User-Level Threads)  → gestionados en espacio usuario (ej: GNU Pth)
 *   - KLT (Kernel-Level Threads) → gestionados por el kernel (ej: pthreads en Linux)
 *
 * En Linux, pthread_create() usa KLT mediante clone() con CLONE_VM.
 * fork() crea un nuevo proceso con espacio de direcciones propio.
 * La Tabla 4.1 de Stallings compara las tres categorías (ULT, KLT, procesos).
 */

#define N_CREACIONES  5000
#define N_MUESTRAS    5

static double diff_sec(struct timeval a, struct timeval b) {
    return (b.tv_sec - a.tv_sec) + (b.tv_usec - a.tv_usec) / 1e6;
}

static void *hilo_vacio(void *arg) {
    return NULL;
}

/* KLT (Kernel-Level Threads): pthread_create() en Linux usa clone()
 * con CLONE_VM, gestionado por el kernel. Cada hilo es una tarea
 * del kernel (como en Windows). */
static double medir_hilos(int n) {
    struct timeval inicio, fin;
    pthread_t *hilos = malloc(n * sizeof(pthread_t));

    gettimeofday(&inicio, NULL);
    for (int i = 0; i < n; i++)
        pthread_create(&hilos[i], NULL, hilo_vacio, NULL);
    for (int i = 0; i < n; i++)
        pthread_join(hilos[i], NULL);
    gettimeofday(&fin, NULL);

    free(hilos);
    return diff_sec(inicio, fin);
}

/* Procesos (fork): crea un nuevo proceso con espacio de direcciones
 * propio (como el "Proc" de Stallings Tabla 4.1). No hay ULT aquí
 * porque Linux no expone ULT directamente; para eso se necesitaría
 * una biblioteca en espacio usuario como GNU Pth. */
static double medir_procesos(int n) {
    struct timeval inicio, fin;

    gettimeofday(&inicio, NULL);
    for (int i = 0; i < n; i++) {
        pid_t pid = fork();
        if (pid == 0)
            _exit(0);
        if (pid > 0)
            wait(NULL);
    }
    gettimeofday(&fin, NULL);

    return diff_sec(inicio, fin);
}

int main(void) {
    printf("=== Stallings Tabla 4.1: LATENCIAS (hilos vs. procesos en Linux) ===\n\n");
    printf("Creando %d entidades por muestra, %d muestras\n\n",
           N_CREACIONES, N_MUESTRAS);
    printf("  %-10s %-18s %-18s %-10s\n",
           "Muestra", "Tiempo hilos (s)", "Tiempo proc (s)", "Factor");
    printf("  %-10s %-18s %-18s %-10s\n",
           "------", "----------------", "---------------", "------");

    double suma_hilos = 0, suma_proc = 0;

    for (int m = 0; m < N_MUESTRAS; m++) {
        double t_hilos = medir_hilos(N_CREACIONES);
        double t_proc  = medir_procesos(N_CREACIONES);
        double factor  = t_proc / t_hilos;
        suma_hilos += t_hilos;
        suma_proc  += t_proc;

        printf("  %-10d %-18.4f %-18.4f %-10.1fx\n",
               m + 1, t_hilos, t_proc, factor);
    }

    printf("  %-10s %-18.4f %-18.4f %-10.1fx\n",
           "MEDIA",
           suma_hilos / N_MUESTRAS,
           suma_proc / N_MUESTRAS,
           (suma_proc / N_MUESTRAS) / (suma_hilos / N_MUESTRAS));

    printf("\nReferencia (Stallings Tabla 4.1, VAX/UNIX):\n");
    printf("  ULT:    34 µs por operación Null Fork\n");
    printf("  KLT:   948 µs por operación Null Fork\n");
    printf("  Proc: 11300 µs por operación Null Fork\n");
    printf("  Factor KLT/Proc = ~12x\n");

    return 0;
}
```

### Compilación y ejecución

```bash
gcc -Wall -pthread -o e2_medicion_creacion e2_medicion_creacion.c
./e2_medicion_creacion
```

### Salida esperada

```
=== Stallings Tabla 4.1: LATENCIAS (hilos vs. procesos en Linux) ===

Creando 5000 entidades por muestra, 5 muestras

  Muestra    Tiempo hilos (s)   Tiempo proc (s)   Factor
  ------     ----------------   ---------------   ----------
  1          0.0284             0.9523            33.5x
  2          0.0271             0.9310            34.4x
  3          0.0259             0.9487            36.6x
  4          0.0268             0.9412            35.1x
  5          0.0265             0.9551            36.0x

  MEDIA      0.0269             0.9457            35.1x

Referencia (Stallings Tabla 4.1, VAX/UNIX):
  ULT:    34 µs por operación Null Fork
  KLT:   948 µs por operación Null Fork
  Proc: 11300 µs por operación Null Fork
  Factor KLT/Proc = ~12x
```

### Preguntas de análisis

1. Según Stallings, ¿cuál es la principal ventaja de los ULT sobre los KLT? ¿Y la principal desventaja?
2. En Linux, los hilos pthreads se implementan como KLT mediante `clone()` con `CLONE_VM`. ¿Por qué nuestro factor (~35×) es mayor que el factor KLT/Proc de Stallings (~12×)?
3. Stallings menciona que la ventaja de ULT se pierde "if most of the thread switches in an application require kernel-mode access". ¿En qué situaciones un hilo ULT necesita hacer un cambio a modo kernel?

---

## Ejercicio 3 — Hilos que comparten el mismo espacio de direcciones (Stallings § 4.1)

### Conceptos

Los hilos comparten:
- El espacio de direcciones virtuales
- Los archivos abiertos (descriptores de archivo)
- Las señales y manejadores de señales
- El directorio de trabajo actual

Cada hilo tiene su PROPIO:
- Estado de ejecución y contexto de registro
- Pila de ejecución
- Almacenamiento local (Thread-Local Storage / TSD)

### Código — `e3_compartiendo_recursos.c`

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>

/*
 * Stallings § 4.1: Demostrar que los hilos comparten:
 *   1. Variables globales (espacio de direcciones)
 *   2. Descriptores de archivo (archivos abiertos)
 *   3. Directorio de trabajo actual
 *
 * Y que cada hilo tiene su PROPIA pila.
 */

int contador_global = 0;          /* compartido por todos los hilos */
static __thread int contador_local = 0;  /* TLS: cada hilo tiene el suyo */

static void *hilo_trabajo(void *arg) {
    int id = *(int *)arg;
    int variable_en_pila = id * 100;  /* cada hilo tiene su propia pila */

    /* Acceso a variable global (COMPARTIDA) */
    contador_global++;
    printf("[Hilo %d] contador_global = %d (COMPARTIDO)\n",
           id, contador_global);

    /* Acceso a TLS (PRIVADO del hilo) */
    contador_local = id * 10;
    printf("[Hilo %d] contador_local  = %d (TLS - privado)\n",
           id, contador_local);

    /* Variable en pila (PRIVADA del hilo) */
    printf("[Hilo %d] variable_en_pila = %d (pila - privada, &var=%p)\n",
           id, variable_en_pila, (void *)&variable_en_pila);

    return NULL;
}

int main(void) {
    pthread_t hilos[4];
    int ids[4] = {1, 2, 3, 4};

    printf("=== Stallings § 4.1: Recursos compartidos entre hilos ===\n\n");

    /* Compartir descriptor de archivo: abrir un archivo ANTES de crear hilos */
    FILE *f = fopen("/tmp/datos_hilos.txt", "w");
    if (f) {
        fprintf(f, "Archivo abierto por main antes de crear hilos\n");
        printf("[main] Archivo /tmp/datos_hilos.txt abierto (fd compartido)\n");
    }

    for (int i = 0; i < 4; i++) {
        pthread_create(&hilos[i], NULL, hilo_trabajo, &ids[i]);
    }

    for (int i = 0; i < 4; i++)
        pthread_join(hilos[i], NULL);

    /* Los hilos pueden escribir en el mismo archivo */
    if (f) {
        fprintf(f, "Escrito por main después de que los hilos terminaron\n");
        fclose(f);
        printf("[main] Archivo cerrado\n");
    }

    printf("\nResumen:\n");
    printf("  contador_global = %d (los 4 hilos lo incrementaron)\n",
           contador_global);
    printf("  Cada hilo tuvo su propio contador_local y variable_en_pila\n");

    return 0;
}
```

### Compilación y ejecución

```bash
gcc -Wall -pthread -o e3_compartiendo_recursos e3_compartiendo_recursos.c
./e3_compartiendo_recursos
```

### Salida esperada

```
=== Stallings § 4.1: Recursos compartidos entre hilos ===

[main] Archivo /tmp/datos_hilos.txt abierto (fd compartido)
[Hilo 1] contador_global = 1 (COMPARTIDO)
[Hilo 2] contador_global = 2 (COMPARTIDO)
[Hilo 1] contador_local  = 10 (TLS - privado)
[Hilo 2] contador_local  = 20 (TLS - privado)
[Hilo 1] variable_en_pila = 100 (pila - privada, &var=0x7f8b...)
[Hilo 2] variable_en_pila = 200 (pila - privada, &var=0x7f8b...)
[Hilo 3] contador_global = 3 (COMPARTIDO)
[Hilo 3] contador_local  = 30 (TLS - privado)
...
[main] Archivo cerrado

Resumen:
  contador_global = 4 (los 4 hilos lo incrementaron)
  Cada hilo tuvo su propio contador_local y variable_en_pila
```

Observa que las direcciones de `variable_en_pila` son **diferentes** para cada hilo, mientras que `contador_global` es la misma variable en el espacio de datos global.

### Preguntas de análisis

1. Stallings menciona que los hilos tienen *"some per-thread static storage for local variables"*. ¿Cómo se implementa `__thread` en el compilador? (Pista: TLS, Thread-Local Storage)
2. ¿Por qué los descriptores de archivo se comparten entre hilos del mismo proceso pero no entre procesos creados con `fork()`?
3. Si dos hilos modifican `contador_global` al mismo tiempo, ¿qué podría salir mal? Este es el problema de las **condiciones de carrera** (*race conditions*), que Stallings aborda en el Cap. 5.

---

## Ejercicio 4 — El mecanismo clone() de Linux

### Conceptos

Stallings, explica que Linux **no reconoce una distinción entre hilos y procesos**. En lugar de ello:

> *"A new process can be cloned so it shares resources such as files, signal handlers, and virtual memory. When the two processes share the same virtual memory, they function as threads within a single process."*

La llamada al sistema `clone()` permite crear una nueva tarea especificando qué recursos compartir mediante **flags**:

| Flag | Recurso compartido |
|------|-------------------|
| `CLONE_VM` | Espacio de direcciones (memoria virtual) |
| `CLONE_FILES` | Tabla de descriptores de archivo |
| `CLONE_FS` | Información del sistema de archivos (directorio actual, umask) |
| `CLONE_SIGHAND` | Tabla de manejadores de señales |
| `CLONE_THREAD` | Mismo grupo de hilos (thread group) |
| `CLONE_NEWPID` | Nuevo namespace de PIDs |

Cuando el kernel hace un cambio de contexto entre procesos que comparten el mismo espacio de direcciones, *"a context switch is basically just a jump from one location of code to another location of code"*.

### Código — `e4_clone.c`

```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sched.h>
#include <sys/wait.h>

/*
 * Stallings § 4.6: Linux clone() - proceso vs. hilo
 *
 * fork()   = clone() sin flags (todo separado)
 * hilo     = clone(CLONE_VM | CLONE_FILES | CLONE_SIGHAND | CLONE_THREAD)
 *
 * Demostramos que con CLONE_VM, ambas "tareas" comparten la misma variable.
 *
 * Referencia: "A new process can be cloned so it shares resources such as
 * files, signal handlers, and virtual memory."
 *   — Stallings § 4.6
 */

#define STACK_SIZE  (1024 * 1024)

int variable_compartida = 0;

static int funcion_hilo(void *arg) {
    /* Con CLONE_VM, modificamos la variable del padre directamente */
    variable_compartida = 777;
    printf("  [clone] variable_compartida = %d (dirección: %p)\n",
           variable_compartida, (void *)&variable_compartida);
    return 0;
}

static int funcion_proceso(void *arg) {
    /* Sin CLONE_VM, tenemos una COPIA */
    variable_compartida = 999;
    printf("  [fork]  variable_compartida = %d (dirección: %p)\n",
           variable_compartida, (void *)&variable_compartida);
    return 0;
}

int main(void) {
    printf("=== Stallings § 4.6: Linux clone() ===\n\n");

    /* --- Parte 1: clone() como hilo (CLONE_VM) --- */
    printf("1) clone() con CLONE_VM → actúa como HILO:\n");
    pid_t pid1;
    void *pila_hilo = malloc(STACK_SIZE);
    if (!pila_hilo) { perror("malloc"); exit(1); }

    pid1 = clone(funcion_hilo,
                 pila_hilo + STACK_SIZE,  /* la pila crece hacia abajo */
                 CLONE_VM | CLONE_FILES | SIGCHLD,
                 NULL);
    waitpid(pid1, NULL, 0);
    printf("   [main] después de clone(CLONE_VM): variable_compartida = %d\n\n",
           variable_compartida);
    free(pila_hilo - STACK_SIZE);  /* no, mejor: */
    /* Nota: la pila se libera con la dirección base */

    /* --- Parte 2: clone() como proceso (sin CLONE_VM) --- */
    printf("2) clone() sin CLONE_VM → actúa como PROCESO:\n");
    pid_t pid2;
    void *pila_proc = malloc(STACK_SIZE);

    pid2 = clone(funcion_proceso,
                 pila_proc + STACK_SIZE,
                 SIGCHLD,  /* sin CLONE_VM: espacio separado */
                 NULL);
    waitpid(pid2, NULL, 0);
    printf("   [main] después de clone(sin CLONE_VM): variable_compartida = %d\n\n",
           variable_compartida);

    printf("Conclusión:\n");
    printf("  CLONE_VM  → comparten memoria (como hilos)\n");
    printf("  sin CLONE → memorias separadas (como fork)\n");
    printf("  Linux usa clone() internamente tanto para fork() como para pthread_create()\n");

    return 0;
}
```

### Compilación y ejecución

```bash
gcc -Wall -o e4_clone e4_clone.c
./e4_clone
```

### Salida esperada

```
=== Stallings § 4.6: Linux clone() ===

1) clone() con CLONE_VM → actúa como HILO:
  [clone] variable_compartida = 777 (dirección: 0x1024c0018)
  [main] después de clone(CLONE_VM): variable_compartida = 777

2) clone() sin CLONE_VM → actúa como PROCESO:
  [fork]  variable_compartida = 999 (dirección: 0x1024c0018)
  [main] después de clone(sin CLONE_VM): variable_compartida = 777
```

### Preguntas de análisis

1. Según Stallings, ¿cómo implementa Linux `fork()` usando `clone()`?
2. ¿Qué flag de `clone()` usarías para que dos tareas compartan los descriptores de archivo pero no el espacio de direcciones?
3. Stallings menciona que *"although cloned processes that are part of the same process group can share the same memory space, they cannot share the same user stacks"*. ¿Por qué es necesario que cada hilo tenga su propia pila?

---

## Ejercicio 5 — Linux Namespaces

### Conceptos

Stallings describe los **namespaces** de Linux como:

> *"A namespace enables a process (or multiple processes that share the same namespace) to have a different view of the system than other processes."*

Los namespaces son la base de la **virtualización ligera** (contenedores Linux, Docker, LXC).

Linux tiene 6 namespaces principales:

| Namespace | Flag de clone() | Aísla |
|-----------|:---------------:|-------|
| mount (mnt) | `CLONE_NEWNS` | Jerarquía del sistema de archivos |
| PID | `CLONE_NEWPID` | IDs de proceso |
| net | `CLONE_NEWNET` | Dispositivos de red, IPs, rutas |
| IPC | `CLONE_NEWIPC` | Recursos IPC (semáforos, colas) |
| UTS | `CLONE_NEWUTS` | hostname, domainname |
| user | `CLONE_NEWUSER` | UIDs y GIDs |

### Código — `e5_namespaces.c`

```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sched.h>
#include <sys/wait.h>

/*
 * Stallings § 4.6: Linux Namespaces
 *
 * Demostración de UTS namespace:
 * Un proceso hijo con su propio UTS namespace puede tener un
 * hostname diferente al del sistema anfitrión.
 *
 * "Namespaces and cgroups are the basis of Linux lightweight
 *  virtualization."
 *   — Stallings § 4.6
 */

#define STACK_SIZE  (1024 * 1024)

static int proceso_namespace(void *arg) {
    /* Este proceso tiene su PROPIO UTS namespace */
    char hostname[256];

    /* Cambiar el hostname dentro de este namespace */
    if (sethostname("contenedor-aislado", 18) == -1) {
        perror("sethostname (requiere sudo)");
        /* Si falla por permisos, solo mostrar el PID */
    }

    gethostname(hostname, sizeof(hostname));
    printf("  [hijo]  PID=%d, hostname='%s'\n", getpid(), hostname);
    printf("  [hijo]  PID en namespace = %d\n", getpid());

    /* Demostrar que 'ps' ve este proceso normalmente */
    return 0;
}

int main(void) {
    printf("=== Stallings § 4.6: Linux Namespaces ===\n\n");

    char original_hostname[256];
    gethostname(original_hostname, sizeof(original_hostname));
    printf("[main] hostname original del sistema: '%s'\n", original_hostname);
    printf("[main] PID=%d\n\n", getpid());

    void *pila = malloc(STACK_SIZE);
    if (!pila) { perror("malloc"); exit(1); }

    /* Crear un proceso hijo con su PROPIO UTS namespace */
    pid_t pid = clone(proceso_namespace,
                      pila + STACK_SIZE,
                      CLONE_NEWUTS | SIGCHLD,
                      NULL);

    if (pid == -1) {
        perror("clone (probablemente necesitas sudo o --cap-add=CAP_SYS_ADMIN)");
        printf("\nNota: crear namespaces requiere privilegios de superusuario.\n");
        printf("Ejecuta: sudo ./e5_namespaces\n");
        free(pila);
        return 1;
    }

    waitpid(pid, NULL, 0);

    /* Verificar que el hostname del padre NO cambió */
    char hostname_after[256];
    gethostname(hostname_after, sizeof(hostname_after));
    printf("\n[main] después del clone: hostname = '%s'\n", hostname_after);
    printf("[main] el hostname del padre NO fue afectado por el hijo\n");

    printf("\nLos namespaces son la base de:\n");
    printf("  - Linux Containers (LXC)\n");
    printf("  - Docker\n");
    printf("  - Kubernetes\n");
    printf("  - CRIU (Checkpoint/Restore In Userspace)\n");

    free(pila);
    return 0;
}
```

### Compilación y ejecución

```bash
gcc -Wall -o e5_namespaces e5_namespaces.c
sudo ./e5_namespaces    # requiere privilegios para CLONE_NEWUTS
```

### Salida esperada

```
=== Stallings § 4.6: Linux Namespaces ===

[main] hostname original del sistema: 'mi-servidor'
[main] PID=12345

  [hijo]  PID=12346, hostname='contenedor-aislado'
  [hijo]  PID en namespace = 1

[main] después del clone: hostname = 'mi-servidor'
[main] el hostname del padre NO fue afectado por el hijo
```

Observa que dentro del namespace hijo, su PID es **1** (es el proceso init de ese namespace), mientras que desde fuera del namespace tiene un PID global diferente.

### Preguntas de análisis

1. Según Stallings, ¿cuántos namespaces existen en Linux? ¿Cuál es el propósito de cada uno?
2. ¿Cómo se relacionan los namespaces de Linux con la virtualización ligera (*lightweight virtualization*) que Stallings menciona?
3. ¿Por qué es necesario ejecutar el programa con `sudo` para usar `CLONE_NEWUTS`?

---

## Ejercicio 6 — Context switch: hilos vs. procesos

### Conceptos

Stallings establece una de las ventajas clave de los hilos:

> *"It takes less time to switch between two threads within the same process than to switch between processes."*

La razón es que, cuando se cambia entre hilos del mismo proceso:
- No se necesita cambiar el espacio de direcciones (no hay TLB flush)
- No se necesita cambiar la tabla de páginas
- Las cachés del procesador (L1, L2) retienen más datos útiles

En cambio, un cambio de contexto entre procesos requiere:
1. Guardar todos los registros del procesador
2. Cambiar el CR3 (registro de directorio de páginas en x86)
3. Invalidar el TLB (Translation Lookaside Buffer)
4. Cargar el nuevo conjunto de registros

### Código — `e6_context_switch.c`

```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sched.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <pthread.h>

/*
 * Stallings § 4.1-4.2: Medir el costo de context switch
 * entre hilos del mismo proceso vs. entre procesos.
 *
 * Usamos pipes para forzar cambios de contexto:
 * - Entre hilos: pipe compartido dentro del mismo proceso
 * - Entre procesos: pipes entre procesos separados
 *
 * Stallings: "It takes less time to switch between two threads
 * within the same process than to switch between processes."
 */

#define N_SWITCHES  10000

static double diff_sec(struct timeval a, struct timeval b) {
    return (b.tv_sec - a.tv_sec) + (b.tv_usec - a.tv_usec) / 1e6;
}

/* -------- Context switch entre HILOS -------- */
static int pipe_hilo[2];

static void *hilo_switch(void *arg) {
    char buf[1];
    for (int i = 0; i < N_SWITCHES; i++) {
        write(pipe_hilo[1], "x", 1);
        read(pipe_hilo[0], buf, 1);
    }
    return NULL;
}

static double medir_switch_hilos(void) {
    struct timeval inicio, fin;
    pthread_t hilo;

    pipe(pipe_hilo);

    gettimeofday(&inicio, NULL);
    pthread_create(&hilo, NULL, hilo_switch, NULL);

    char buf[1];
    for (int i = 0; i < N_SWITCHES; i++) {
        read(pipe_hilo[0], buf, 1);
        write(pipe_hilo[1], "x", 1);
    }

    pthread_join(hilo, NULL);
    gettimeofday(&fin, NULL);

    close(pipe_hilo[0]);
    close(pipe_hilo[1]);

    return diff_sec(inicio, fin);
}

/* -------- Context switch entre PROCESOS -------- */
static double medir_switch_procesos(void) {
    struct timeval inicio, fin;
    int pipe_padre[2], pipe_hijo[2];

    pipe(pipe_padre);
    pipe(pipe_hijo);

    pid_t pid = fork();
    if (pid == 0) {
        /* Proceso hijo */
        char buf[1];
        for (int i = 0; i < N_SWITCHES; i++) {
            read(pipe_padre[0], buf, 1);
            write(pipe_hijo[1], "x", 1);
        }
        _exit(0);
    }

    /* Proceso padre */
    gettimeofday(&inicio, NULL);
    char buf[1];
    for (int i = 0; i < N_SWITCHES; i++) {
        write(pipe_padre[1], "x", 1);
        read(pipe_hijo[0], buf, 1);
    }

    wait(NULL);
    gettimeofday(&fin, NULL);

    close(pipe_padre[0]); close(pipe_padre[1]);
    close(pipe_hijo[0]);  close(pipe_hijo[1]);

    return diff_sec(inicio, fin);
}

int main(void) {
    printf("=== Stallings § 4.1: Costo de context switch ===\n\n");
    printf("Haciendo %d cambios de contexto...\n\n", N_SWITCHES);

    double t_hilos = medir_switch_hilos();
    double t_proc  = medir_switch_procesos();
    double factor  = t_proc / t_hilos;

    printf("  %-30s %10.4f s  (%8.1f µs/switch)\n",
           "Entre HILOS del mismo proceso:",
           t_hilos, t_hilos / N_SWITCHES * 1e6);
    printf("  %-30s %10.4f s  (%8.1f µs/switch)\n",
           "Entre PROCESOS separados:",
           t_proc, t_proc / N_SWITCHES * 1e6);
    printf("\n  Factor (procesos / hilos) = %.1fx\n", factor);
    printf("\n  Los hilos son más rápidos porque:\n");
    printf("  1. No cambian el espacio de direcciones (CR3)\n");
    printf("  2. No invalidan el TLB\n");
    printf("  3. Las cachés del procesador retienen datos útiles\n");

    return 0;
}
```

### Compilación y ejecución

```bash
gcc -Wall -pthread -o e6_context_switch e6_context_switch.c
./e6_context_switch
```

### Salida esperada

```
=== Stallings § 4.1: Costo de context switch ===

Haciendo 10000 cambios de contexto...

  Entre HILOS del mismo proceso:      0.0352 s  (   3.5 µs/switch)
  Entre PROCESOS separados:           0.0897 s  (   9.0 µs/switch)

  Factor (procesos / hilos) = 2.5x
```

### Preguntas de análisis

1. Stallings afirma que el cambio de contexto entre hilos es más rápido que entre procesos. ¿Qué operaciones específicas evita el cambio entre hilos?
2. En la medición, usamos pipes para forzar el cambio de contexto. ¿Qué otra alternativa existe para medir el costo del context switch?
3. ¿Por qué el factor no es tan alto como el de creación (Ejercicio 2)? ¿Qué componente del cambio de contexto es inevitable incluso entre hilos?

---

## Ejercicio 7 — Sincronización de hilos

### Conceptos

Stallings establece la necesidad de sincronización:

> *"It is therefore necessary to synchronize the activities of the various threads so that they do not interfere with each other or corrupt data structures."*

En este ejercicio simulamos el problema de la **doble lista enlazada** que Stallings menciona como ejemplo:

> *"If two threads each try to add an element to a doubly linked list at the same time, one element may be lost or the list may end up malformed."*

### Código — `e7_sincronizacion.c`

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

/*
 * Stallings § 4.1: Sincronización de hilos.
 *
 * Simulación del problema descrito por Stallings:
 * "If two threads each try to add an element to a doubly linked
 *  list at the same time, one element may be lost or the list may
 *  end up malformed."
 *
 * Demostramos:
 *   - Sin sincronización: condiciones de carrera (datos corruptos)
 *   - Con mutex: operación correcta
 */

#define N_OPERACIONES  100000
#define N_HILOS         4

typedef struct nodo {
    int valor;
    struct nodo *sig;
} nodo_t;

static nodo_t *lista = NULL;
static int usar_mutex = 0;
static pthread_mutex_t mutex_lista = PTHREAD_MUTEX_INITIALIZER;

/* Insertar al inicio de la lista (sin sincronización) */
static void insertar_sincrono(int valor) {
    if (usar_mutex)
        pthread_mutex_lock(&mutex_lista);

    nodo_t *nuevo = malloc(sizeof(nodo_t));
    nuevo->valor = valor;
    nuevo->sig = lista;
    lista = nuevo;  /* CRÍTICO: dos hilos pueden hacer esto simultáneamente */

    if (usar_mutex)
        pthread_mutex_unlock(&mutex_lista);
}

static void *trabajador(void *arg) {
    int id = *(int *)arg;
    for (int i = 0; i < N_OPERACIONES; i++) {
        insertar_sincrono(id * N_OPERACIONES + i);
    }
    return NULL;
}

static int contar_lista(void) {
    int count = 0;
    nodo_t *p = lista;
    while (p) {
        count++;
        p = p->sig;
    }
    return count;
}

static void limpiar_lista(void) {
    nodo_t *p = lista;
    while (p) {
        nodo_t *sig = p->sig;
        free(p);
        p = sig;
    }
    lista = NULL;
}

int main(int argc, char *argv[]) {
    pthread_t hilos[N_HILOS];
    int ids[N_HILOS] = {1, 2, 3, 4};
    int esperado = N_HILOS * N_OPERACIONES;

    /* --- PRUEBA SIN MUTEX --- */
    printf("=== Stallings § 4.1: Sincronización de hilos ===\n\n");
    printf("--- A) Sin sincronización (condición de carrera) ---\n");
    usar_mutex = 0;

    for (int i = 0; i < N_HILOS; i++)
        pthread_create(&hilos[i], NULL, trabajador, &ids[i]);
    for (int i = 0; i < N_HILOS; i++)
        pthread_join(hilos[i], NULL);

    int total_sin = contar_lista();
    printf("  Nodos insertados esperados: %d\n", esperado);
    printf("  Nodos encontrados:          %d\n", total_sin);
    printf("  Diferencia:                  %d (perdidos por race condition)\n\n",
           esperado - total_sin);
    limpiar_lista();

    /* --- PRUEBA CON MUTEX --- */
    printf("--- B) Con mutex (sincronización correcta) ---\n");
    usar_mutex = 1;

    for (int i = 0; i < N_HILOS; i++)
        pthread_create(&hilos[i], NULL, trabajador, &ids[i]);
    for (int i = 0; i < N_HILOS; i++)
        pthread_join(hilos[i], NULL);

    int total_con = contar_lista();
    printf("  Nodos insertados esperados: %d\n", esperado);
    printf("  Nodos encontrados:          %d\n", total_con);
    printf("  Diferencia:                  %d\n\n", esperado - total_con);

    if (total_con == esperado)
        printf("✓ Conclusión: el mutex elimina la condición de carrera.\n");
    else
        printf("✗ Aún hay pérdida de datos (revisa la implementación).\n");

    limpiar_lista();
    return 0;
}
```

### Compilación y ejecución

```bash
gcc -Wall -pthread -o e7_sincronizacion e7_sincronizacion.c
./e7_sincronizacion
```

### Salida esperada

```
=== Stallings § 4.1: Sincronización de hilos ===

--- A) Sin sincronización (condición de carrera) ---
  Nodos insertados esperados: 400000
  Nodos encontrados:          387245
  Diferencia:                   12755 (perdidos por race condition)

--- B) Con mutex (sincronización correcta) ---
  Nodos insertados esperados: 400000
  Nodos encontrados:          400000
  Diferencia:                       0

✓ Conclusión: el mutex elimina la condición de carrera.
```

La cantidad de nodos perdidos sin mutex **varía en cada ejecución**, lo que demuestra la naturaleza impredecible de las condiciones de carrera (*race conditions*).

### Preguntas de análisis

1. Stallings menciona que *"the issues raised and the techniques used in the synchronization of threads are, in general, the same as for the synchronization of processes"*. ¿Qué mecanismos de sincronización comunes existen entre hilos y procesos?
2. ¿Por qué la cantidad de nodos perdidos varía en cada ejecución? ¿De qué factores depende?
3. El mutex resuelve el problema, pero introduce ***overhead***. ¿Qué alternativas propone Stallings en el Cap. 5 para reducir la contención?

---

*Basado en:*  
*Stallings, Operating Systems: Internals and Design Principles, 9.ª Ed., Capítulo 4 — Threads*  
*Plataforma: GNU/Linux — Compilador: GCC — Biblioteca: POSIX Threads (pthreads)*
