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

# Capítulo 4: Hilos
## Secciones 4.3 – 4.10
### Sistemas Operativos: Fundamentos y Diseño
#### William Stallings, 9.ª Edición

---

# 4.3 Multinúcleo y Multihilo

**Pregunta clave:** ¿Qué tan bien puede el software aprovechar múltiples núcleos?

### Ley de Amdahl

$$\text{Aceleración} = \frac{1}{(1-f) + \frac{f}{N}}$$

- `f` = fracción del código paralelizable
- `N` = número de procesadores
- Con **10% de código serial** y **8 procesadores** → solo **4.7× de aceleración**

> Incluso pequeñas fracciones seriales limitan significativamente el rendimiento

---

# 4.3 Rendimiento Multinúcleo en la Práctica

### ¿Por qué no se alcanza la aceleración teórica?
- Sobrecarga de comunicación entre procesadores
- Costos de coherencia de caché
- Sobrecarga de distribución y planificación del trabajo

### Categorías de aplicaciones que escalan bien:
- **Apps nativas multihilo** (ej. Lotus Domino, Siebel CRM)
- **Apps multiproceso** (ej. Oracle DB, SAP, PeopleSoft)
- **Aplicaciones Java** (la JVM es inherentemente multihilo)
- **Apps multi-instancia** (ejecutan varias copias independientes)

---

# 4.3 Caso de Estudio: Motor Source de Valve

Valve reprogramó el motor Source para explotar chips multinúcleo (Intel/AMD).

### Tres estrategias de enhebrado evaluadas:

| Estrategia | Descripción | Resultado |
|---|---|---|
| **Gruesa** | Un sistema por procesador (IA, renderizado, física…) | ~1.2× en la práctica |
| **Granularidad fina** | Dividir bucles en micro-tareas paralelas | Complejo, tiempos variables |
| **Híbrida** ✅ | Mezcla de ambas; enfoque elegido | Mejor escalabilidad |

- Mezcla de sonido → fijada a un solo CPU (sin interacción, autocontenida)
- Renderizado → distribuido jerárquicamente entre hilos

---

# 4.3 Enhebrado Híbrido – Módulo de Renderizado

Estructura jerárquica de hilos para el módulo de renderizado:

![renderizado-modulo](img/renderizado-modulo.png)

### Modelo de concurrencia clave:
- Bloqueo **un escritor / múltiples lectores**
- >95% del acceso a hilos es de **solo lectura** → alto paralelismo
- Solo ~5% requiere bloqueos de escritura

---

# 4.4 Gestión de Procesos e Hilos en Windows

### Conceptos de ejecución principales:

| Objeto | Descripción |
|---|---|
| **Proceso** | Espacio de direcciones virtual + recursos + al menos un hilo |
| **Hilo** | Unidad planificable; comparte memoria del proceso |
| **Objeto de Trabajo** | Gestiona grupos de procesos como una unidad |
| **Grupo de Hilos** | Hilos trabajadores para callbacks asíncronos |
| **Fibra** | Planificada manualmente; sin apropiación |
| **UMS** | Planificación en modo usuario; cambio de hilo sin involucrar al núcleo |

---

# 4.4 Atributos del Objeto Proceso en Windows

| Atributo | Descripción |
|---|---|
| ID de Proceso | Identificador único |
| Descriptor de Seguridad | Información de control de acceso |
| Prioridad Base | Prioridad de ejecución base |
| Afinidad de Procesador | Procesadores permitidos |
| Límites de Cuota | Máx. memoria, paginación, tiempo de CPU |
| Estado de Salida | Razón de terminación |

**Hilo de Windows** añade: Contexto del Hilo, Prioridad Dinámica, Estado de Alerta, Contador de Suspensión, Token de Suplantación

---

# 4.4 Estados de Hilo en Windows

![windows-estados-hilo](img/windows-estados-hilo.png)

1. **Listo** – puede ser planificado
2. **En Espera** – seleccionado para ejecutar en un procesador
3. **Ejecutando** – en ejecución actualmente
4. **Esperando** – bloqueado por evento, sincronización o suspensión
5. **Transición** – listo para correr pero recursos no disponibles
6. **Terminado** – finalizado; puede retenerse para reinicialización

---

# 4.4 Tareas en Segundo Plano (Windows 8/10)

### Nuevo modelo de ciclo de vida (apps Metro/Store):
- **Solo una app se ejecuta completamente** a la vez — las demás se **suspenden**
- El desarrollador debe **guardar el estado al suspender** y restaurarlo al reanudar
- Windows puede **terminar silenciosamente** apps en segundo plano para liberar memoria

### Límites de la API de tareas en segundo plano:
- Las tareas en segundo plano reciben solo **1 segundo de CPU por hora de CPU**
- Garantiza recursos a las apps en primer plano
- Notificaciones push entregadas vía **Servicio de Notificaciones de Windows (WNS)**

---

# 4.5 Gestión de Hilos y SMP en Solaris

### Modelo de hilos de cuatro niveles:

![solaris-4-niveles](img/solaris-4-niveles.png)

- **ULT** – creados por el usuario, invisibles al SO
- **LWP** – visible dentro del proceso; se mapea a un hilo del núcleo
- **Hilo del Núcleo** – entidad realmente planificable

---

# 4.5 Estados de Ejecución de Hilos en Solaris

![solaris-estados-hilo](img/solaris-estados-hilo.png)

| Estado | Significado |
|---|---|
| **RUN** | Ejecutable / listo |
| **ONPROC** | Ejecutándose en un procesador |
| **SLEEP** | Bloqueado (esperando un evento) |
| **STOP** | Suspendido (ej. para depuración) |
| **ZOMBIE** | Terminado, aún no limpiado |
| **FREE** | Recursos liberados, esperando eliminación |

---

# 4.5 Solaris: Interrupciones como Hilos

**Problema:** El manejo tradicional de interrupciones requiere bloquearlas durante accesos a datos del núcleo — costoso en multiprocesadores.

### Solución de Solaris:
1. Las interrupciones se convierten en **hilos del núcleo**
2. Los hilos de interrupción tienen **mayor prioridad** que todos los demás
3. El acceso a datos compartidos usa **primitivas de exclusión mutua** (igual que hilos normales)

### Beneficio:
- Elimina la necesidad de subir/bajar niveles de prioridad de interrupción
- Escala bien en sistemas multiprocesador
- Unifica el modelo de concurrencia: todo es un hilo del núcleo

---

# 4.6 Gestión de Procesos e Hilos en Linux

### La estructura `task_struct` contiene:
- **Estado** – ejecutando, listo, suspendido, detenido, zombie
- **Info de planificación** – normal/tiempo real, prioridad, contador de tiempo
- **Identificadores** – PID, ID de usuario, ID de grupo
- **Enlaces** – padre, hermanos, hijos
- **IPC** – semáforos, colas de mensajes
- **Temporizadores** – tiempo de creación, CPU consumida, temporizadores de intervalo
- **Sistema de archivos** – archivos abiertos, directorio actual/raíz
- **Espacio de direcciones** – mapa de memoria virtual
- **Contexto del procesador** – registros, pila

---

# 4.6 Estados de Proceso en Linux

![linux-estados-proceso](img/linux-estados-proceso.png)

| Estado | Descripción |
|---|---|
| **Ejecutando** | En ejecución o listo para ejecutar |
| **Interrumpible** | Bloqueado; puede manejar señales |
| **No Interrumpible** | Bloqueado en hardware; ignora señales |
| **Detenido** | Pausado; reanuda por acción externa |
| **Zombie** | Terminado; estructura `task_struct` aún en tabla |

---

# 4.6 Hilos en Linux: ¡Sin Distinción!

> Linux **no distingue** entre hilos y procesos — ambos son `task_struct`

### `clone()` vs `fork()`
- `fork()` = `clone()` con todos los flags en cero (copia completa)
- `clone()` permite compartir recursos:

| Flag | Efecto |
|---|---|
| `CLONE_VM` | Compartir memoria virtual |
| `CLONE_FILES` | Compartir descriptores de archivo |
| `CLONE_THREAD` | Mismo grupo de hilos que el padre |
| `CLONE_FS` | Compartir info del sistema de archivos |
| `CLONE_NEWPID` | Nuevo espacio de nombres PID |

---

# 4.6 Namespaces y cgroups en Linux

### 6 tipos de Namespaces:
`mnt` · `pid` · `net` · `ipc` · `uts` · `user`

- Cada proceso obtiene una **vista específica del sistema**
- Base de la **virtualización ligera** (Docker, LXC, Kubernetes)

### cgroups (Grupos de Control):
- Gestión de recursos: CPU, memoria, red, E/S
- Desarrollo iniciado en Google (2006) como "contenedores de proceso"
- `cgroups v2` lanzado en el núcleo 4.5 (2016) — interfaces consistentes
- Montado como sistema de archivos virtual en `/sys/fs/cgroup`
- Junto con namespaces → **Contenedores Linux**

---

# 4.7 Gestión de Procesos e Hilos en Android

### 4 Tipos de Componentes de Aplicación:

| Componente | Función |
|---|---|
| **Activity** | Pantalla de UI única; gestionada en pila LIFO |
| **Service** | Tareas en segundo plano (música, descargas) |
| **Content Provider** | Interfaz a datos de la app (privados o compartidos) |
| **Broadcast Receiver** | Responde a eventos del sistema |

**Modelo de sandboxing:** Cada app = su propio proceso + máquina virtual + ID de usuario Linux único

---

# 4.7 Estados de una Activity en Android

![android-estados-activity](img/android-estados-activity.png)

---

# 4.7 Jerarquía de Precedencia de Procesos en Android

Cuando la memoria es escasa, Android elimina procesos desde la **menor prioridad**:

| Prioridad | Tipo | Ejemplo |
|---|---|---|
| 1 (mayor) | **Primer plano** | Activity con la que interactúa el usuario |
| 2 | **Visible** | Activity visible pero sin foco |
| 3 | **Servicio** | Música en fondo, descarga de red |
| 4 | **Segundo plano** | Activity detenida |
| 5 (menor) | **Vacío** | Sin componentes activos; retenido para inicio rápido |

---

# 4.8 Grand Central Dispatch (GCD) de Mac OS X

**Objetivo:** Simplificar el multihilo; dejar que el SO gestione los grupos de hilos automáticamente.

### Bloques — la unidad de trabajo principal:
```c
x = ^{ printf("hola mundo\n"); }
x();  // invoca el bloque
```

Un bloque = **función + datos**, pasable como una variable: `F̄ = F + datos`

### Colas:
- **Cola concurrente** → bloques despachados cuando hay hilos disponibles
- **Cola serial** → bloques despachados uno tras otro (FIFO)
- Grupos de hilos **dimensionados automáticamente** por el SO

---

# 4.8 GCD en la Práctica

### Sin GCD (se ejecuta en el hilo principal — puede congelar la UI):
```objc
- (IBAction)analizarDocumento:(NSButton *)sender {
    NSDictionary *stats = [myDoc analyze];  // ¡puede ser lento!
    [myModel setDict:stats];
    [myStatsView setNeedsDisplay:YES];
}
```

### Con GCD (análisis en segundo plano; actualización de UI en cola principal):
```objc
dispatch_async(dispatch_get_global_queue(0, 0), ^{
    NSDictionary *stats = [myDoc analyze];
    dispatch_async(dispatch_get_main_queue(), ^{
        [myModel setDict:stats];
        [myStatsView setNeedsDisplay:YES];
    });
});
```

---

# 4.9 Resumen

| Tipo de Hilo | Ventajas | Desventajas |
|---|---|---|
| **Nivel de Usuario** | Sin cambio de modo; rápido | Solo uno ejecuta a la vez; bloqueo afecta al proceso |
| **Nivel de Núcleo** | Paralelismo real en multiprocesadores | Requiere cambio de modo en cada cambio de hilo |

### Distinciones clave:
- **Proceso** = propietario de recursos (espacio de direcciones, archivos, handles)
- **Hilo** = unidad de ejecución (planificable, comparte recursos del proceso)
- Los SO modernos difuminan esta línea (Linux) o la estructuran en capas (modelo de 4 niveles de Solaris)

---

# 4.10 Términos Clave

| Término | Definición |
|---|---|
| **Fibra** | Unidad planificada manualmente; sin apropiación |
| **Jacketing** | Envolver una llamada bloqueante para no bloquear todo el proceso |
| **Proceso Ligero (LWP)** | Mapea hilos de usuario a hilos del núcleo (Solaris) |
| **Namespaces** | Aíslan recursos del sistema por grupo de procesos |
| **Grupo de Hilos** | Hilos trabajadores precreados para tareas asíncronas |
| **UMS** | Planificación en Modo Usuario; cambio de hilo sin pasar por el núcleo |
| **Multihilo** | Múltiples hilos dentro de un mismo proceso |

---

<!-- _class: titulo -->

# Fin del Capítulo 4
## Hilos — De la Teoría a la Implementación en SO

> *«Un hilo es una unidad de trabajo despachable que se ejecuta secuencialmente y puede ser interrumpida.»*
> — Stallings, Sistemas Operativos: Fundamentos y Diseño

---

# 4.3 Diagrama: Ley de Amdahl Explicada

![amdahl-ley](img/amdahl-ley.png)

### ¿Por qué no escala perfectamente?
- La parte **serial siempre tarda lo mismo** sin importar cuántos núcleos haya
- A medida que `N → ∞`, la aceleración máxima está **limitada por `1/(1−f)`**
- Con 10% serial → aceleración máxima posible = **10×**, sin importar cuántos núcleos

---

# 4.3 Diagrama: Estrategias de Enhebrado en Valve

![valve-estrategias](img/valve-estrategias.png)

> La clave: fijar lo predecible, paralelizar lo costoso

---

# 4.4 Diagrama: Jerarquía de Objetos en Windows

![windows-jerarquia-objetos](img/windows-jerarquia-objetos.png)

- El proceso **no ejecuta código** por sí mismo — solo posee recursos
- **Los hilos** son quienes realmente ejecutan instrucciones
- Un proceso puede tener **múltiples hilos** ejecutando en paralelo

---

# 4.4 Diagrama: Ciclo de Vida de un Hilo en Windows

![windows-ciclo-hilo](img/windows-ciclo-hilo.png)

> **Transición** ocurre cuando el hilo está listo para correr pero su pila fue paginada a disco

---

# 4.5 Diagrama: Modelo de 4 Niveles de Solaris

![solaris-4-niveles-detalle](img/solaris-4-niveles-detalle.png)

> Cada LWP se mapea **exactamente a un** hilo del núcleo (Solaris 9+)

---

# 4.5 Diagrama: Interrupciones como Hilos en Solaris

![solaris-interrupciones](img/solaris-interrupciones.png)

---

# 4.6 Diagrama: `fork()` vs `clone()` en Linux

![linux-fork-clone](img/linux-fork-clone.png)

> La pila **nunca se comparte** — `clone()` crea espacios de pila separados

---

# 4.6 Diagrama: Namespaces y Contenedores Linux

![linux-namespaces](img/linux-namespaces.png)

- **Namespaces** → cada contenedor cree que es el único en el sistema
- **cgroups** → limitan cuántos recursos puede consumir cada contenedor
- Juntos = **aislamiento + control de recursos** sin una VM completa

---

# 4.7 Diagrama: Pila de Activities en Android

![android-pila-activities](img/android-pila-activities.png)

---

# 4.8 Diagrama: Colas en Grand Central Dispatch

![gcd-colas](img/gcd-colas.png)

> La cola serial del hilo principal garantiza que la **UI solo se actualice desde un hilo**

---

# Comparación General: Hilos entre Sistemas Operativos

| Característica | Windows | Solaris | Linux | Android |
|---|---|---|---|---|
| **Modelo de hilos** | Proceso + Hilo + Fibra | ULT → LWP → Hilo núcleo | `task_struct` unificado | Proceso + VM dedicada |
| **¿Distingue hilo/proceso?** | Sí | Sí (4 niveles) | No | Sí (sandboxing) |
| **Planificación** | Kernel (6 estados) | Kernel (por hilo núcleo) | Kernel (CFS) | Kernel Linux + jerarquía |
| **Interrupciones** | Rutinas del núcleo | Hilos del núcleo | Rutinas del núcleo | Rutinas del núcleo |
| **Virtualización ligera** | Hyper-V | Zonas | Namespaces + cgroups | Máquina virtual Dalvik/ART |
| **API de hilos** | Win32 / UMS | POSIX pthreads | `clone()` / pthreads | Java threads / NDK |

> Linux es el más flexible (sin distinción hilo/proceso); Solaris el más estructurado (4 capas)

---

# Resumen Visual: Todo el Capítulo 4

![capitulo4-mindmap](img/capitulo4-mindmap.png)
