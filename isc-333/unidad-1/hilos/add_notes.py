#!/usr/bin/env python3
"""
Agrega notas de presentador (<!-- ... -->) a cada diapositiva Marp
de mos.md y osid.md.
Las notas aparecen en el modo presentador de Marp.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────
# NOTAS PARA mos.md  — Tanenbaum, Modern Operating Systems §2.2
# Índice 0 = frontmatter YAML (sin nota).
# Índice 1 = primera diapositiva (título).
# ─────────────────────────────────────────────────────────────────
MOS_NOTES = {
    1: "",   # Portada — sin nota
    2: (
        "**Contexto histórico:** en los sistemas UNIX clásicos cada proceso era monohilo. "
        "Para lograr concurrencia había que usar `fork()`, que duplica todo el espacio de memoria —muy costoso—. "
        "Los hilos resuelven esto al compartir el espacio de direcciones del proceso.\n\n"
        "**Cuasi-paralelismo vs paralelismo real:** en un CPU de un núcleo los hilos alternan "
        "en la CPU (tiempo compartido); con multinúcleo pueden ejecutarse verdaderamente en paralelo.\n\n"
        "**Pregunta de reflexión:** ¿qué diferencia hay entre tener 4 procesos y tener 1 proceso con 4 hilos?"
    ),
    3: (
        "**Puntos clave:**\n"
        "- El beneficio central en E/S es el **solapamiento**: mientras hilo A espera que el disco responda "
        "(puede tardar milisegundos), hilo B usa la CPU productivamente.\n"
        "- Creación de hilo ≈ 10-100× más rápida que `fork()` porque no hay copia de memoria.\n"
        "- La limitación CPU-bound es importante para el examen: si todos los hilos solo computan "
        "y no hacen E/S, el paralelismo real solo ocurre con múltiples núcleos.\n\n"
        "**Ejemplo práctico:** un servidor web sin hilos que atiende 1000 req/s: con una sola petición "
        "lenta de disco todo el servidor se bloquea. Con hilos, solo ese hilo se bloquea."
    ),
    4: (
        "**Análisis del diagrama (Fig. 2-7):**\n"
        "- **Hilo 1 (interactivo):** responde a teclado/ratón. Sin él, el usuario esperaría cada vez "
        "que el reformateador trabaja.\n"
        "- **Hilo 2 (reformateo):** recalcula paginación en segundo plano mientras el usuario escribe.\n"
        "- **Hilo 3 (respaldo):** guarda periódicamente sin detener los otros dos hilos.\n\n"
        "**Sin hilos:** habría que usar una máquina de estados con interrupciones y callbacks, "
        "lo que hace el código muy difícil de mantener."
    ),
    5: (
        "**El punto crítico es la memoria compartida:** los tres hilos acceden directamente a las "
        "mismas estructuras de datos del documento —sin IPC (pipes, sockets, shared memory explícita)—. "
        "Esto simplifica enormemente la comunicación pero obliga a usar sincronización "
        "(mutex, semáforos) para evitar condiciones de carrera."
    ),
    6: (
        "**Patrón Dispatcher/Worker:** el dispatcher es un hilo ligero que solo recibe solicitudes y "
        "las asigna al pool; los workers hacen el trabajo real.\n\n"
        "Este patrón es la base de Nginx, Apache MPM Worker, Java thread pools y Go routines.\n\n"
        "**Ventaja clave:** si Worker 1 se bloquea esperando un disco lento, Worker 2 y 3 "
        "continúan atendiendo otras solicitudes sin interferencia."
    ),
    7: (
        "**Comparación directa con proceso monohilo:** si el servidor tuviese un solo hilo "
        "atendiendo solicitudes, mientras espera el disco **ningún** cliente puede ser atendido —el "
        "proceso entero está bloqueado en la syscall `read()`—.\n\n"
        "Con hilos, la E/S de un hilo se solapa con el cómputo de otros. "
        "Este solapamiento es la razón principal de mejora de throughput en servidores web."
    ),
    8: (
        "**Pool precreado vs creación por demanda:** crear un hilo por cada solicitud introduciría "
        "latencia de creación y consumiría muchos recursos. El pool amortiza ese costo: "
        "los hilos se crean al arrancar el servidor y se reutilizan.\n\n"
        "Cuando no hay workers libres, las solicitudes entran en cola. "
        "El tamaño del pool es un parámetro de configuración clave (ej. `MaxThreads` en Apache)."
    ),
    9: (
        "**Análisis de los tres modelos (Fig. 2-10):**\n"
        "- **Monohilo:** el más simple, pero una llamada bloqueante detiene todo. Solo útil para cargas triviales.\n"
        "- **Máquina de estados finitos (FSM):** usa `select()`/`epoll()` con E/S no bloqueante. "
        "Es el más eficiente en un solo núcleo pero muy difícil de programar "
        "(código como callbacks anidados — «callback hell»).\n"
        "- **Hilos:** el mejor balance. El programador escribe código secuencial natural; "
        "el SO maneja la concurrencia.\n\n"
        "**Node.js** usa el modelo FSM para el event loop; **Java EE** usa hilos; "
        "**Nginx** combina ambos."
    ),
    10: (
        "**Separación conceptual fundamental:**\n"
        "- **Proceso = contenedor de recursos** (espacio de direcciones, archivos abiertos, "
        "señales, procesos hijo). Garantiza aislamiento entre aplicaciones.\n"
        "- **Hilo = unidad de ejecución** (PC, registros, pila). "
        "La CPU planifica hilos, no procesos.\n\n"
        "Esta distinción aparece en Windows (PROCESS_OBJECT vs THREAD_OBJECT), "
        "POSIX pthreads, y en el modelo de 4 niveles de Solaris.\n\n"
        "**Nota:** Linux difumina esta línea: proceso e hilo son ambos `task_struct` "
        "(ver Stallings cap. 4)."
    ),
    11: (
        "**Para el examen — memorizar qué es compartido y qué es privado:**\n\n"
        "| Compartido (proceso) | Privado (hilo) |\n"
        "|---|---|\n"
        "| Espacio de direcciones | Contador de programa (PC) |\n"
        "| Variables globales | Registros del CPU |\n"
        "| Archivos abiertos | Pila de ejecución |\n"
        "| Procesos hijo | Estado del hilo |\n"
        "| Señales y handlers | Variables locales |\n\n"
        "**¿Por qué la pila es privada?** Cada hilo tiene su propia secuencia de llamadas a funciones "
        "con sus propias variables locales y direcciones de retorno."
    ),
    12: (
        "**Transiciones importantes:**\n"
        "- `running → blocked`: el hilo hace una llamada bloqueante (E/S, `wait()`, adquirir mutex ocupado).\n"
        "- `blocked → ready`: el evento que esperaba ocurrió (datos disponibles, mutex liberado).\n"
        "- `running → ready`: el planificador expulsa al hilo por quantum agotado (preemption).\n"
        "- `thread_exit → terminated`: fin del hilo; sus recursos no se liberan hasta que otro hilo haga `join()`.\n\n"
        "**Diferencia con procesos:** los estados son análogos, pero las transiciones "
        "en hilos de kernel son más frecuentes y rápidas."
    ),
    13: (
        "**Mapeo con la API POSIX pthreads:**\n"
        "```c\n"
        "pthread_create(&tid, NULL, fn, arg);  // thread_create\n"
        "pthread_exit(retval);                  // thread_exit\n"
        "pthread_join(tid, &retval);            // thread_join\n"
        "pthread_yield();                       // thread_yield (no estándar en todos los SO)\n"
        "```\n\n"
        "**`thread_yield`** raramente se usa directamente en producción; "
        "el planificador del kernel maneja la cesión de CPU automáticamente. "
        "Se usa principalmente en implementaciones de hilos en espacio de usuario "
        "donde no hay planificador con preemption."
    ),
    14: (
        "**Problema del fork en contexto multihilo (POSIX):**\n"
        "POSIX define que `fork()` en un proceso multihilo crea un hijo con **un solo hilo** "
        "(el que llamó a `fork()`). "
        "Los mutexes bloqueados por otros hilos en el padre quedan bloqueados en el hijo "
        "sin nadie que los libere → deadlock potencial.\n\n"
        "**Solución:** usar `exec()` inmediatamente después de `fork()`, "
        "o registrar handlers con `pthread_atfork()`.\n\n"
        "**Señales y multihilo:** `SIGINT` puede ser recibida por cualquier hilo. "
        "Para control preciso se usa `pthread_sigmask()` y `sigwait()`."
    ),
    15: (
        "**Historia de Pthreads:** antes del estándar IEEE 1003.1c (1995), "
        "cada SO tenía su propia API de hilos incompatible "
        "(Solaris threads, DCE threads, POSIX draft, etc.). "
        "Pthreads permitió escribir código portable entre Linux, macOS, Solaris y otros UNIX.\n\n"
        "**Implementación en Linux:** Pthreads usa internamente `clone()` con los flags "
        "`CLONE_VM | CLONE_FILES | CLONE_THREAD | CLONE_SIGHAND`. "
        "La biblioteca NPTL (Native POSIX Thread Library) reemplazó a LinuxThreads en 2003 "
        "con una implementación 1:1 mucho más eficiente."
    ),
    16: (
        "**La biblioteca de hilos** (como GNU Portable Threads) se ejecuta completamente en "
        "modo usuario. El kernel solo ve un proceso monohilo.\n\n"
        "**Cómo funciona el cambio de contexto en user space:**\n"
        "1. La biblioteca guarda los registros del hilo actual en su TCB (Thread Control Block)\n"
        "2. Carga los registros del siguiente hilo desde su TCB\n"
        "3. Salta al PC guardado del siguiente hilo\n"
        "Todo esto sin una sola llamada al sistema → muy rápido."
    ),
    17: (
        "**Velocidad del cambio de contexto en user space:**\n"
        "Un cambio de contexto de kernel requiere:\n"
        "1. Trap (cambio a modo kernel) — ~100 ciclos\n"
        "2. Guardar/restaurar contexto de kernel\n"
        "3. Retorno a modo usuario\n\n"
        "Un cambio de contexto en user space: solo guardar/restaurar registros (~10-20 ciclos).\n\n"
        "**En hardware moderno** con vDSO (Linux) y syscalls optimizadas, la diferencia es "
        "menos dramática que en los años 90, pero sigue siendo relevante para aplicaciones "
        "con millones de cambios de contexto por segundo."
    ),
    18: (
        "**Técnica de jacketing en detalle:**\n"
        "En lugar de llamar directamente a `read()` (que bloquea el proceso entero), "
        "se llama a una versión envuelta:\n"
        "```c\n"
        "// Versión 'jacket' de read():\n"
        "ssize_t read_jacket(int fd, void *buf, size_t n) {\n"
        "    while (!data_available(fd))  // select() no bloqueante\n"
        "        thread_yield();           // ceder CPU a otro hilo\n"
        "    return real_read(fd, buf, n);\n"
        "}\n"
        "```\n\n"
        "**El problema:** hay que envolver TODAS las llamadas bloqueantes del sistema. "
        "Esto es laborioso y propenso a errores. "
        "Los hilos de kernel eliminan esta necesidad."
    ),
    19: (
        "**Diferencia clave con user space:** cada hilo tiene su propio hilo de kernel. "
        "Si Hilo A del proceso hace `read()` y se bloquea, el kernel puede planificar "
        "Hilo B del mismo proceso en otra CPU —o en la misma CPU después del bloqueo—.\n\n"
        "**Paralelismo real en multinúcleo:** dos hilos del mismo proceso pueden ejecutarse "
        "simultáneamente en CPU1 y CPU2. Esto es imposible con hilos en user space "
        "(el kernel solo ve un proceso en una CPU a la vez)."
    ),
    20: (
        "**Costo concreto de las syscalls para operaciones de hilo:**\n"
        "- Crear un hilo de kernel: ~microsegundo\n"
        "- Crear un hilo de user space: ~nanosegundos\n"
        "- Bloquear en mutex de kernel: syscall `futex()` — tiene costo si hay contención\n\n"
        "**Por eso se usan thread pools:** pagar el costo de creación una sola vez, "
        "reutilizar los hilos para muchas tareas.\n\n"
        "**Pregunta de examen:** ¿qué ventaja tienen los hilos de kernel sobre los de user space? "
        "→ Paralelismo real en multinúcleo y no bloquean el proceso entero en llamadas al sistema."
    ),
    21: (
        "**Modelo M:N (muchos-a-muchos):** N hilos de usuario se mapean a M hilos de kernel (M ≤ N). "
        "Permite tener miles de hilos de usuario ligeros, con solo M hilos de kernel activos.\n\n"
        "**NPTL en Linux eligió 1:1:** cada pthread corresponde exactamente a un hilo de kernel. "
        "Razón: las syscalls de Linux son muy eficientes, y la complejidad del M:N "
        "superó sus beneficios.\n\n"
        "**Solaris 9+ también migró a 1:1** por la misma razón. "
        "El modelo híbrido persiste en Go (goroutines sobre hilos de OS) y en Erlang."
    ),
    22: (
        "**¿Por qué el M:N es difícil de implementar?**\n"
        "El planificador de usuario necesita coordinarse con el planificador del kernel "
        "para evitar que ambos tomen decisiones conflictivas. "
        "Por ejemplo: si el kernel bloquea un hilo de kernel que el runtime de usuario cree que está libre, "
        "el runtime puede asignarle más trabajo que nunca se ejecutará.\n\n"
        "**Conclusión práctica:** los SO modernos (Linux, Windows, macOS) usan 1:1 "
        "porque las syscalls son baratas y la simplicidad supera al rendimiento teórico del M:N."
    ),
    23: (
        "**El mecanismo de upcall rompe el principio de capas:**\n"
        "Normalmente en un SO las capas inferiores nunca llaman a las superiores "
        "(el kernel no llama a código de usuario). "
        "Con activaciones del planificador, el kernel usa upcalls para notificar al runtime "
        "cuando un hilo se bloquea o se desbloquea.\n\n"
        "**Flujo de una upcall:**\n"
        "1. Hilo A llama a `read()` y el kernel lo bloquea\n"
        "2. El kernel hace upcall al runtime: «el hilo A se bloqueó, te asigno un VP extra»\n"
        "3. El runtime ejecuta el hilo B en ese VP\n"
        "4. Cuando A se desbloquea, otra upcall notifica al runtime\n\n"
        "**Implementación real:** `scheduler activations` de Anderson et al. (1991), "
        "base conceptual de los goroutines de Go."
    ),
    24: (
        "**Casos de uso reales de pop-up threads:**\n"
        "- Servidores de red que crean un hilo por conexión entrante\n"
        "- Sistemas de mensajería asíncrona (MQ, Kafka consumers)\n"
        "- Manejadores de eventos en sistemas embebidos\n\n"
        "**Diferencia clave con un pool de hilos:**\n"
        "| Pop-up thread | Pool de hilos |\n"
        "|---|---|\n"
        "| Se crea al llegar el mensaje | Hilos esperan en idle |\n"
        "| Latencia = costo de creación | Latencia mínima |\n"
        "| Menor uso de memoria en idle | Mayor uso de memoria en idle |\n"
        "| Riesgo de crear demasiados | Límite natural de hilos |\n"
    ),
    25: (
        "**Kernel thread vs user thread para pop-up:**\n"
        "- **En kernel:** acceso directo a estructuras del kernel, más rápido, "
        "pero un bug puede corromper el estado del kernel (panic). "
        "Usado en controladores de dispositivos.\n"
        "- **En user space:** más seguro, aislado, pero requiere cambio de contexto kernel↔usuario. "
        "Usado en la mayoría de aplicaciones.\n\n"
        "**Regla práctica:** solo se usan pop-up threads en kernel para rutas de código "
        "extremadamente críticas en rendimiento y muy bien probadas."
    ),
    26: (
        "**El problema de `errno` ilustra perfectamente el desafío:**\n"
        "En C estándar, `errno` es una variable global. Si Hilo 1 llama a `open()` y falla, "
        "y antes de leer `errno` el planificador cede a Hilo 2 que también falla en una syscall, "
        "Hilo 2 sobreescribe `errno`. Cuando Hilo 1 reanuda, lee el `errno` incorrecto.\n\n"
        "**Solución moderna:** en glibc `errno` es una macro que expande a "
        "`(*__errno_location())` — una función que retorna un puntero a la copia TLS de `errno`.\n\n"
        "**`strtok` no reentrante:** mantiene un puntero interno estático. "
        "Alternativa: `strtok_r()` que recibe el contexto como argumento."
    ),
    27: (
        "**TLS en diferentes lenguajes/plataformas:**\n"
        "- **C/GCC:** `__thread int var;` o `_Thread_local int var;` (C11)\n"
        "- **C++11:** `thread_local int var;`\n"
        "- **Java:** `ThreadLocal<T> var = new ThreadLocal<>();`\n"
        "- **Python:** `import threading; local = threading.local()`\n"
        "- **Go:** no tiene TLS directo — goroutines evitan variables globales mediante closures\n"
        "- **Rust:** el sistema de tipos previene data races en tiempo de compilación "
        "(`Send` y `Sync` traits)\n\n"
        "**Wrappers para serialización** (jacketing): envuelven funciones no reentrantes "
        "con un mutex para garantizar acceso exclusivo."
    ),
    28: (
        "**Para el examen — tabla de comparación:**\n\n"
        "| Aspecto | User Space | Kernel | Híbrido |\n"
        "|---|---|---|---|\n"
        "| Cambio de contexto | Sin syscall (rápido) | Con syscall (lento) | Medio |\n"
        "| Bloqueo E/S | Bloquea TODO el proceso | Solo bloquea ese hilo | Depende |\n"
        "| Paralelismo (multicore) | NO | SÍ | SÍ (si M KLTs ≥ CPUs) |\n"
        "| Flexibilidad planif. | Alta (programa define) | Baja (kernel decide) | Media |\n"
        "| Ejemplo real | GNU Portable Threads | Linux NPTL, Windows | Go, Erlang |\n\n"
        "**Tendencia actual:** la mayoría de SO modernos usa 1:1 (kernel threads) "
        "porque el hardware es rápido y la simplicidad supera los beneficios teóricos del M:N."
    ),
    29: (
        "**Síntesis del capítulo 2.2:**\n"
        "Los hilos son la solución del SO al problema de la concurrencia dentro de un proceso. "
        "Los temas están interconectados:\n"
        "- La **motivación** (procesador de texto, servidor web) justifica la necesidad\n"
        "- El **modelo clásico** define qué se comparte y qué es privado\n"
        "- Las **implementaciones** (user/kernel/híbrido) son trade-offs del mismo problema\n"
        "- Las **complicaciones** (fork, señales, TLS) son consecuencias del modelo compartido\n\n"
        "**Conexión con Stallings (osid.md):** los conceptos aquí vistos son los fundamentos "
        "de las implementaciones reales en Windows (cap. 4.4), Solaris (4.5), Linux (4.6) y Android (4.7)."
    ),
    30: "",  # Portada final — sin nota
}

# ─────────────────────────────────────────────────────────────────
# NOTAS PARA osid.md  — Stallings, OS Internals and Design, Cap. 4
# ─────────────────────────────────────────────────────────────────
OSID_NOTES = {
    1: "",   # Portada
    2: (
        "**Ley de Amdahl — derivación intuitiva:**\n"
        "Si f = fracción paralelizable, entonces (1-f) es la fracción serial que siempre tarda lo mismo.\n"
        "Con N CPUs, la parte paralela se reduce N veces pero la serial no:\n"
        "  Tiempo(N) = (1-f) + f/N  →  Aceleración = 1 / ((1-f) + f/N)\n\n"
        "**Ejemplo concreto:** f=0.90, N=8\n"
        "  Aceleración = 1 / (0.10 + 0.90/8) = 1 / 0.2125 ≈ **4.7×**\n"
        "  Para lograr 8× necesitaríamos f = 1.0 (imposible en la práctica)\n\n"
        "**Implicación crítica:** reducir la fracción serial es más impactante que agregar CPUs. "
        "Con f=0.99 y N=∞, la aceleración máxima es solo **100×**."
    ),
    3: (
        "**Coherencia de caché — el verdadero cuello de botella:**\n"
        "Cuando CPU1 modifica un valor en su caché L1, el protocolo MESI debe invalidar "
        "las copias en caché de CPU2, CPU3... Cada invalidación es un mensaje de bus "
        "(IPI — Inter-Processor Interrupt). Con muchos núcleos compartiendo muchos datos, "
        "este overhead puede superar el beneficio del paralelismo.\n\n"
        "**Las aplicaciones que escalan bien** tienen en común: **baja comunicación entre hilos**. "
        "Si cada hilo trabaja en su propio conjunto de datos (sin compartir estado), "
        "la fracción serial se acerca a cero y la ley de Amdahl favorece el escalado."
    ),
    4: (
        "**Lecciones del caso Valve (Motor Source):**\n"
        "1. No existe una estrategia universal; hay que analizar cada módulo\n"
        "2. Los sistemas predecibles y autocontenidos (audio) se fijan a un CPU → sin locks, sin overhead\n"
        "3. Los sistemas con mucha independencia (renderizado de objetos) se paralelizan finamente\n"
        "4. Los sistemas con dependencias fuertes (IA → física → renderizado) se manejan con granularidad gruesa\n\n"
        "**Resultado medible:** el motor Source pasó de ~20 fps a ~60 fps en hardware quad-core de 2007 "
        "después de la refactorización multihilo."
    ),
    5: (
        "**Patrón lector/escritor con 95% lecturas:**\n"
        "Con acceso 95% de lectura, usar `pthread_rwlock_t` (POSIX) o `std::shared_mutex` (C++17) "
        "permite que múltiples lectores accedan simultáneamente:\n"
        "```c\n"
        "pthread_rwlock_rdlock(&lock);  // múltiples lectores concurrentes\n"
        "// leer datos...\n"
        "pthread_rwlock_unlock(&lock);\n"
        "\n"
        "pthread_rwlock_wrlock(&lock);  // escritor exclusivo\n"
        "// modificar datos...\n"
        "pthread_rwlock_unlock(&lock);\n"
        "```\n"
        "Con 95% lecturas, casi nunca hay contención real → alto paralelismo efectivo."
    ),
    6: (
        "**Jerarquía de abstracciones en Windows:**\n"
        "- **Fibra:** planificada manualmente por la aplicación dentro de un hilo. "
        "El kernel no la conoce. Útil para migrar código cooperativo (como coroutines).\n"
        "- **UMS (User-Mode Scheduling):** disponible en Windows 7+. "
        "Permite que la aplicación implemente su propio planificador, "
        "cambiando entre hilos UMS sin pasar por el kernel. "
        "Usado por runtimes de lenguajes (similar a goroutines de Go).\n"
        "- **Grupo de Hilos (Thread Pool):** API de alto nivel. "
        "El SO gestiona la creación/destrucción de hilos automáticamente."
    ),
    7: (
        "**Descriptor de Seguridad:** contiene el SID del propietario, SID del grupo, "
        "DACL (permisos discrecionales) y SACL (auditoría). "
        "Permite que el modelo de seguridad de Windows sea uniforme: "
        "todo recurso (archivo, proceso, hilo, mutex) tiene un descriptor de seguridad.\n\n"
        "**Afinidad de procesador:** fijar un hilo a una CPU específica evita la migración "
        "y maximiza la reutilización de caché L1/L2. "
        "Usado en aplicaciones de tiempo real, video juegos y procesamiento de señales digitales.\n\n"
        "**Contador de suspensión:** cada llamada a `SuspendThread()` incrementa el contador; "
        "el hilo solo se reanuda cuando llega a 0 con `ResumeThread()`."
    ),
    8: (
        "**El estado 'Transición' es único de Windows:**\n"
        "Ocurre cuando:\n"
        "1. El hilo está listo para ejecutar (su evento ocurrió)\n"
        "2. Pero su pila de kernel fue paginada a disco (presión de memoria)\n"
        "3. Debe esperar que la pila vuelva a RAM antes de ejecutar\n\n"
        "Este estado es transparente para las aplicaciones pero visible en el "
        "Performance Monitor de Windows (contador de hilos en transición).\n\n"
        "**Estado 'En Espera':** el dispatcher seleccionó el hilo para ejecutar en un procesador "
        "pero aún no ha completado el cambio de contexto (estado transitorio muy breve)."
    ),
    9: (
        "**Modelo de apps Metro/UWP — inspirado en iOS:**\n"
        "Microsoft adoptó el modelo de ciclo de vida de iOS para Windows 8: "
        "solo una app en primer plano, las demás suspendidas.\n\n"
        "**WNS (Windows Notification Service):** análogo a APNs (Apple) y FCM (Google). "
        "El dispositivo mantiene una conexión persistente con el servidor WNS. "
        "Cuando el backend quiere notificar, envía al WNS que reenvía al dispositivo. "
        "La app se 'despierta' brevemente sin necesidad de estar en ejecución.\n\n"
        "**1 segundo de CPU por hora:** garantiza que apps en background no consumen batería. "
        "Tasa equivalente a ~0.028% de uso de CPU."
    ),
    10: (
        "**Evolución del modelo de hilos en Solaris:**\n"
        "- **Solaris 2.x (años 90):** modelo M:N verdadero. "
        "Muchos ULT se mapeaban a pocos LWP. Flexible pero complejo.\n"
        "- **Solaris 9+ (2002):** migró a 1:1. Cada ULT = 1 LWP = 1 hilo de núcleo. "
        "Los LWPs son ahora transparentes para el programador.\n\n"
        "**¿Por qué el M:N fue abandonado?** La complejidad de sincronización entre el "
        "planificador de usuario y el kernel superó los beneficios en hardware moderno. "
        "Las syscalls de Solaris son eficientes y el 1:1 es mucho más predecible."
    ),
    11: (
        "**Estado ZOMBIE — importante para entender `wait()`:**\n"
        "Cuando un hilo/proceso termina, sus recursos se liberan pero "
        "la entrada en la tabla de procesos permanece hasta que el padre llame a `wait()`.\n"
        "Esto permite al padre obtener el código de salida del hijo.\n\n"
        "**Si el padre termina antes:** el hijo zombie es adoptado por `init` (PID 1), "
        "que inmediatamente llama a `wait()` para limpiarlo.\n\n"
        "**Zombie leak:** si el padre nunca llama a `wait()`, la tabla de procesos se llena "
        "de zombies → el sistema se queda sin PIDs disponibles (DoS)."
    ),
    12: (
        "**El problema de las interrupciones en multiprocesadores clásicos:**\n"
        "Para acceder a estructuras compartidas del kernel durante un handler de interrupción, "
        "hay que deshabilitar interrupciones. En un SMP con 16 CPUs, deshabilitar interrupciones "
        "requiere un IPI (Inter-Processor Interrupt) a todos los CPUs — muy costoso.\n\n"
        "**Solución de Solaris con hilos de interrupción:**\n"
        "1. Cada interrupción activa un hilo de un pool precreado\n"
        "2. El hilo usa mutex normales (sin deshabilitar interrupciones globalmente)\n"
        "3. Prioridad más alta que todos los demás hilos → ejecuta casi inmediatamente\n"
        "4. Al terminar, regresa al pool\n\n"
        "**Resultado:** escala linealmente con el número de CPUs sin coordinación global."
    ),
    13: (
        "**Campos clave de `task_struct` para el planificador (Linux kernel):**\n"
        "```c\n"
        "struct task_struct {\n"
        "    volatile long  state;      // TASK_RUNNING, TASK_INTERRUPTIBLE...\n"
        "    int            prio;       // prioridad dinámica [0-139]\n"
        "    int            static_prio; // prioridad estática (nice value)\n"
        "    unsigned int   policy;     // SCHED_NORMAL, SCHED_FIFO, SCHED_RR...\n"
        "    struct sched_entity se;    // entidad del Completely Fair Scheduler\n"
        "    pid_t          pid;        // ID del hilo\n"
        "    pid_t          tgid;       // ID del grupo de hilos (= PID del proceso)\n"
        "    struct mm_struct *mm;      // NULL en hilos de kernel\n"
        "    // ... >100 campos más\n"
        "};\n"
        "```\n"
        "El código fuente está en `include/linux/sched.h`."
    ),
    14: (
        "**¿Por qué dos estados de sleep?**\n"
        "- `TASK_INTERRUPTIBLE`: espera un evento pero puede manejar señales. "
        "Ej: esperar input de terminal. `Ctrl+C` funciona.\n"
        "- `TASK_UNINTERRUPTIBLE`: espera hardware y no puede ser interrumpido por señales. "
        "Ej: esperar que un disco NFS responda. `kill -9` no funciona.\n\n"
        "**El estado 'D' en `ps aux`** corresponde a `TASK_UNINTERRUPTIBLE`. "
        "Un proceso en estado D que no avanza suele indicar un problema de hardware "
        "(disco roto, NFS caído). No puede matarse con señales."
    ),
    15: (
        "**`clone()` — la syscall más poderosa de Linux:**\n"
        "Todo mecanismo de concurrencia en Linux se construye sobre ella:\n\n"
        "| Llamada | Flags de clone() | Resultado |\n"
        "|---|---|---|\n"
        "| `fork()` | ninguno | Proceso hijo aislado (COW) |\n"
        "| `pthread_create()` | VM + FILES + THREAD + SIGHAND | Hilo POSIX |\n"
        "| `vfork()` | VM + VFORK | Proceso hijo sin copia |\n"
        "| `unshare()` | NEWPID + NEWNET + ... | Nuevo namespace |\n\n"
        "**La pila siempre es privada:** `clone()` requiere que el llamador suministre "
        "una pila nueva para el hijo. No hay forma de compartir la pila."
    ),
    16: (
        "**Docker usa exactamente `clone()` con flags de namespace:**\n"
        "```bash\n"
        "# Conceptualmente, docker run hace:\n"
        "clone(fn, stack, CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWNS |\n"
        "           CLONE_NEWUTS | CLONE_NEWIPC, args)\n"
        "# + configurar cgroups para limitar CPU/memoria\n"
        "```\n"
        "No hay hipervisor ni virtualización de hardware. Es puro Linux.\n\n"
        "**Diferencia clave Namespaces vs cgroups:**\n"
        "- **Namespaces** → aíslan lo que el proceso **ve** (su visión del sistema)\n"
        "- **cgroups** → limitan lo que el proceso puede **consumir** (CPU, RAM, I/O)\n"
        "Juntos = contenedores sin VM."
    ),
    17: (
        "**Sandboxing de Android — más estricto que iOS en un aspecto:**\n"
        "Cada app tiene un UID de Linux único. El kernel fuerza el aislamiento a nivel de SO, "
        "no solo a nivel de runtime. Incluso con root, cruzar límites de app requiere "
        "vulnerabilidades del kernel.\n\n"
        "**Binder IPC:** el mecanismo de comunicación entre apps. "
        "Más eficiente que pipes o sockets (una sola copia en memoria vs dos). "
        "Toda la comunicación inter-componente (startActivity, bindService) usa Binder."
    ),
    18: (
        "**Ciclo de vida de Activity — errores comunes de desarrollo:**\n"
        "1. **No guardar estado en `onPause()`:** si el SO mata la Activity, el usuario pierde progreso\n"
        "2. **Hacer trabajo lento en el hilo principal:** congela la UI → Android muestra \"App no responde\"\n"
        "3. **Memory leaks:** referenciar la Activity desde un callback en background que sobrevive a ella\n\n"
        "**`onSaveInstanceState(Bundle)`:** se llama antes de `onStop()`. "
        "Permite guardar estado que se restaura en `onCreate(savedInstanceState)` "
        "si la Activity es recreada (ej. al rotar la pantalla o por presión de memoria)."
    ),
    19: (
        "**Low Memory Killer (LMK) de Android:**\n"
        "Es un componente del kernel que activa la eliminación de procesos cuando la memoria libre "
        "cae por debajo de umbrales configurables:\n"
        "- Umbral 1 (minfree[0]): elimina procesos vacíos\n"
        "- Umbral 2: elimina procesos en segundo plano\n"
        "- Umbral 3: elimina servicios\n"
        "- Umbral 4 (emergencia): elimina procesos visibles\n\n"
        "**El sistema de prioridades** implementa directamente los principios de diseño de SO: "
        "maximizar la experiencia del usuario priorizando lo que ve y con lo que interactúa."
    ),
    20: (
        "**GCD — paradigma orientado a tareas vs orientado a hilos:**\n"
        "- **Orientado a hilos (tradicional):** `pthread_create()`, el programador gestiona hilos\n"
        "- **Orientado a tareas (GCD):** `dispatch_async()`, el programador describe trabajo; "
        "el SO asigna hilos automáticamente\n\n"
        "**Ventaja de GCD:** el pool de hilos se adapta al hardware. "
        "El mismo código corre eficientemente en un iPhone con 2 núcleos y en un Mac Pro con 24.\n\n"
        "**Bloque = función + contexto capturado:**\n"
        "```objc\n"
        "int x = 42;\n"
        "dispatch_async(queue, ^{\n"
        "    NSLog(@\"x = %d\", x);  // x capturado por valor\n"
        "});\n"
        "```"
    ),
    21: (
        "**La regla fundamental de UI en frameworks modernos:**\n"
        "La cola serial del hilo principal garantiza que la UI se actualice desde un único hilo. "
        "Esta regla existe en todos los frameworks:\n"
        "- GCD/Cocoa: `dispatch_get_main_queue()`\n"
        "- Android: `runOnUiThread()` o `Handler(Looper.getMainLooper())`\n"
        "- Windows Win32: `PostMessage()` al hilo principal\n"
        "- JavaFX: `Platform.runLater()`\n\n"
        "**¿Por qué?** Los frameworks de UI no son thread-safe. "
        "Actualizar un widget desde un hilo de background produce comportamiento indefinido "
        "(crashes, corrupción visual, condiciones de carrera)."
    ),
    22: (
        "**Síntesis comparativa para el examen:**\n\n"
        "| SO | Primitiva base | Modelo | Distingue hilo/proceso |\n"
        "|---|---|---|---|\n"
        "| Windows | `CreateThread()` | Proceso + Hilo + Fibra + UMS | Sí |\n"
        "| Solaris | `thr_create()` | ULT→LWP→KT→CPU (1:1 en Sol.9+) | Sí |\n"
        "| Linux | `clone()` | `task_struct` unificado | No |\n"
        "| Android | Java threads / NDK | Proceso Linux + VM | Sí |\n\n"
        "**¿Por qué Linux no distingue hilo/proceso?** "
        "`clone()` permite cualquier grado de compartición. "
        "El planificador CFS trata todas las `task_struct` igual."
    ),
    23: (
        "**Definiciones clave para el examen:**\n\n"
        "- **Jacketing:** envolver llamadas bloqueantes para que no bloqueen el proceso entero. "
        "Necesario solo con hilos en user space.\n"
        "- **LWP (Lightweight Process):** en Solaris, entidad que mapea ULT a hilo de kernel. "
        "En Linux, el término se usa informalmente para hilos de kernel.\n"
        "- **UMS:** permite cambiar entre hilos de un proceso sin involucrar al kernel "
        "(Windows 7+). Similar a goroutines de Go.\n"
        "- **Grupo de Hilos:** pool precreado de hilos esperando trabajo. "
        "Evita el overhead de creación/destrucción repetida."
    ),
    24: "",  # Portada final — sin nota
    25: (
        "**La asíntota de la Ley de Amdahl:**\n"
        "A medida que N → ∞, la aceleración → 1/(1-f).\n"
        "Con f=0.90: límite = 10×, con f=0.99: límite = 100×.\n\n"
        "**Rendimientos decrecientes:** la curva se aplana rápidamente. "
        "Pasar de 1 a 2 CPUs con f=0.9 da 1.82× (ganancia del 82%). "
        "Pasar de 8 a 16 CPUs solo da de 4.71× a 6.40× (ganancia adicional del 36%).\n\n"
        "**Implicación de diseño:** invertir en reducir la fracción serial "
        "siempre supera el beneficio de agregar más núcleos."
    ),
    26: (
        "**Clave del diseño híbrido de Valve:**\n"
        "La estrategia no es 'paralelizar todo' sino 'fijar lo predecible y paralelizar lo costoso'.\n\n"
        "- **Audio (fijo a 1 CPU):** el audio digital es extremadamente sensible al timing. "
        "Mezclar en un solo hilo garantiza latencia determinista sin locks.\n"
        "- **Renderizado (paralelo por objeto):** cada objeto puede renderizarse independientemente. "
        "Alta independencia de datos → casi sin contención en locks.\n\n"
        "**Resultado práctico:** ≥60 fps estables en hardware quad-core "
        "vs ~20 fps en versión single-threaded del mismo motor."
    ),
    27: (
        "**La separación proceso/hilo en Windows es más estricta que en Linux:**\n"
        "Un proceso Windows sin hilos no puede ejecutar ninguna instrucción. "
        "Cuando se crea un proceso (`CreateProcess()`), Windows crea automáticamente un hilo principal.\n\n"
        "**Handles vs punteros:** los procesos en Windows nunca tienen punteros directos a objetos del kernel. "
        "Usan handles (índices en la tabla de handles del proceso). "
        "Esto garantiza que cuando un proceso termina, "
        "todos sus handles se cierran automáticamente y los objetos se liberan."
    ),
    28: (
        "**¿Cuándo ocurre el estado Transición en producción?**\n"
        "En sistemas con alta carga de memoria, las pilas de hilos bloqueados son "
        "candidatas a ser paginadas a disco (page out). "
        "Esto es más probable con muchos hilos en WAIT simultáneamente.\n\n"
        "**Diagnóstico:** el contador 'Threads - Transition' en Performance Monitor "
        "indica cuántos hilos están esperando que su pila vuelva de página.\n"
        "Un valor alto sugiere presión de memoria → considerar aumentar RAM o "
        "reducir el número de hilos activos simultáneamente."
    ),
    29: (
        "**Modelo de 4 niveles en Solaris 8 vs 9+:**\n"
        "- **Solaris 8 (M:N):** N ULTs → M LWPs → M KTs → CPUs. "
        "Un LWP podía servir a múltiples ULTs.\n"
        "- **Solaris 9+ (1:1):** cada ULT → 1 LWP → 1 KT → 1 CPU. "
        "Los LWPs son prácticamente transparentes para el programador.\n\n"
        "**¿Por qué el M:N fue abandonado en Solaris?**\n"
        "La complejidad de los bugs de sincronización entre el runtime de usuario y el kernel "
        "fue mayor que el beneficio de rendimiento. "
        "Con hardware moderno, el overhead de syscalls es mínimo."
    ),
    30: (
        "**Comparación del enfoque de interrupciones:**\n\n"
        "| Aspecto | Tradicional | Solaris (hilos) |\n"
        "|---|---|---|\n"
        "| Deshabilitar interrupciones | Global (todas las CPUs) | No necesario |\n"
        "| Costo en SMP | O(N CPUs) — IPI a todos | O(1) — mutex local |\n"
        "| Escalabilidad | Pobre en >4 CPUs | Lineal con CPUs |\n"
        "| Latencia | Baja (sin cambio de contexto) | Media (cambio de hilo) |\n"
        "| Unificación del modelo | Interrupciones = especiales | Todo es un hilo |\n\n"
        "Este enfoque influyó en el diseño de interrupciones en macOS/XNU (interrupt threads)."
    ),
    31: (
        "**Copy-on-Write (COW) en fork():**\n"
        "Al llamar a `fork()`, el hijo no recibe una copia inmediata de la memoria del padre. "
        "Las páginas se marcan como de solo lectura y se comparten entre padre e hijo. "
        "Solo cuando padre O hijo intenta escribir en una página, "
        "esa página específica se copia (copy-on-fault).\n\n"
        "**Ventaja:** `fork()` es casi tan rápido como `clone()` si el hijo llama a `exec()` "
        "inmediatamente (pattern fork+exec = ninguna copia real ocurre).\n\n"
        "**La pila nunca se comparte en `clone()`:** el llamador debe proporcionar "
        "una nueva pila para el hijo. En pthreads, la biblioteca gestiona esto automáticamente."
    ),
    32: (
        "**Docker internamente usa exactamente esta arquitectura:**\n"
        "```bash\n"
        "# Verificar namespaces de un contenedor Docker:\n"
        "docker run -d nginx\n"
        "CONTAINER_PID=$(docker inspect --format '{{.State.Pid}}' <id>)\n"
        "ls -la /proc/$CONTAINER_PID/ns/\n"
        "# Muestra: ipc, mnt, net, pid, user, uts — todos distintos del host\n"
        "```\n\n"
        "**Kubernetes** agrega orquestación sobre Docker/containerd, "
        "pero el aislamiento sigue siendo namespaces + cgroups del kernel Linux."
    ),
    33: (
        "**La pila de Activities = navegación de usuario:**\n"
        "El botón ATRÁS hace `pop()` en la pila de Activities, restaurando la Activity anterior. "
        "Las Activities debajo en la pila están en estado `STOPPED` (no destruidas), "
        "lo que hace la navegación de regreso instantánea.\n\n"
        "**Task vs Back Stack:** Android agrupa Activities en 'Tasks'. "
        "Cada app tiene su propia Back Stack, pero una Task puede mezclar Activities "
        "de diferentes apps (ej. abrir una Activity de Gmail desde tu app)."
    ),
    34: (
        "**La cola serial = event loop de un solo hilo:**\n"
        "La `dispatch_get_main_queue()` implementa el mismo patrón que el event loop de "
        "Node.js, el event loop de Qt, el RunLoop de Cocoa y el Looper de Android: "
        "un único hilo procesa eventos en orden FIFO.\n\n"
        "**Regla de oro:** nunca ejecutar trabajo que tome más de ~16ms en la cola principal "
        "(equivale a 60 fps). Trabajo más largo = frames perdidos = UI entrecortada.\n\n"
        "**`dispatch_after`:** programa trabajo en la cola principal después de un delay, "
        "sin bloquear el hilo principal."
    ),
    35: (
        "**Para preparar el examen — diferencias clave:**\n"
        "1. **Linux es el más flexible:** `clone()` puede crear cualquier combinación de "
        "compartición. No hay distinción conceptual entre proceso e hilo.\n"
        "2. **Windows es el más rico en abstracciones:** fibras, UMS, grupos de hilos, "
        "objetos de trabajo. Mayor complejidad, mayor control.\n"
        "3. **Solaris es el más estructurado:** 4 capas bien definidas, aunque hoy usa 1:1.\n"
        "4. **Android prioriza la experiencia del usuario:** el sistema mata agresivamente "
        "procesos de baja prioridad para mantener la fluidez de la app en primer plano.\n\n"
        "**Pregunta frecuente de examen:** compare `fork()` en Linux con `CreateProcess()` en Windows."
    ),
    36: (
        "**Síntesis del Capítulo 4:**\n"
        "Los cuatro SO representan cuatro filosofías de diseño:\n"
        "- **Windows:** orientado a objetos, abstracciones ricas, gran empresa\n"
        "- **Solaris:** POSIX estricto, modelo en capas, empresa/servidor\n"
        "- **Linux:** minimalismo elegante, una primitiva poderosa (`clone()`), universal\n"
        "- **Android:** optimizado para dispositivos con recursos limitados y batería\n\n"
        "**Conexión con Tanenbaum (mos.md):** los conceptos de hilos en user space, "
        "kernel y híbrido de la sección 2.2 son la base teórica de todas estas implementaciones. "
        "Linux usa kernel threads (2.2.5), Solaris usó híbrido (2.2.6) y Go usa activaciones del planificador (2.2.7)."
    ),
}


def add_notes(md_path: str, notes: dict) -> int:
    """Agrega notas de presentador a cada diapositiva del archivo Marp.
    Retorna el número de diapositivas anotadas."""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Dividir en partes usando el separador de diapositivas de Marp
    parts = re.split(r'\n---\n', content)

    # parts[0] = frontmatter YAML; diapositivas en parts[1:]
    annotated = 0
    new_parts = [parts[0]]  # YAML sin modificar

    for i, part in enumerate(parts[1:], start=1):
        note = notes.get(i, "")
        if note and note.strip():
            part = part.rstrip("\n") + f"\n\n<!--\n{note.strip()}\n-->\n"
            annotated += 1
        new_parts.append(part)

    new_content = "\n---\n".join(new_parts)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return annotated


def verify_format(md_path: str) -> list:
    """Verifica problemas de formato Marp. Retorna lista de advertencias."""
    warnings = []
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.splitlines()

    # 1. Frontmatter YAML presente
    if not content.startswith("---"):
        warnings.append("WARN: el archivo no empieza con '---' (frontmatter YAML)")

    # 2. marp: true presente
    if "marp: true" not in content:
        warnings.append("WARN: falta 'marp: true' en el frontmatter")

    # 3. Imágenes referenciadas existen
    base_dir = os.path.dirname(md_path)
    for m in re.finditer(r'!\[.*?\]\((.*?)\)', content):
        img_path = os.path.join(base_dir, m.group(1))
        if not os.path.exists(img_path):
            warnings.append(f"WARN: imagen no encontrada: {m.group(1)}")

    # 4. Notas de presentador bien cerradas (cada <!-- tiene su -->)
    opens = content.count("<!--")
    closes = content.count("-->")
    if opens != closes:
        warnings.append(f"WARN: comentarios HTML desbalanceados (<!-- × {opens} vs --> × {closes})")

    # 5. No hay bloques ```mermaid sin renderizar (en mos.md ya se convirtieron)
    mermaid_blocks = len(re.findall(r'```mermaid', content))
    if mermaid_blocks > 0:
        warnings.append(f"INFO: {mermaid_blocks} bloque(s) mermaid sin convertir a imagen")

    # 6. Contar diapositivas
    slides = len(re.split(r'\n---\n', content)) - 1  # -1 por el frontmatter
    return warnings, slides


if __name__ == "__main__":
    for fname, notes in [("mos.md", MOS_NOTES), ("osid.md", OSID_NOTES)]:
        path = os.path.join(BASE_DIR, fname)
        print(f"\n{'='*50}")
        print(f"Procesando: {fname}")
        count = add_notes(path, notes)
        print(f"  Diapositivas anotadas: {count}")

        warnings, slides = verify_format(path)
        print(f"  Total diapositivas:    {slides}")
        if warnings:
            for w in warnings:
                print(f"  {w}")
        else:
            print("  Formato: OK (sin advertencias)")
