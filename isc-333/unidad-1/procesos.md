# Procesos en Sistemas Operativos

**Tanenbaum & Bos · Modern Operating Systems, Cap. 2**  
**William Stallings · Operating Systems: Internals and Design Principles, 9ª Ed., Cap. 3**

---

## Contenido

- [2.1 ¿Qué es un Proceso?](#21-qué-es-un-proceso)
- [2.2 El Modelo de Proceso](#22-el-modelo-de-proceso)
- [2.3 Estados de un Proceso](#23-estados-de-un-proceso)
  - [2.3.1 Modelo de Dos Estados](#231-modelo-de-dos-estados)
  - [2.3.2 Modelo de Tres Estados](#232-modelo-de-tres-estados)
  - [2.3.3 Modelo de Cinco Estados](#233-modelo-de-cinco-estados)
  - [2.3.4 Procesos Suspendidos — Modelo de Siete Estados](#234-procesos-suspendidos--modelo-de-siete-estados)
- [2.4 Descripción de Procesos](#24-descripción-de-procesos)
  - [2.4.1 Tablas del Sistema Operativo](#241-tablas-del-sistema-operativo)
  - [2.4.2 La Imagen del Proceso](#242-la-imagen-del-proceso)
  - [2.4.3 El Bloque de Control del Proceso (PCB)](#243-el-bloque-de-control-del-proceso-pcb)
- [2.5 Modos de Ejecución](#25-modos-de-ejecución)
- [2.6 Creación de Procesos](#26-creación-de-procesos)
- [2.7 Terminación de Procesos](#27-terminación-de-procesos)
- [2.8 Jerarquías de Procesos](#28-jerarquías-de-procesos)
- [2.9 Control de Procesos — Conmutación](#29-control-de-procesos--conmutación)
  - [2.9.1 Mecanismos que Ceden el Control al SO](#291-mecanismos-que-ceden-el-control-al-so)
  - [2.9.2 Cambio de Modo vs. Cambio de Proceso](#292-cambio-de-modo-vs-cambio-de-proceso)
  - [2.9.3 Pasos de una Conmutación Completa](#293-pasos-de-una-conmutación-completa)
- [2.10 Threads (Hilos de Ejecución)](#210-threads-hilos-de-ejecución)
  - [2.10.1 ¿Por qué Usar Threads?](#2101-por-qué-usar-threads)
  - [2.10.2 El Modelo Clásico de Threads](#2102-el-modelo-clásico-de-threads)
  - [2.10.3 Implementación en Espacio de Usuario (ULT)](#2103-implementación-en-espacio-de-usuario-ult)
  - [2.10.4 Implementación en el Kernel (KLT)](#2104-implementación-en-el-kernel-klt)
- [2.11 Procesos en UNIX SVR4](#211-procesos-en-unix-svr4)
- [2.12 Resumen del Capítulo](#212-resumen-del-capítulo)

---

## 2.1 ¿Qué es un Proceso?

Un **proceso** es un programa en ejecución. Más precisamente, es la instancia de un programa junto con los valores actuales del contador de programa, registros del procesador y variables en un momento dado.

> *"Conceptualmente, cada proceso tiene su propia CPU virtual. En la realidad, la CPU física alterna entre procesos — esto se denomina **multiprogramación**."*  
> — Tanenbaum & Bos

La distinción fundamental es:

| Concepto | Naturaleza | Analogía |
|----------|------------|----------|
| **Programa** | Entidad estática (código en disco) | La receta de cocina |
| **Proceso** | Entidad dinámica (programa + estado de ejecución) | La actividad de cocinar |

Un mismo programa puede dar lugar a **múltiples procesos independientes** simultáneamente (por ejemplo, dos usuarios ejecutando el mismo editor de texto).

### Traza de un Proceso

La **traza** (*instruction trace*) de un proceso es la secuencia de instrucciones que se ejecutan para ese proceso. El comportamiento del procesador puede describirse mostrando cómo se **intercalan** las trazas de los distintos procesos.

El **dispatcher** es el pequeño módulo del SO encargado de alternar el procesador entre los procesos listos.

---

## 2.2 El Modelo de Proceso

En un sistema con una sola CPU, en cualquier instante **solo un proceso ejecuta físicamente**. Sin embargo, la conmutación rápida entre procesos crea la **ilusión de paralelismo** — llamada **pseudoparalelismo**. El paralelismo real (hardware) requiere múltiples CPUs o núcleos.

```
Proceso A  ███░░░░░░███░░░░░░███
Proceso B  ░░░███░░░░░░███░░░░░░
Proceso C  ░░░░░░███░░░░░░███░░░

           ──────────────────────▶ Tiempo
           (la CPU alterna entre procesos)
```

Cada proceso tiene su propia **CPU virtual** con:
- Su **contador de programa** (PC) privado
- Sus **registros** propios
- Su **pila** (stack)
- Sus **variables** y espacio de memoria

Cuando se reanuda un proceso, su PC y registros se restauran exactamente al estado en que estaban cuando fue interrumpido.

---

## 2.3 Estados de un Proceso

### 2.3.1 Modelo de Dos Estados

El modelo más simple. Un proceso puede estar en uno de dos estados:

| Estado | Descripción |
|--------|-------------|
| **Running** (Ejecutando) | El proceso está usando la CPU actualmente |
| **Not Running** (No ejecutando) | El proceso espera su turno en una cola |

```
         despacho
Not Running ──────────────▶ Running
    ▲                           │
    └───────────────────────────┘
           pausa / espera
```

**Limitación:** este modelo no distingue entre procesos que esperan E/S (bloqueados, *no pueden* ejecutar) y procesos listos para ejecutar (*pueden* ejecutar). Esto lleva al modelo de cinco estados.

---

### 2.3.2 Modelo de Tres Estados

Tanenbaum presenta tres estados principales que capturan las situaciones fundamentales de un proceso:

| Estado | Descripción |
|--------|-------------|
| **Running** (Ejecutando) | Usando la CPU en este instante |
| **Ready** (Listo) | Ejecutable, detenido temporalmente mientras otro proceso usa la CPU |
| **Blocked** (Bloqueado) | Incapaz de ejecutar hasta que ocurra un evento externo (E/S completada, señal, etc.) |

```
              ┌────────────────────┐
              │                    │ 1. El proceso se bloquea
              ▼                    │    esperando entrada/evento
          [Blocked] ─────────── [Running]
              │                    │
              │ 4. El evento    2. │ El scheduler selecciona
              │    ocurre          │ otro proceso (preempción)
              ▼                    ▼
           [Ready] ──────────▶ [Running]
                    3. El scheduler
                       selecciona este proceso
```

**Transiciones:**

| # | Transición | Causa |
|---|-----------|-------|
| 1 | Running → Blocked | El proceso solicita E/S o espera un evento |
| 2 | Running → Ready | El planificador desaloja el proceso (preempción por tiempo) |
| 3 | Ready → Running | El planificador selecciona este proceso |
| 4 | Blocked → Ready | El evento esperado ocurre (E/S completa, señal recibida) |

> La transición 2 es causada por el **planificador** (decisión del SO). Las transiciones 1 y 4 son causadas por el **proceso mismo** o por eventos externos.

---

### 2.3.3 Modelo de Cinco Estados

Stallings amplía el modelo para incluir la **creación** y **terminación** explícita de procesos:

| Estado | Descripción |
|--------|-------------|
| **New** (Nuevo) | El proceso acaba de ser creado; aún no está listo para ejecutar |
| **Ready** (Listo) | Preparado para ejecutar en cuanto el procesador esté disponible |
| **Running** (Ejecutando) | Actualmente siendo ejecutado por el procesador |
| **Blocked/Waiting** (Bloqueado) | No puede continuar hasta que ocurra algún evento (E/S, señal) |
| **Exit** (Terminado) | Ha terminado o fue abortado; liberado del conjunto de procesos ejecutables |

```
                    ┌──────────────────────────────────┐
                    │          admisión                 │
  [New] ─────────▶ [Ready] ──────────────▶ [Running] ──┤
                     ▲                        │  │      │
                     │     tiempo agotado     │  │      │
                     └────────────────────────┘  │      ▼
                                                 │   [Exit]
                     ┌───────────────────────────┘
                     │  solicita evento / E/S
                     ▼
                  [Blocked]
                     │
                     │  evento ocurre
                     └──────────────▶ [Ready]
```

---

### 2.3.4 Procesos Suspendidos — Modelo de Siete Estados

**Problema:** con solo cinco estados, si todos los procesos están bloqueados esperando E/S, la CPU queda ociosa aunque podría estar haciendo trabajo útil.

**Solución — Swapping:** mover procesos de la memoria principal al disco (*swap out*), liberando espacio para cargar otros procesos. Un proceso movido al disco se llama **suspendido**.

Esto introduce dos nuevos estados:

| Estado | Descripción |
|--------|-------------|
| **Ready/Suspend** | El proceso está en disco pero listo para ejecutar cuando sea cargado a memoria |
| **Blocked/Suspend** | El proceso está en disco *y además* espera un evento |

```
                        swap out
         [Ready] ─────────────────────▶ [Ready/Suspend]
            ▲                                  │
            │ swap in                          │ evento
            │                                 ▼
         [Blocked] ───────────────▶ [Blocked/Suspend]
                     swap out
```

**Razones para suspender un proceso:**

| Razón | Descripción |
|-------|-------------|
| **Swapping** | El SO necesita liberar memoria para traer otro proceso |
| **Solicitud interactiva** | El usuario quiere depurar o pausar su programa |
| **Temporización** | Proceso periódico suspendido entre intervalos |
| **Solicitud del padre** | El proceso padre suspende a un descendiente para examinarlo |
| **Auditoría del SO** | Un proceso de monitoreo se suspende temporalmente |

**Características de un proceso suspendido:**
1. No está disponible inmediatamente para ejecución.
2. Puede o no estar esperando un evento (independiente del bloqueo).
3. Fue colocado en suspensión por un agente: el propio proceso, su padre, o el SO.
4. No puede salir del estado de suspensión hasta que el agente lo ordene explícitamente.

---

## 2.4 Descripción de Procesos

### 2.4.1 Tablas del Sistema Operativo

Para gestionar los recursos del sistema, el SO construye y mantiene cuatro categorías de tablas:

| Tabla | Contenido |
|-------|-----------|
| **Memory tables** | Asignación de memoria principal y secundaria a procesos; atributos de protección; info de memoria virtual |
| **I/O tables** | Estado de dispositivos y canales; si un dispositivo está disponible o asignado; operaciones E/S en curso |
| **File tables** | Existencia y ubicación de archivos en disco; estado actual; permisos de acceso |
| **Process tables** | Una entrada por proceso; apunta a la imagen del proceso en memoria |

Estas tablas están **interrelacionadas**: la memoria, los dispositivos E/S y los archivos se gestionan en nombre de los procesos, por lo que las tablas de proceso las referencian entre sí.

---

### 2.4.2 La Imagen del Proceso

La **imagen del proceso** (*process image*) es la colección completa de información que define a un proceso:

| Elemento | Descripción |
|----------|-------------|
| **User Program** | El código ejecutable del programa |
| **User Data** | Datos del programa, variables globales, pila de usuario |
| **Stack** | Pila LIFO para parámetros y direcciones de retorno en llamadas a procedimientos y al sistema |
| **Process Control Block (PCB)** | Todos los datos que el SO necesita para controlar el proceso |

La imagen puede residir en **memoria secundaria (disco)** de forma contigua. Para ejecutarse, toda (o parte, con memoria virtual) la imagen debe cargarse en **memoria principal**.

---

### 2.4.3 El Bloque de Control del Proceso (PCB)

El **PCB** (*Process Control Block*, también llamado *task control block*, *process descriptor* o *task descriptor*) es la estructura de datos **más importante del sistema operativo**. Contiene toda la información que el SO necesita para gestionar un proceso.

> *"El PCB define el estado del SO. Todos los módulos del SO leen y modifican el PCB. Un error en un solo módulo podría corromper los PCBs de múltiples procesos."*  
> — Stallings

El PCB se divide en tres categorías:

#### Categoría 1: Identificación del Proceso

| Campo | Descripción |
|-------|-------------|
| **PID** | Identificador único del proceso |
| **PPID** | Identificador del proceso padre |
| **UID / GID** | Identificadores del usuario y grupo propietarios |

#### Categoría 2: Información del Estado del Procesador

| Campo | Descripción |
|-------|-------------|
| **Registros de propósito general** | 8 a 32 registros visibles al usuario |
| **Contador de programa (PC)** | Dirección de la siguiente instrucción a ejecutar |
| **Códigos de condición** | Resultado de la última operación: signo, cero, acarreo, overflow |
| **Información de estado** | Flags de interrupción habilitada/deshabilitada, modo de ejecución |
| **Punteros de pila (SP)** | Uno o más punteros a pilas LIFO del sistema |
| **PSW (Program Status Word)** | Registro especial con información de estado; en x86 se llama **EFLAGS** |

#### Categoría 3: Información de Control del Proceso

| Campo | Descripción |
|-------|-------------|
| **Estado del proceso** | Estado actual (Ready, Running, Blocked, etc.) |
| **Prioridad** | Valor para el planificador |
| **Información de planificación** | Tiempo en espera, tiempo de última ejecución, evento esperado |
| **Estructuración de datos** | Punteros a otros PCBs para colas, listas, árboles |
| **Comunicación entre procesos** | Flags, señales, mensajes pendientes |
| **Privilegios** | Accesos de memoria e instrucciones permitidos |
| **Gestión de memoria** | Punteros a tablas de segmentos y/o páginas de la memoria virtual |
| **Recursos y utilización** | Archivos abiertos, historial de uso del procesador |

Tanenbaum organiza los campos del PCB en tres grupos funcionales:

| Gestión de Procesos | Gestión de Memoria | Gestión de Archivos |
|--------------------|--------------------|---------------------|
| Registros, PC, SP | Puntero al segmento de texto | Directorio raíz |
| Estado del proceso | Puntero al segmento de datos | Directorio de trabajo |
| Prioridad | Puntero al segmento de pila | Descriptores de archivos |
| PID, PPID | | UID, GID |
| Señales, temporizadores | | |
| Tiempo de CPU usado | | |

---

## 2.5 Modos de Ejecución

Los procesadores soportan al menos **dos modos de ejecución** para proteger el SO de los programas de usuario:

| Modo | Privilegio | Quién ejecuta aquí | Capacidades |
|------|-----------|-------------------|-------------|
| **Modo Kernel** (Supervisor / Control) | Alto | El núcleo del SO | Control total: cualquier instrucción, cualquier dirección de memoria |
| **Modo Usuario** | Bajo | Programas de usuario | No puede ejecutar instrucciones privilegiadas ni acceder a regiones protegidas de memoria |

El modo actual se indica mediante un bit en el **PSW** (Program Status Word).

### Cambio de Modo

El modo cambia en las siguientes situaciones:

```
Modo usuario                    Modo kernel
─────────────                   ────────────────────
                 TRAP/syscall
Programa ──────────────────────▶ Rutina del SO
                                     │
                                     │ (ejecuta servicio)
                                     │
                 retorno
Programa ◀────────────────────── Restaura modo usuario
```

| Evento | Dirección |
|--------|-----------|
| Llamada al sistema (supervisor call) | Usuario → Kernel |
| Interrupción | Usuario → Kernel |
| Trap / excepción | Usuario → Kernel |
| Retorno de rutina del SO | Kernel → Usuario |

**Funciones típicas del kernel** (en modo kernel):
- Creación, terminación y conmutación de procesos
- Planificación y despacho
- Gestión de memoria (asignación, swapping, paginación)
- Gestión de E/S (buffers, dispositivos)
- Manejo de interrupciones y traps

---

## 2.6 Creación de Procesos

### Eventos que originan la creación de un proceso

| Evento | Descripción |
|--------|-------------|
| **Inicialización del sistema** | Al arrancar el SO se crean procesos de sistema y daemons |
| **Llamada al sistema** | Un proceso en ejecución solicita crear un proceso hijo |
| **Petición del usuario** | El usuario inicia una aplicación (doble clic, comando en terminal) |
| **Inicio de trabajo batch** | El SO lanza un nuevo trabajo de la cola batch |

### Creación en UNIX — `fork()`

En UNIX, la creación de procesos se hace con la llamada al sistema `fork()`. El SO realiza los siguientes pasos:

1. **Asigna un PID único** al nuevo proceso y agrega una entrada en la tabla de procesos.
2. **Asigna espacio** para la imagen del proceso: datos, código, pila de usuario y PCB.
3. **Copia la imagen** del proceso padre (excepto memoria compartida).
4. **Incrementa contadores** de los archivos abiertos que pertenecen al padre.
5. **Inicializa el PCB:** estado → Ready to Run, PC al punto de entrada, punteros de pila configurados.
6. **Retorna:** el PID del hijo al padre, y el valor `0` al hijo.

```c
pid_t pid = fork();

if (pid < 0) {
    /* error */
} else if (pid == 0) {
    /* proceso hijo: pid == 0 */
    execve("/bin/programa", args, env);
} else {
    /* proceso padre: pid == PID del hijo */
    waitpid(pid, &status, 0);
}
```

El hijo comienza a ejecutar en el **mismo punto del código** que el padre (al retorno del `fork()`). Si el hijo necesita ejecutar un programa diferente, usa `execve()` para reemplazar su imagen de memoria.

**Memoria y copy-on-write:** Tras el `fork()`, padre e hijo tienen espacios de memoria **separados**. Los sistemas modernos usan *copy-on-write*: los espacios se comparten como solo-lectura hasta que alguno escribe, momento en que se hace la copia real.

### Creación en Windows — `CreateProcess()`

En Windows, la creación de proceso e imagen nueva se fusionan en una sola llamada:

```c
CreateProcess(
    lpApplicationName,    // nombre del programa
    lpCommandLine,        // línea de comandos
    lpProcessAttributes,  // atributos de seguridad
    lpThreadAttributes,   // atributos del thread principal
    bInheritHandles,      // hereda handles del padre
    dwCreationFlags,      // flags de creación
    lpEnvironment,        // variables de entorno
    lpCurrentDirectory,   // directorio inicial
    lpStartupInfo,        // configuración de ventana
    lpProcessInformation  // recibe PID y handles del nuevo proceso
);
```

---

## 2.7 Terminación de Procesos

Un proceso puede terminar por cuatro razones:

| Tipo | Voluntario | Causa |
|------|-----------|-------|
| **Salida normal** | Sí | El proceso terminó su trabajo → `exit()` / `ExitProcess()` |
| **Salida por error** | Sí | El proceso detecta un error fatal y se termina a sí mismo |
| **Error fatal** | No | Bug en el proceso: división por cero, instrucción ilegal, segfault |
| **Eliminado por otro proceso** | No | Otro proceso ejecuta `kill()` (UNIX) o `TerminateProcess()` (Windows) |

> En la mayoría de los sistemas, solo el **proceso padre** puede matar a sus hijos.

---

## 2.8 Jerarquías de Procesos

### UNIX — Árbol de procesos

En UNIX los procesos forman una **jerarquía estricta** (árbol) con `init` (PID 1) como raíz. La relación padre-hijo es permanente. Un proceso y todos sus descendientes forman un **grupo de procesos**.

```
init (PID 1)
├── sshd
│   └── bash
│       └── vim
├── cron
└── httpd
    ├── worker_1
    └── worker_2
```

Al arrancar, el SO crea el **proceso 0** (swapper), que a su vez crea el **proceso 1** (`init`). El `init` es el ancestro de todos los procesos de usuario.

### Windows — Sin jerarquía

En Windows **no existe** el concepto de jerarquía de procesos. Todos los procesos son iguales. El padre recibe un *handle* especial para controlar al hijo, pero puede transferir ese handle a otro proceso — rompiendo cualquier relación jerárquica.

---

## 2.9 Control de Procesos — Conmutación

### 2.9.1 Mecanismos que Ceden el Control al SO

El SO recupera el control del procesador a través de tres mecanismos:

| Mecanismo | Asociado a | Uso típico |
|-----------|-----------|------------|
| **Interrupción** (*Interrupt*) | Externa a la instrucción actual; asíncrona | Reacción a evento externo (E/S completa, reloj) |
| **Trap** | Asociada a la instrucción actual; error o excepción | División por cero, acceso inválido a memoria |
| **Supervisor call** (*syscall*) | Solicitud explícita del programa | El proceso pide un servicio del SO |

**Tipos de interrupciones:**

| Tipo | Acción del SO |
|------|--------------|
| **Clock interrupt** | El proceso agotó su cuanto de tiempo → Ready; dispatcher asigna otro proceso |
| **I/O interrupt** | E/S completada → procesos bloqueados en esa E/S pasan a Ready |
| **Memory fault** | Dirección virtual no en memoria → page fault → bloquea proceso, carga página, luego Ready |
| **Trap** | Error fatal → Exit + cambio de proceso; o error recuperable → continúa |

---

### 2.9.2 Cambio de Modo vs. Cambio de Proceso

Un **cambio de modo** (*mode switch*) NO necesariamente implica un **cambio de proceso** (*process switch*):

```
Proceso A ejecuta          Interrupción ocurre
(modo usuario)      ────────────────────────────▶
                                                    Modo kernel
                                                    Handler ejecuta
                           ¿Proceso A puede continuar?
                                     │
                    SÍ ──────────────┤──────────── NO
                    │                              │
                    ▼                              ▼
              Restaura contexto           Cambio de proceso completo
              Retorna a A                (selecciona proceso B)
              (solo cambio de modo)
```

El mecanismo de interrupción en Tanenbaum:

1. El hardware guarda el PC y el PSW en la pila del kernel.
2. El hardware carga el nuevo PC desde el vector de interrupciones.
3. Una rutina en ensamblador guarda el resto del contexto (registros).
4. La rutina configura la nueva pila del kernel.
5. Se ejecuta la rutina de servicio en C.
6. El planificador decide qué proceso ejecutar a continuación.
7. Se restaura el contexto del proceso seleccionado y se reanuda.

---

### 2.9.3 Pasos de una Conmutación Completa

Cuando el SO decide cambiar de proceso, ejecuta los siguientes siete pasos (Stallings):

```
1. Guardar el contexto del procesador
   (PC y todos los registros del proceso actual)
          │
          ▼
2. Actualizar el PCB del proceso actual
   (cambiar su estado: Ready/Blocked/Exit;
    actualizar campos de contabilidad)
          │
          ▼
3. Mover el PCB a la cola apropiada
   (cola de Ready, cola de Blocked en evento i,
    o Ready/Suspend)
          │
          ▼
4. Seleccionar otro proceso para ejecución
   (función del planificador — scheduler)
          │
          ▼
5. Actualizar el PCB del proceso seleccionado
   (cambiar su estado a Running)
          │
          ▼
6. Actualizar estructuras de gestión de memoria
   (tablas de páginas/segmentos del nuevo proceso)
          │
          ▼
7. Restaurar el contexto del proceso seleccionado
   (cargar los valores previos del PC y registros)
```

> La conmutación de contexto tiene un **costo real en tiempo de CPU**: el tiempo invertido en guardar y restaurar el contexto no realiza trabajo útil. Por eso se busca minimizar el número de conmutaciones.

---

## 2.10 Threads (Hilos de Ejecución)

### 2.10.1 ¿Por qué Usar Threads?

Un **thread** (hilo) es una unidad de ejecución dentro de un proceso. Múltiples threads pueden coexistir en el mismo proceso compartiendo su espacio de memoria y recursos.

**Razones para usar threads:**

| Razón | Explicación |
|-------|-------------|
| **Paralelismo** | Permiten actividades paralelas dentro de una aplicación |
| **Eficiencia** | Son hasta 100 veces más rápidos de crear y destruir que procesos |
| **E/S + CPU simultáneos** | Mientras un thread espera E/S, otro sigue usando la CPU |
| **Multicore** | Aprovechan paralelismo real en sistemas con múltiples núcleos |

**Ejemplo — Servidor web con modelo dispatcher/worker:**

```
Petición HTTP llega
        │
        ▼
[Thread Dispatcher] ──── despierta ────▶ [Thread Worker]
                                               │
                                               │ ¿Página en caché?
                                    SÍ ────────┤──────── NO
                                    │                    │
                                    ▼                    ▼
                              Responde           Hace syscall de disco
                              al cliente         (se bloquea)
                                                         │
                                         Otro worker ejecuta mientras tanto
```

**Ejemplo — Procesador de texto con tres threads:**
- **Thread 1:** Interacción con el usuario
- **Thread 2:** Reformateo del documento (responde a cambios)
- **Thread 3:** Respaldo automático al disco periódicamente

---

### 2.10.2 El Modelo Clásico de Threads

**Lo que cada thread tiene propio vs. lo que se comparte:**

| Por proceso (compartido) | Por thread (privado) |
|--------------------------|----------------------|
| Espacio de direcciones | Contador de programa (PC) |
| Variables globales | Registros |
| Archivos abiertos | Pila (stack) |
| Procesos hijos | Estado (Running/Ready/Blocked) |
| Alarmas pendientes | |
| Señales y manejadores | |
| Información de contabilidad | |

Los estados de un thread son análogos a los de un proceso: **Running, Blocked, Ready, Terminated**.

> Los threads no tienen estado **Suspended** porque la memoria es compartida entre todos los threads del proceso — no aplica el swapping individual por thread.

**API POSIX para threads (pthreads):**

```c
pthread_create(&thread, &attr, funcion, arg);  // crear thread
pthread_exit(status);                           // terminar thread
pthread_join(thread, &valor_retorno);           // esperar a que termine
pthread_yield();                                // ceder CPU voluntariamente
```

---

### 2.10.3 Implementación en Espacio de Usuario (ULT)

Los threads se implementan mediante una **biblioteca de threads en espacio de usuario**, sin que el kernel los conozca. El kernel solo ve procesos de un único thread.

```
Proceso (vista del kernel)
┌─────────────────────────────┐
│ Biblioteca de threads        │
│  Thread A  Thread B  Thread C│  ← Todos en espacio de usuario
│  [Ready]   [Running] [Blocked]│
└─────────────────────────────┘
           Un solo proceso
```

| Ventajas | Desventajas |
|----------|-------------|
| Conmutación sin llamadas al kernel (muy rápido) | Si un thread hace syscall bloqueante, **todo el proceso se bloquea** |
| Cada proceso puede tener su propio algoritmo de planificación | Un thread en ejecución no libera CPU a menos que llame a la biblioteca |
| No requiere tabla de threads en el kernel | |

---

### 2.10.4 Implementación en el Kernel (KLT)

El kernel **conoce y gestiona** los threads directamente. La tabla de threads está en el kernel.

```
Kernel
┌──────────────────────────────────┐
│ Tabla de threads                  │
│  Thread A  Thread B  Thread C    │
└──────────────────────────────────┘
```

| Ventajas | Desventajas |
|----------|-------------|
| Si un thread se bloquea, el kernel planifica otro del mismo proceso | Creación y conmutación implican llamadas al kernel (mayor overhead) |
| Paralelismo real en sistemas multiprocesador | |

**Implementaciones híbridas:** combinan ULT y KLT — múltiples threads de usuario por thread de kernel. El programador controla cuántos threads de kernel usa.

---

## 2.11 Procesos en UNIX SVR4

UNIX SVR4 usa el modelo de **ejecución dentro del proceso de usuario** — el SO se ejecuta en el contexto de un proceso de usuario.

UNIX utiliza dos categorías de procesos:
- **Procesos de sistema:** ejecutan en modo kernel para funciones administrativas (asignación de memoria, swapping).
- **Procesos de usuario:** ejecutan en modo usuario para programas de usuario, y en modo kernel durante llamadas al sistema o interrupciones.

### Estados de proceso en UNIX SVR4

UNIX SVR4 define **9 estados** de proceso:

| Estado | Descripción |
|--------|-------------|
| **User Running** | Ejecutando en modo usuario |
| **Kernel Running** | Ejecutando en modo kernel |
| **Ready to Run, in Memory** | Listo para ejecutar tan pronto el kernel lo planifique |
| **Asleep in Memory** | Bloqueado esperando un evento; proceso en memoria principal |
| **Ready to Run, Swapped** | Listo para ejecutar pero el swapper debe cargarlo a memoria |
| **Sleeping, Swapped** | Bloqueado y en almacenamiento secundario |
| **Preempted** | Retorna de modo kernel a modo usuario pero el kernel lo desaloja |
| **Created** | Proceso recién creado por `fork()`; aún no está listo |
| **Zombie** | El proceso terminó pero deja un registro para que su padre lo recoja |

> **Restricción importante:** Un proceso que ejecuta en **modo kernel NO puede ser desalojado** (non-preemptible). La preempción solo ocurre cuando el proceso va a pasar de modo kernel a modo usuario. Esto hace a UNIX tradicional inadecuado para procesamiento en tiempo real estricto.

### Imagen de proceso en UNIX SVR4

| Componente | Descripción |
|------------|-------------|
| **Process text** | Instrucciones máquina ejecutables |
| **Process data** | Datos accesibles por el programa de usuario |
| **User stack** | Argumentos, variables locales, punteros de retorno en modo usuario |
| **Shared memory** | Memoria compartida con otros procesos para IPC |
| **Register context** | PC, PSR, SP, registros de propósito general |
| **Process table entry** | Define el estado del proceso; siempre accesible al SO |
| **U (user) area** | Información de control accesible solo en el contexto del proceso |
| **Per-process region table** | Mapeo virtual → físico; permisos de acceso |
| **Kernel stack** | Pila para llamadas a procedimientos del kernel |

### Procesos especiales de UNIX

| Proceso | PID | Descripción |
|---------|-----|-------------|
| **Proceso 0** | 0 | Creado en boot time como estructura de datos; es el swapper |
| **init** | 1 | Creado por el proceso 0; ancestro de todos los procesos de usuario |

### fork() en UNIX SVR4 — Pasos detallados

1. Asigna una entrada en la tabla de procesos para el proceso hijo.
2. Asigna un PID único al hijo.
3. Hace una copia de la imagen del proceso padre (excepto memoria compartida).
4. Incrementa contadores de archivos que pertenecen al padre.
5. Asigna al hijo el estado **Ready to Run**.
6. Retorna el PID del hijo al padre, y el valor `0` al hijo.

Después del `fork()`, el dispatcher puede:
- Permanecer en el proceso padre.
- Transferir control al proceso hijo.
- Transferir control a un tercer proceso (padre e hijo quedan en Ready).

---

## 2.12 Resumen del Capítulo

### Puntos clave

| Concepto | Esencia |
|----------|---------|
| **Proceso** | Instancia dinámica de un programa en ejecución; tiene PC, registros, pila y espacio de memoria propio |
| **Pseudoparalelismo** | La CPU alterna entre procesos creando la ilusión de ejecución simultánea |
| **Estados** | Un proceso transita entre New, Ready, Running, Blocked y Exit; con swapping se añaden Ready/Suspend y Blocked/Suspend |
| **PCB** | Estructura de datos central del SO; contiene identificación, estado del procesador e información de control |
| **Modo kernel/usuario** | El SO se protege ejecutando en modo privilegiado; los programas de usuario no pueden acceder directamente al hardware |
| **Conmutación** | Cambiar de proceso implica guardar el contexto del proceso actual y restaurar el del siguiente (7 pasos) |
| **Thread** | Unidad de ejecución dentro de un proceso; comparte memoria y recursos con otros threads del mismo proceso |
| **ULT vs. KLT** | Threads en espacio de usuario son más rápidos; threads en kernel son más robustos frente a llamadas bloqueantes |
| **fork() en UNIX** | Crea un clon del proceso padre; el hijo puede ejecutar otro programa con execve() |

### Comparación: Tanenbaum vs. Stallings

| Aspecto | Tanenbaum (Cap. 2) | Stallings (Cap. 3) |
|---------|-------------------|-------------------|
| **Modelo de estados** | 3 estados principales | 5 estados + 2 suspendidos (7 total) |
| **PCB** | Tabla con 3 grupos funcionales | Tabla 3 categorías: identificación, estado del procesador, control |
| **Creación UNIX** | fork() + execve(); copy-on-write | fork(): 5 pasos detallados en el SO |
| **Creación Windows** | CreateProcess() con 10 parámetros | No detalla |
| **Jerarquía** | Árbol UNIX (init); sin jerarquía en Windows (handles) | Padre/hijo; proceso 0 y proceso 1 en UNIX |
| **Threads** | Cap. 2: ULT, KLT, híbridos, scheduler activations, pop-up threads | Cap. 4 (separado): ULT/KLT/multicore |
| **Modos de ejecución** | Kernel/usuario; TRAP; PSW | Kernel/usuario; PSW; EFLAGS x86; 7 pasos de conmutación |
| **Swapping** | No elabora | Detallado: razones, estados suspend |
| **UNIX SVR4** | fork()/execve() generales | 9 estados, imagen completa, fork() interno |

---

*Basado en: Modern Operating Systems 4ª Ed. (Tanenbaum & Bos, Cap. 2) y Operating Systems: Internals and Design Principles 9ª Ed. (Stallings, Cap. 3)*
