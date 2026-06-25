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
    font-size: 0.7em;
    line-height: 1.4;
  }
  table {
    border-collapse: collapse;
    font-size: 0.75em;
    width: 100%;
  }
  th {
    background: #0055b3;
    color: white;
    padding: 8px;
  }
  td {
    border: 1px solid #d0d7de;
    padding: 6px;
  }
  img {
    max-width: 90%;
    max-height: 420px;
    display: block;
    margin: 0 auto;
  }
  .columns {
    display: flex;
    gap: 20px;
  }
  .col {
    flex: 1;
  }
  .small-code pre {
    font-size: 0.55em;
  }
  .compact li {
    margin-bottom: 3px;
    font-size: 0.8em;
  }
  .compact p {
    margin: 4px 0;
  }
---

# **Capítulo 5: Concurrencia**

## Exclusión Mutua y Sincronización

### William Stallings — Operating Systems: Internals and Design Principles (9ª Ed.)

---

# **Contenido del Capítulo**

1. **Exclusión Mutua:** Enfoques de Software
2. **Principios de Concurrencia**
3. **Exclusión Mutua:** Soporte Hardware
4. **Semáforos**
5. **Monitores**
6. **Paso de Mensajes**
7. **Problema de Lectores/Escritores**

![bg right:35% 90%](img/ch5-page-0223.jpg)

<!--
**Estructura del capítulo:** el capítulo 5 avanza de lo más básico (software) a lo más abstracto (monitores, mensajes). Cada mecanismo resuelve las limitaciones del anterior:

1. **Software (Dekker, Peterson):** demuestran que el problema es soluble sin hardware especial, pero son imprácticos para sistemas reales (busy waiting).
2. **Hardware (C&S, XCHG):** solución atómica a nivel de ISA, pero aún con busy waiting.
3. **Semáforos:** abstracción que elimina busy waiting usando colas de bloqueo.
4. **Monitores:** encapsulan datos + sincronización en una estructura.
5. **Mensajes:** permiten concurrencia en sistemas distribuidos sin memoria compartida.
-->

---

# **Objetivos de Aprendizaje**

- Discutir conceptos básicos de concurrencia: **condiciones de carrera**, preocupaciones del SO, requisitos de exclusión mutua
- Comprender **enfoques hardware** para soportar exclusión mutua
- Definir y explicar **semáforos**
- Definir y explicar **monitores**
- Explicar el **problema de lectores/escritores**

<!--
**Mapa conceptual para el estudiante:**
- Condiciones de carrera → ¿por qué ocurren? → intercalación no determinista de instrucciones
- Exclusión mutua → ¿cómo se garantiza? → mecanismos de software/hardware/semáforos
- Sincronización → ¿cómo coordinar eventos? → semáforos, monitores, mensajes

**Conexión con capítulos anteriores:** en el capítulo 4 vimos que los hilos comparten el espacio de direcciones del proceso. Ahora veremos cómo proteger ese espacio compartido de condiciones de carrera.
-->

---

# **Multiprogramación, Multiprocesamiento y Procesamiento Distribuido**

La concurrencia surge de tres entornos distintos, cada uno con sus propios retos:

| Entorno | Descripción |
|:--------|:------------|
| **Multiprogramación** (Uniprocesador) | Varios procesos comparten una sola CPU. La concurrencia se logra por **intercalación** — el SO multiplexa la CPU entre procesos. |
| **Multiprocesamiento** (SMP) | Dos o más CPUs comparten memoria física. La concurrencia es **real**: los procesos ejecutan simultáneamente en distintas CPUs. |
| **Procesamiento Distribuido** | Sistemas autónomos conectados por red, cada uno con su propia memoria. La concurrencia es **distribuida**: no hay memoria compartida física. |

<!--
**Multiprogramación, Multiprocesamiento y Procesamiento Distribuido — introducción conceptual:**
Esta diapositiva establece la base para entender por qué la concurrencia es importante: surge naturalmente de tres entornos computacionales distintos.

**Multiprogramación (uniprocesador):**
- Varios procesos se ejecutan en una sola CPU
- El SO intercala la ejecución (planificación)
- La concurrencia es aparente, no real
- Reto: condiciones de carrera entre procesos que comparten memoria

**Multiprocesamiento (SMP — Symmetric MultiProcessing):**
- Múltiples CPUs comparten memoria física
- Los procesos ejecutan simultáneamente en distintas CPUs
- Reto: coherencia de caché, acceso concurrente real a memoria compartida

**Procesamiento Distribuido:**
- Sistemas independientes conectados por red
- Cada sistema tiene su propia memoria
- Reto: coordinación sin memoria compartida, latencia de red, fallos parciales

**Mnemotecnia para el examen:** estos tres entornos representan un espectro de compartición: máxima (multiprogramación) → media (multiprocesamiento) → mínima (distribuido).
-->

---

# **Comparación de Entornos de Concurrencia**

| Característica | Multiprogramación | Multiprocesamiento | Distribuido |
|:---------------|:-----------------:|:------------------:|:-----------:|
| **# de CPUs** | 1 | 2+ | Múltiples sistemas |
| **Memoria** | Compartida | Compartida | Independiente (red) |
| **Paralelismo real** | No | Sí | Sí |
| **Sincronización** | Variables compartidas | Variables compartidas + coherencia caché | Paso de mensajes |
| **Escalabilidad** | Limitada (1 CPU) | Buena (hasta decenas de CPUs) | Excelente (centenares de nodos) |
| **Complejidad** | Baja-media | Media-alta | Alta (fallos parciales, red) |

<!--
**Tabla comparativa — ¿qué cambia entre los tres entornos?:**
Esta tabla es útil para entender las diferencias fundamentales.

**Para discusión en clase:**
- En multiprogramación, la exclusión mutua se resuelve fácilmente deshabilitando interrupciones (solo 1 CPU)
- En multiprocesamiento, necesitamos instrucciones atómicas como C&S porque dos procesos pueden ejecutar simultáneamente
- En distribuido, ni siquiera hay memoria compartida — necesitamos paso de mensajes o transacciones distribuidas

**Nota histórica:** Stallings organiza el capítulo 5 en torno a estos tres paradigmas. Las soluciones software (Dekker, Peterson) asumen multiprogramación. El soporte hardware (C&S) es necesario para multiprocesamiento. El paso de mensajes surge del procesamiento distribuido.
-->

---

# **Implicaciones para la Concurrencia**

**¿Por qué estudiar estos tres escenarios juntos?**

1. **Principios unificados:** los conceptos de exclusión mutua, sincronización y condiciones de carrera son universales —aparecen en los tres entornos.
2. **Mecanismos específicos:** cada entorno requiere mecanismos adaptados:
   - Multiprogramación → semáforos, monitores
   - Multiprocesamiento → instrucciones atómicas (C&S, XCHG)
   - Distribuido → paso de mensajes, bloqueos distribuidos
3. **Evolución histórica:** los SO modernos combinan los tres. Un servidor actual ejecuta multiprogramación (muchos procesos), multiprocesamiento (varios núcleos) y procesamiento distribuido (comunicación entre servidores).

![bg right:30% 80%](img/ch5-page-0223.jpg)

<!--
**Implicaciones para la concurrencia — ¿por qué es importante esta clasificación?:**

Esta diapositiva cierra la introducción conceptual y conecta con la estructura del capítulo.

**Para ayudar a los estudiantes a ver el panorama general:**
Cada mecanismo del capítulo 5 está diseñado para uno o más de estos entornos:
1. Los algoritmos de software (Peterson, Dekker) asumen multiprogramación en uniprocesador
2. C&S y XCHG fueron diseñados para multiprocesamiento SMP
3. Los monitores funcionan en multiprogramación y multiprocesamiento
4. El paso de mensajes es la única opción para sistemas distribuidos

**Conexión con el contenido del capítulo:** la tabla de contenido (diapositiva 2) ahora tiene más sentido — cada sección del capítulo corresponde a uno de estos entornos.

**Pregunta de reflexión:** ¿qué mecanismo usarías para sincronizar dos hilos del mismo proceso? ¿Y para dos procesos en distintas máquinas?
-->

---

<!-- _class: lead -->
# **1. Exclusión Mutua: Enfoques de Software**

---

# **El Problema de la Exclusión Mutua**

- Múltiples procesos compiten por el mismo recurso
- Solo **un proceso** puede estar en su **sección crítica** a la vez
- Se necesita garantizar que ningún otro proceso acceda al recurso compartido mientras un proceso lo está usando

### Términos Clave

| Término | Definición |
|---|---|
| **Sección crítica** | Código que accede a recursos compartidos |
| **Carrera (race condition)** | Resultado depende del orden de ejecución |
| **Bloqueo mutuo (deadlock)** | Procesos esperando indefinidamente |
| **Inanición (starvation)** | Proceso nunca accede al recurso |

<!--
**Motivación para la sección:** antes de ver soluciones hardware o del SO, es importante entender por qué el problema es difícil. Los primeros intentos (variable turn, flag[]) muestran cómo soluciones aparentemente correctas fallan.

**Términos clave para el examen:**
- **Sección crítica:** segmento de código que accede a recurso compartido
- **Race condition:** el resultado depende del orden de ejecución (interleaving)
- **Deadlock:** procesos esperándose mutuamente para siempre
- **Starvation:** un proceso nunca accede al recurso mientras otros sí

**Pregunta de reflexión:** ¿podemos resolver la exclusión mutua solo con variables compartidas y sin instrucciones atómicas especiales?
-->

---

# **Tabla 5.1 — Términos Clave Relacionados con Concurrencia**

| Término | Definición |
|:--------|:-----------|
| **Sección crítica** | Segmento de código que accede a un recurso compartido; solo un proceso puede ejecutarla a la vez |
| **Condición de carrera (race condition)** | Situación donde el resultado depende del orden no determinista de ejecución (interleaving) de los procesos |
| **Bloqueo mutuo (deadlock)** | Dos o más procesos se esperan mutuamente para siempre, ninguno puede progresar |
| **Inanición (starvation)** | Un proceso nunca accede al recurso porque otros lo toman siempre antes |

<!--
**Tabla 5.1 — análisis de términos:**
Esta tabla unifica la terminología que se usará en todo el capítulo. Es importante que los estudiantes memoricen estos cuatro términos.

**Diferencias sutiles:**
- Deadlock vs starvation: en deadlock **todos** los procesos esperan; en starvation **solo uno** espera mientras otros progresan.
- Deadlock es siempre un interbloqueo; starvation es una postergación indefinida.

**Nota histórica:** el término 'race condition' fue acuñado informalmente en los años 70 para describir bugs en sistemas multihilo tempranos de UNIX.
-->

---

# **Primer Intento — Variable turn**

```c
/* PROCESS 0 */               /* PROCESS 1 */
while (turn != 0)             while (turn != 1)
  /* do nothing */ ;            /* do nothing */;
/* critical section */;       /* critical section */;
turn = 1;                     turn = 0;
```

**Problemas:**
- Garantiza exclusión mutua
- **Alternancia estricta** — proceso lento dicta el ritmo
- Si un proceso falla, el otro queda **bloqueado permanentemente**

---

**Secuencia de fallo (alternancia estricta — viola progreso):**

| Paso | P0 | P1 | `turn` |
|:----:|:---|:---|:------:|
| 1 | `while(turn≠0)` → turn=0 → sale, **entra a SC** | — | 0 |
| 2 | **Sección Crítica** | — | 0 |
| 3 | `turn = 1` — pasa el turno | — | → **1** |
| 4 | Código restante | Código restante (no necesita SC) | 1 |
| 5 | **Quiere reingresar a SC** | — | 1 |
| 6 | `while(turn≠0)` → turn=1 → **BLOQUEADO** | — | 1 |
| 7 | **↑ P0 bloqueado esperando** a que P1 entre y salga de SC | Sigue con código restante, sin necesitar SC | 1 |
| 8 | Espera innecesaria... | ...nunca entra a SC, turn nunca cambia | 1 |
| ⋮ | **P0 no progresa** aunque P1 no necesita el recurso | — | 1 |

<div style="font-size:0.75em; color:#666; margin-top:6px;">P0 no puede reingresar a SC porque P1 debe ceder el turno primero. Alternancia estricta viola el requisito #4.</div>


<!--
**Primer intento — análisis detallado:**

Funciona como un 'turno' en un juego de mesa: un proceso espera hasta que sea su turno.

Garantiza exclusión mutua porque la variable `turn` solo puede tener un valor a la vez.

**Problemas fundamentales:**
1. **Alternancia estricta:** si P0 entra a SC y sale, y quiere entrar inmediatamente otra vez, no puede —debe esperar a que P1 también entre y salga. Esto viola el requisito #4 (un proceso fuera de SC no debe interferir).
2. **Fallo catastrófico:** si P0 termina dentro de SC y nunca ejecuta `turn = 1`, P1 queda bloqueado permanentemente. Esto es peor que un deadlock típico porque no hay forma de recuperación.

**Analogía didáctica:** un semáforo peatonal que alterna estrictamente — si nadie cruza, los carros igual deben esperar su turno aunque no haya peatones.
-->


---

# **Segundo Intento — Vector flag[]**

```c
/* PROCESS 0 */               /* PROCESS 1 */
while (flag[1])               while (flag[0])
  /* do nothing */;             /* do nothing */;
flag[0] = true;               flag[1] = true;
/* critical section */;       /* critical section */;
flag[0] = false;              flag[1] = false;
```

**Problema:**
**No garantiza exclusión mutua** — ambos procesos pueden entrar si se intercalan correctamente
Si un proceso falla dentro de la sección crítica, el otro se bloquea

---

**Secuencia de fallo (race condition — viola exclusión mutua):**

| Paso | P0 | P1 | `flag[0]` | `flag[1]` |
|:----:|:---|:---|:---------:|:---------:|
| 1 | `while(flag[1])` → flag[1]=false → **sale del bucle** | — | false | false |
| 2 | **⇨ ¡Cambio de contexto!** P0 interrumpido justo aquí ⇨ | — | false | false |
| 3 | — | `while(flag[0])` → flag[0]=false → **sale del bucle** | false | false |
| 4 | — | `flag[1] = true` — **marca intención** | false | → **true** |
| 5 | — | **Sección Crítica** ← ¡P1 entra! | false | true |
| 6 | — | *(P1 dentro de SC)* | false | true |
| 7 | *(P0 reanuda)* `flag[0] = true` — **marca intención** | *(P1 en SC)* | → **true** | true |
| 8 | **Sección Crítica** ← ¡P0 también entra! | *(P1 aún en SC)* | true | true |



<!--
**Segundo intento — el error de diseño:**


Aquí cada proceso declara su intención de entrar (`flag[i] = true`) **después** de verificar que el otro no está interesado. El error es el orden de las operaciones.

**Escenario de fallo (race condition):**
1. P0: `while (flag[1])` → flag[1]=false → sale del while
2. **Cambio de contexto a P1**
3. P1: `while (flag[0])` → flag[0]=false → sale del while
4. P0: `flag[0] = true`
5. P1: `flag[1] = true`
6. ¡Ambos entran a SC simultáneamente!

**Lección:** verificar y luego marcar no es atómico. Entre la verificación y la marcación puede ocurrir un cambio de contexto.
-->

---

# **Tercer Intento — flag[] antes del while**

```c
/* PROCESS 0 */               /* PROCESS 1 */
flag[0] = true;               flag[1] = true;
while (flag[1])               while (flag[0])
  /* do nothing */;             /* do nothing */;
/* critical section */;       /* critical section */;
flag[0] = false;              flag[1] = false;
```

**Problema:**
Garantiza exclusión mutua
**Interbloqueo (deadlock)** — ambos se ponen en true simultáneamente

---

**Secuencia de fallo (deadlock — ambos esperan al otro):**

| Paso | P0 | P1 | `flag[0]` | `flag[1]` |
|:----:|:---|:---|:---------:|:---------:|
| 1 | `flag[0] = true` — **marca intención** | — | → **true** | false |
| 2 | — | `flag[1] = true` — **marca intención** | true | → **true** |
| 3 | `while(flag[1])` → flag[1]=true → **espera que P1 salga** | — | true | true |
| 4 | — | `while(flag[0])` → flag[0]=true → **espera que P0 salga** | true | true |
| 5 | **↑ P0 espera que P1 ponga flag[1]=false** | **↑ P1 espera que P0 ponga flag[0]=false** | true | true |
| 6 | Pero P1 **no puede** salir de su while (flag[0]=true) | Pero P0 **no puede** salir de su while (flag[1]=true) | true | true |
| ⋮ | **DEADLOCK** — nadie progresa | **DEADLOCK** — nadie progresa | true | true |

<div style="font-size:0.1em; color:#666; margin-top:3px;">P0 espera que P1 baje flag[1]; P1 espera que P0 baje flag[0]. Ninguno puede bajar su propio flag porque está atrapado en el while. Deadlock clásico: deadly embrace.</div>


<!--
**Tercer intento — deadlock por inversión de orden:**


Corrige el error anterior: ahora cada proceso marca su intención **antes** de verificar.

Garantiza exclusión mutua — si ambos marcan, ambos ven el flag del otro en true y ambos esperan.

**Deadlock:** si los dos procesos ejecutan `flag[0]=true` y `flag[1]=true` antes de llegar al while, ambos quedan atrapados:
- P0: `while (flag[1])` → flag[1]=true → espera
- P1: `while (flag[0])` → flag[0]=true → espera
- Ninguno puede avanzar porque `flag` del otro nunca cambiará.

**Patrón clásico:** este es el mismo principio del abrazo mortal (deadly embrace) que veremos más adelante en el capítulo sobre deadlocks.
-->

---

# **Cuarto Intento — Con retirada**

```c
/* PROCESS 0 */                    /* PROCESS 1 */
flag[0] = true;                    flag[1] = true;
while (flag[0]) {                  while (flag[1]) {
  flag[0] = false;                   flag[1] = false;
  /*delay */;                        /*delay */;
  flag[0] = true;                    flag[1] = true;
}                                  }
/* critical section */;            /* critical section */;
flag[0] = false;                   flag[1] = false;
```

**Problema:**
- Exclusión mutua garantizada
- **Livelock** — posibilidad de ciclo indefinido de cortesía mutua

---

**Secuencia de fallo (livelock — cortesía mutua, nadie avanza):**

| Paso | P0 | P1 | `flag[0]` | `flag[1]` |
|:----:|:---|:---|:---------:|:---------:|
| 1 | `flag[0]=true` → while(flag[1])→ lo ve=true | — | → **true** | false |
| 2 | — | `flag[1]=true` → while(flag[0])→ lo ve=true | true | → **true** |
| 3 | `flag[0]=false` — **cede el paso** | — | → **false** | true |
| 4 | `delay` — espera un momento | — | false | true |
| 5 | — | `flag[1]=false` — **cede el paso** | false | → **false** |
| 6 | — | `delay` — espera un momento | false | false |
| 7 | `flag[0]=true` — **reintenta** | — | → **true** | false |
| 8 | — | `flag[1]=true` — **reintenta** | true | → **true** |
| 9 | `while(flag[1])` → **sigue true** | — | true | true |
| 10 | — | `while(flag[0])` → **sigue true** | true | true |
| ⋮ | **↑ Vuelve al paso 3** — ciclo infinito | **↑ Vuelve al paso 3** — ciclo infinito | ⋮ | ⋮ |

---

<div style="font-size:0.75em; color:#666; margin-top:6px;">Ambos se retiran al mismo tiempo, esperan el mismo delay, y vuelven a encontrarse en la misma situación. Livelock: los procesos cambian de estado (alternan true/false) pero nunca progresan a SC. Es como dos personas que se apartan al mismo lado repetidamente en un pasillo.</div>


<!--
**Cuarto intento — livelock corrección temporal pero no definitiva:**


La 'retirada' (backoff) rompe el deadlock: si ambos ven ocupado, ceden el paso y reintentan. Pero esto introduce un nuevo problema.

**Livelock:** ambos procesos ejecutan el ciclo simultáneamente:
1. P0: flag[0]=true → while flag[1] → flag[0]=false → delay → flag[0]=true
2. P1: flag[1]=true → while flag[0] → flag[1]=false → delay → flag[1]=true
3. Se repite indefinidamente si los delays son iguales.

**Solución al livelock:** delays aleatorios (backoff exponencial) — técnica que se usa en Ethernet (CSMA/CD) y en algoritmos de locks.

**Analogía:** dos personas que se encuentran en un pasillo y ambos se mueven al mismo lado repetidamente para dejarse pasar.
-->

---

# **Figura 5.1 — Intentos de Exclusión Mutua**

| Intento | Propiedad violada |
|:--------|:-----------------|
| **1 (turn)** | Progreso si un proceso se detiene fuera de SC |
| **2 (flag después)** | Exclusión mutua |
| **3 (flag antes)** | Ausencia de deadlock |
| **4 (backoff)** | Ausencia de livelock |

> Ningún intento satisface los 5 requisitos. Para eso necesitamos Dekker o Peterson.

---

![w:140%](img/mutual_exclusion_attempts.svg)


<!--
**Figura 5.1 — resumen de los 4 intentos:**
Esta figura muestra visualmente por qué cada intento falla. Es útil para el examen: entender qué propiedad viola cada uno.

| Intento | Propiedad violada |
|---------|-------------------|
| 1 (turn) | Progreso si un proceso se detiene fuera de SC |
| 2 (flag después) | Exclusión mutua |
| 3 (flag antes) | Ausencia de deadlock |
| 4 (backoff) | Ausencia de livelock |

**Nota:** ningún intento satisface los 5 requisitos. Para eso necesitamos Dekker o Peterson.
-->

---

# **Algoritmo de Dekker**

Combina **flag[]** (deseo) y **turn** (derecho a insistir):

```c
void P0() {
  while (true) {
    flag[0] = true;
    while (flag[1]) {
      if (turn == 1) {
        flag[0] = false;
        while (turn == 1) /* do nothing */;
        flag[0] = true;
      }
    }
    /* critical section */
    turn = 1;
    flag[0] = false;
  }
}
```
**Características:** Exclusión mutua. Sin deadlock. Progreso garantizado

<!--
**Regla #1:** flag[] indica **deseo** de entrar, turn decide **quién insiste** cuando hay conflicto.
**Regla #2:** Si ambos quieren entrar, el que **NO tiene el turno** retrocede temporalmente (cede el paso).
-->

<!--
**Algoritmo de Dekker — solución histórica:**

Publicado por Th. J. Dekker en 1965, es la **primera solución correcta documentada** al problema de la exclusión mutua para 2 procesos.

**Lógica de funcionamiento:**
1. `flag[i]` indica que el proceso i quiere entrar
2. `turn` decide quién tiene derecho a **insistir** cuando hay conflicto
3. Cuando P0 ve que P1 también quiere, consulta `turn`:
   - Si `turn == 1`: P0 retrocede temporalmente (cede el paso)
   - Si `turn == 0`: P0 espera activamente (tiene prioridad)

**Propiedades:**
- Exclusión mutua
- Progreso garantizado (no hay deadlock)
- Espera limitada (no hay starvation)

**Limitación:** solo funciona para 2 procesos.
-->

---

# **Figura 5.2 — Algoritmo de Dekker**

![](img/peterson_lock.svg)



<!--
**Figura 5.2 — diagrama de flujo de Dekker:**
Esta figura es clave para entender el algoritmo visualmente. Comparar el diagrama con el código ayuda a comprender la lógica.

**Puntos de decisión en el diagrama:**
1. `flag[i] = true` — declaro mi intención
2. `flag[j] = true?` — ¿el otro proceso también quiere entrar?
3. `turn == i?` — si no es mi turno, retiro mi flag y espero
4. Cuando `turn` cambia, restablezco mi flag y reintento

**Nota para el examen:** el algoritmo de Peterson reemplaza a Dekker por ser más simple, pero Dekker es históricamente importante.
-->

---

**Puntos de decisión clave:**
1. `flag[i] = true` → declaro mi intención de entrar
2. `flag[j] == true?` → ¿el otro proceso también quiere entrar?
3. `turn == i?` → si es mi turno, espero activamente; si no, retiro mi flag y cedo el paso
4. Cuando `turn` cambia, restablezco mi flag y reintento

> **Nota:** el algoritmo de Peterson reemplaza a Dekker por ser más simple, pero Dekker es históricamente importante (primera solución correcta documentada, 1965).

---

# **Algoritmo de Peterson**

Solución más simple y elegante:

```c
void P0() {
  while (true) {
    flag[0] = true;
    turn = 1;
    while (flag[1] && turn == 1) /* do nothing */;
    /* critical section */
    flag[0] = false;
  }
}
```

Funciona para 2 procesos. **Principio:** si ambos quieren entrar, el que establece `turn` último **cede el paso**.

<!--
**Regla #1:** `flag[i]=true` declara intención, `turn=j` cede el paso cortésmente ("después de ti").
**Regla #2:** Si ambos quieren entrar, el último en escribir `turn` espera — el que cedió último se aparta.
**Regla #3:** Peterson = Dekker simplificado: solo 3 líneas vs ~10, misma funcionalidad.
-->

<!--
**Algoritmo de Peterson — solución elegante (1981):**

G. L. Peterson publicó esta solución mucho más simple que Dekker.

**¿Por qué funciona?**
1. `flag[i] = true`: declaro intención de entrar
2. `turn = j`: cedo cortésmente ('después de ti')
3. `while (flag[j] && turn == j)`: espero solo si el otro quiere entrar **y** además le cedí el turno

**Clave de la corrección:** el último en escribir `turn` es quien cede. Si ambos ejecutan `turn = 1` y `turn = 0`, uno de los dos valores prevalece (el último en escribir). Ese proceso verá `turn == j` y esperará.

**Ventaja sobre Dekker:**
- Solo 3 líneas de código por proceso (vs ~10 de Dekker)
- Más fácil de verificar formalmente
- Intuitivo: 'si ambos quieren, el que cedió último espera'

**Limitación:** igual que Dekker, solo 2 procesos.
-->

---

# **Figura 5.3 — Algoritmo de Peterson**

![bg right:35% 70%](img/peterson_mutex.svg)

**Clave:** si ambos quieren entrar, el que establece `turn` último **cede el paso**.

<!--
**Figura 5.3 — diagrama de Peterson:**
Comparar con la figura 5.2 (Dekker) para apreciar la simplicidad.

Peterson elimina la necesidad de la variable `turn` adicional y la 'retirada temporal' (flag[0]=false / flag[0]=true).

**Ambos algoritmos demuestran** que la exclusión mutua es soluble con solo operaciones de lectura/escritura en memoria compartida — no se requiere soporte hardware especial. Sin embargo, en la práctica los SO modernos usan instrucciones atómicas hardware (C&S, XCHG) porque los algoritmos de software asumen un modelo de memoria secuencial que no siempre se cumple en hardware moderno (reordenamiento de instrucciones).
-->

---

<!-- _class: lead -->
# **2. Principios de Concurrencia**

---

# **Dificultades de la Concurrencia**

1. **Recursos globales compartidos** — el orden de lectura/escritura es crítico
2. **Asignación óptima de recursos** difícil para el SO
3. **Errores no deterministas** — resultados no reproducibles


<!--
**Tres dificultades fundamentales — contexto más amplio:**

1. **Recursos globales compartidos:** el orden de lectura/escritura sobre variables compartidas no es determinista desde la perspectiva del programador. El planificador del SO decide cuándo cambiar de proceso.

2. **Asignación óptima de recursos:** el SO debe decidir cuánta CPU, memoria y E/S dar a cada proceso. No sabe de antemano las necesidades de cada proceso. Un proceso que pide más memoria de la disponible puede forzar swapping.

3. **Errores no deterministas:** el 'Heisenbug' clásico — errores que desaparecen al agregar código de depuración porque el instrumento cambia el timing. Estos son los bugs más difíciles de encontrar y corregir.

**Regla práctica:** los bugs de concurrencia son los más costosos de la industria del software —ej. el 'Therac-25' (1985-87) causado por condiciones de carrera.
-->

---
# **Ejemplo de Condición de Carrera (Race Condition)**
### Ejemplo clásico — Procedimiento `echo`

```c
void echo() {
  chin = getchar();
  chout = chin;
  putchar(chout);
}
```

Problema: si P1 es interrumpido después de `getchar()`, P2 puede sobrescribir `chin` antes de que P1 lo use.

---

# **Ejemplo de Condición de Carrera (Race Condition)**

### Escenario del problema echo:

| Paso | Proceso P1 | Proceso P2 |
|:----:|:----------|:----------|
| 1 | `chin = 'x'` | — |
| 2 | (interrupción) | — |
| 3 | — | `chin = getchar()` → **'y'** |
| 4 | — | `chout = chin` → 'y' |
| 5 | — | `putchar('y')` |
| 6 | **`chout = chin` → 'y'** | — |
| 7 | `putchar('y')` | — |

**Resultado:** Se pierde 'x', se muestra 'y' dos veces

<!--
**Ejemplo `echo` — análisis instrucción por instrucción:**

El código parece inocente: leer un char, copiarlo, imprimirlo. Pero al compartir `chin` y `chout` entre procesos, el interleaving lo rompe.

**Secuencia real del desastre:**
1. P1: `chin = getchar()` → chin='x'
2. **P1 interrumpido** — el planificador da CPU a P2
3. P2: `chin = getchar()` → chin='y' (sobrescribe 'x')
4. P2: `chout = chin` → chout='y'
5. P2: `putchar('y')` → imprime 'y'
6. P1 reanuda: `chout = chin` → **chout='y'** (lee el 'y' de P2, no 'x')
7. P1: `putchar('y')` → imprime 'y' otra vez

**Resultado:** se perdió 'x', se imprimió 'y' dos veces. Pérdida de datos por condición de carrera.

**Solución trivial (pero incorrecta):** usar variables locales en la pila — eso no funciona porque cada proceso tiene su propia pila.
-->

---

# **Interacción entre Procesos**

**Tabla 5.2 — Grados de Conocimiento entre Procesos**

| Grado de Conocimiento | Relación | Problemas | Ejemplos |
|:---------------------|:---------|:----------|:---------|
| **Sin conocimiento** | Competición | Exclusión mutua, Deadlock, Inanición | Dos procesos imprimiendo |
| **Conocimiento indirecto** | Cooperación por compartición | Exclusión mutua, Deadlock, Inanición, Coherencia de datos | Variables compartidas |
| **Conocimiento directo** | Cooperación por comunicación | Deadlock, Inanición | Paso de mensajes
<!--
**Tabla 5.2 — grados de conocimiento entre procesos:**

Esta tabla clasifica los problemas de concurrencia según cuánto saben los procesos unos de otros. Es fundamental para entender qué mecanismo usar.

- **Sin conocimiento:** procesos compiten por recursos (ej. dos usuarios imprimiendo). El SO debe mediar. Problemas: exclusión mutua, deadlock, inanición.
- **Conocimiento indirecto:** procesos comparten datos a través de un recurso (ej. variables compartidas, archivos). Además de exclusión mutua, hay que mantener coherencia de datos. Los semáforos y monitores resuelven esto.
- **Conocimiento directo:** procesos se comunican explícitamente mediante mensajes. No hay memoria compartida, pero puede haber deadlock si A espera a B y B espera a A.

**Regla general:** a mayor conocimiento, más mecanismos de coordinación disponibles pero también más complejidad.
-->

---

<a href="img/fig_5_4.png" target="_blank"><img src="img/fig_5_4.png" style="width:100%"></a>

<!--
**Figura 5.4 — representación visual de las relaciones:**
Esta figura complementa la tabla 5.2 con diagramas de cada tipo de interacción.

**Puntos de discusión:**
- Los sistemas modernos raramente caen en una sola categoría. Un servidor web típico tiene competición (CPU, RAM), cooperación (caché compartida) y comunicación (paso de mensajes entre procesos workers).
- La clasificación de Stallings es útil para el análisis académico, pero en la práctica los límites son borrosos.
-->

---

# **Competición por Recursos**

- Procesos compiten por recursos **no compartibles** (impresora, archivo, etc.)
- Recurso crítico → **sección crítica**
- Solo un proceso puede estar en su sección crítica a la vez

<!--
**Competición por recursos — el escenario más común:**

**Recursos no compartibles:** impresora, archivo en modo exclusivo, estructura de datos compartida, conexión de red, dispositivo de E/S.

**Sección crítica (SC):** el segmento de código que accede al recurso no compartible. La SC es la 'zona prohibida' donde solo un proceso puede estar a la vez.

**Figura 5.x — diagrama de competencia:**
- Proceso A intenta entrar a SC: si recurso libre, entra y lo marca ocupado.
- Proceso B intenta entrar a SC: recurso ocupado, espera.
- Proceso A sale de SC: libera recurso.
- Proceso B entra a SC.

**Analogía:** un baño público con una sola cabina — solo una persona puede usarlo a la vez, las demás hacen fila.
-->

---

# **Requisitos para la Exclusión Mutua**

1. Solo un proceso puede estar en su sección crítica
2. Un proceso detenido fuera de su SC no debe interferir
3. Ningún proceso debe esperar indefinidamente (sin deadlock/inanición)
4. Si no hay proceso en SC, cualquier solicitud debe permitirse sin demora
5. Sin suposiciones sobre velocidades relativas o número de procesadores
6. Un proceso permanece en su SC solo por tiempo finito

<!--
**Los 6 requisitos de la exclusión mutua — cada uno importa:**

1. **Exclusión mutua:** solo un proceso en SC (el requisito fundamental)
2. **No interferencia:** un proceso que se detiene fuera de SC no debe afectar a otros (el primer intento con `turn` viola esto)
3. **Sin espera indefinida:** deadlock e inanición están prohibidos (el tercer intento con flag[] viola esto)
4. **Acceso inmediato sin contención:** si nadie usa el recurso, no debe demorarse (bajo demanda, sin espera innecesaria)
5. **Sin suposiciones de hardware:** debe funcionar con CPUs lentas o rápidas, 1 o N CPUs
6. **Tiempo finito en SC:** ningún proceso debe monopolizar el recurso (esto depende del programador, no del mecanismo)

**Pregunta de examen frecuente:** '¿Cuál de los 6 requisitos NO depende del mecanismo de exclusión mutua, sino del programa?' — Respuesta: el #6.
-->

---

<!-- _class: lead -->
# **3. Exclusión Mutua: Soporte Hardware**

---

# **Deshabilitación de Interrupciones**

Solución simple para **uniprocesador**:

```c
while (true) {
  /* disable interrupts */;
  /* critical section */;
  /* enable interrupts */;
}
```

### Problemas:
- Degradación de eficiencia
- No funciona en multiprocesador
- Riesgo si el proceso falla con interrupciones deshabilitadas

<!--
**Deshabilitación de interrupciones — la solución más simple:**

En un **uniprocesador**, deshabilitar interrupciones evita el cambio de contexto mientras se ejecuta la SC. El proceso no puede ser interrumpido.

**Tres problemas graves:**
1. **Degradación de eficiencia:** el SO usa interrupciones para el timer. Si las deshabilitamos, el planificador no puede redistribuir la CPU. Un proceso en SC podría usarla por milisegundos que otros necesitan.
2. **No funciona en multiprocesador:** deshabilitar interrupciones solo afecta al CPU donde se ejecuta el proceso. Otro proceso en otro CPU puede entrar a la misma SC.
3. **Riesgo catastrófico:** si el proceso falla (bug, segmentation fault) mientras las interrupciones están deshabilitadas, el sistema nunca las re-habilita → sistema congelado. Solo el watchdog timer podría reiniciarlo.

**Uso real:** el kernel de Linux la usa internamente para proteger estructuras de datos muy pequeñas (spinlocks con IRQ disable), pero no se expone al usuario.
-->

---

# **Instrucción Compare&Swap**

### ¿Qué hace el código, línea a línea?

```c
int compare_and_swap(int *word, int testval, int newval) {
  int oldval;
  oldval = *word;                        // 1. Lee el valor actual
  if (oldval == testval) *word = newval; // 2. Si coincide con testval, escribe newval
  return oldval;                         // 3. Devuelve el valor que leyó (antes del cambio)
}
```

**Clave:** los pasos 1–3 son atómicos — el hardware garantiza que ningún otro CPU puede tocar `*word` entre ellos.

---

### Uso para exclusión mutua:

```c
int bolt = 0;  // compartida: 0=libre, 1=ocupado

// Entrar a sección crítica:
while (compare_and_swap(&bolt, 0, 1) != 0);  // busy-wait
/* sección crítica */
bolt = 0;  // liberar
```

**¿Por qué funciona?**
- Si bolt era **0** (libre): CAS lo pone a 1 y retorna **0** → `!= 0` es falso → salimos del while → entramos a SC
- Si bolt era **1** (ocupado): CAS no lo modifica y retorna **1** → `!= 0` es verdadero → seguimos esperando

---

### Traza con 2 procesos simultáneos:

| Tiempo | P1 | P2 | bolt |
|:------:|:---|:---|:----:|
| t1 | `CAS(&bolt, 0, 1)` → retorna **0**, bolt=1 | — | **1** |
| t2 | Entra a SC | `CAS(&bolt, 0, 1)` → retorna **1**, sin cambio | **1** |
| t3 | En SC | Sigue en busy-wait | **1** |
| t4 | `bolt = 0` (sale de SC) | `CAS(&bolt, 0, 1)` → retorna **0**, bolt=1 | **1** |
| t5 | — | Entra a SC | **1** |

P1 y P2 nunca están en SC al mismo tiempo → **exclusión mutua garantizada**.

<!--
**Compare&Swap (C&S) — la instrucción atómica más versátil:**

**Atomicidad:** C&S se ejecuta como una sola instrucción. Ningún otro proceso puede modificar `*word` entre la lectura y la escritura.

**Uso típico para exclusión mutua:**
- Variable compartida `bolt = 0` (0 = libre, 1 = ocupado)
- `while (compare_and_swap(&bolt, 0, 1) == 1)` → espera mientras bolt=1
- Cuando C&S retorna 0 → bolt pasó de 0 a 1 → entramos a SC
- Al salir: `bolt = 0`

**Variantes:** CAS (x86: `CMPXCHG`), LL/SC (ARM, PowerPC), C++ `std::atomic::compare_exchange_weak()`.

**Nota:** C&S es la base de implementación de semáforos, mutexes y casi todos los mecanismos de sincronización en SO modernos.
-->

---

# **Instrucción Exchange (XCHG)**

```c
void exchange(int *register, int *memory) {
  int temp;
  temp = *memory;
  *memory = *register;
  *register = temp;
}
```

### Uso para exclusión mutua:

```c
int keyi = 1;
do exchange(&keyi, &bolt);
while (keyi != 0);
/* critical section */
bolt = 0;
```

- Intel IA-32/IA-64 incluyen XCHG
- Invariante: `bolt + Σkeyi = n`

<!--
**Exchange (XCHG) — intercambio atómico registro↔memoria:**

**Uso típico:**
- Cada proceso tiene `keyi = 1` (local)
- Variable compartida `bolt = 0` (inicialmente libre)
- `do exchange(&keyi, &bolt); while (keyi != 0)`
  - Si bolt=0: exchange hace bolt=1, keyi=0 → sale del while → entra a SC
  - Si bolt=1: exchange mantiene bolt=1, keyi=1 → sigue esperando
- Al salir: `bolt = 0`

**Invariante:** `bolt + Σkeyi = n` (n = número de procesos). Cuando n=4 y 2 procesos están en SC (imposible), la invariante se violaría.

**Intel IA-32/IA-64:** XCHG con prefijo `LOCK` garantiza atomicidad en el bus de memoria, incluso en sistemas multiprocesador. Sin `LOCK`, la instrucción no es atómica entre CPUs.
-->

---

# **Figura 5.5 — Soporte Hardware para Exclusión Mutua**

| Técnica | ¿Funciona en? | ¿Busy waiting? | Riesgo |
|:--------|:-------------:|:--------------:|:-------|
| **Deshabilitar IRQ** | Uniprocesador (no en MultiCPU) | Sí | Sistema congelado si falla |
| **Compare&Swap** | Uniprocesador y MultiCPU | Sí | Inanición |
| **Exchange (XCHG)** | Uniprocesador y MultiCPU | Sí | Inanición |

<!--
**Figura 5.5 — comparativa de soporte hardware:**
Esta figura muestra las tres técnicas hardware lado a lado: deshabilitación de interrupciones, C&S y XCHG.

**Para el examen:** entender las diferencias fundamentales:
- Deshabilitar IRQ solo sirve en uniprocesador
- C&S y XCHG funcionan en multiprocesador
- Todos tienen **busy waiting** — el proceso consume CPU mientras espera
- Todos pueden causar **inanición** (un proceso nunca logra entrar)
-->

---

![](img/hardware_support.svg)

<!--
**Propiedades — ventajas y desventajas del soporte hardware:**

**Ventajas:**
- Aplicable a cualquier número de procesos
- Simple de implementar y verificar (la atomicidad la garantiza el hardware)
- Soporta múltiples secciones críticas (cada SC puede usar su propia variable)

**Desventajas:**
- **Busy waiting:** el proceso gasta ciclos de CPU mientras espera. En uniprocesador esto es catastrófico (el proceso que espera nunca cede la CPU si el planificador es no expulsivo).
- **Inanición:** posible si varios procesos esperan y el planificador nunca selecciona a uno en particular.
- **Deadlock por inversión de prioridades:** en uniprocesador con planificación por prioridades, un proceso de baja prioridad en SC puede ser interrumpido por uno de alta prioridad que también necesita la SC → el de alta prioridad espera al de baja, que no puede ejecutar porque el de alta tiene más prioridad → deadlock.

**Conclusión:** el soporte hardware es necesario pero no suficiente. Se necesita una abstracción mejor: los **semáforos**.
-->

---

# **Propiedades del Enfoque por Instrucción Máquina**

### Ventajas:
- Aplicable a cualquier número de procesos
- Simple y fácil de verificar
- Soporta múltiples secciones críticas

### Desventajas:
- **Espera ocupada (busy waiting)** — consume CPU
- Posible **inanición**
- Posible **deadlock** (inversión de prioridades en uniprocesador)

---

<!-- _class: lead -->
# **4. Semáforos**

---

# **Definición de Semáforo**

- **Estructura:** contador entero `count` + cola `queue` de procesos bloqueados
- **Dos operaciones atómicas:**
  1. **`semWait(s)`**: `s.count--`; si `s.count < 0`, el proceso se bloquea en `s.queue`
  2. **`semSignal(s)`**: `s.count++`; si `s.count <= 0`, despierta un proceso de `s.queue`

<!-- 🎤 Narrador: El semáforo tiene dos componentes: un contador y una cola. La clave es que semWait y semSignal son atómicas — no pueden interrumpirse a medias. Cuando s.count > 0 hay recursos disponibles; cuando s.count < 0 hay procesos esperando. Fíjate que semSignal usa <= 0, no <. Esto asegura que siempre se despierte a alguien si hay procesos en la cola. -->

> **Nota:** `semWait` decrementa primero, luego decide. `semSignal` incrementa primero, luego decide. Este orden es clave para entender el comportamiento con múltiples procesos.

---

### Interpretación de `s.count`

| Valor | Significado |
|:-----|:------------|
| `s.count > 0` | Hay recursos disponibles. `semWait` no bloquea |
| `s.count == 0` | No hay recursos. El próximo `semWait` **bloqueará** |
| `s.count < 0` | Hay `\|s.count\|` procesos **bloqueados** esperando |

> **Nota:** `semSignal` usa `<= 0` (no `<`). Si `count` era -3 (3 bloqueados), tras signal es -2 (2 bloqueados, 1 desbloqueado).

---

# **Semáforo Binario**

```c
struct binary_semaphore {
  enum {zero, one} value;
  queueType queue;
};
void semWaitB(binary_semaphore s) {
  if (s.value == one) s.value = zero;
  else { /* block this process in s.queue */; }
}
void semSignalB(binary_semaphore s) {
  if (s.queue is empty()) s.value = one;
  else { /* remove a process from s.queue */;
        /* place on ready list */; }
}
```

> **Nota:** En el semáforo binario, `s.count` solo puede ser 0 o 1. Se usa principalmente para **exclusión mutua** (mutex). Cuando `semSignalB` despierta a un proceso bloqueado, **no cambia** el valor del semáforo — el proceso despertado tomará el recurso inmediatamente.

---

<!-- 🎤 Narrador: La diferencia clave del semáforo binario es que el valor solo puede ser 0 o 1 — se satura. En el general, semSignal siempre incrementa; en el binario, si hay alguien esperando, solo lo despierta sin cambiar el valor. Esto es importante porque el proceso despertado asume inmediatamente el recurso. -->

### Semáforo Fuerte vs. Débil
- **Fuerte (FIFO):** orden de llegada → garantiza **no inanición**. Es el que asume Stallings.
- **Débil:** orden no especificado → puede causar **inanición** (algunos procesos nunca son despertados)

> **Clave en semáforo binario:** `semSignalB` despierta a un proceso bloqueado **sin cambiar** `s.value` — el proceso despertado tomará el recurso inmediatamente. A diferencia del general, donde `semSignal` siempre incrementa el contador.

---

<!-- 🎤 Narrador: Esta figura es clave. Muestra cómo semWait (izquierda) y semSignal (derecha) se ramifican según el estado del contador. En semWait, si count es mayor que 0, simplemente decrementa y sigue; si es menor o igual a 0, decrementa y bloquea. En semSignal es al revés: incrementa, y si count es mayor o igual a 0, despierta a alguien de la cola; si no, simplemente sigue. -->

# **Figura 5.6 — Primitivas de Semáforo**

![Primitivas de Semáforo](img/semaphore_wait_signal.svg)

> **Leyendo la figura:** En `semWait` (izquierda), primero se decrementa el contador; si queda negativo, el proceso se bloquea en la cola. En `semSignal` (derecha), primero se incrementa; si el valor sigue siendo ≤ 0, se despierta a un proceso de la cola.

---

| Operación | Antes | Después | Efecto |
|:---------:|:-----:|:-------:|:-------|
| semWait (libre) | 2 | 1 | Proceso entra |
| semWait (ocupado) | 0 | -1 | Proceso se bloquea |
| semSignal (con espera) | -3 | -2 | Se despierta 1 proceso |
| semSignal (sin espera) | 1 | 2 | Solo incrementa |

---

<!-- 🎤 Narrador: Esta tabla muestra la evolución de un semáforo general inicializado a 1 con tres procesos compitiendo por la sección crítica. P1 ejecuta semWait primero y entra — s baja de 1 a 0. P2 ejecuta semWait, s baja a -1, se bloquea en la cola. P3 ejecuta semWait, s baja a -2, se bloquea también. Cuando P1 sale con semSignal, s sube a -1 y se despierta a P2 de la cola FIFO. Cuando P2 sale con semSignal, se despierta a P3. Observa que el semáforo actúa como un portero: solo deja pasar a uno a la vez y los demás esperan ordenados en la fila. -->

# **Ejemplo del Mecanismo de Semáforo**

> **Sigue el rastro del semáforo `s` inicializado a 1.** Observa cómo `s.count` cambia con cada operación y cómo la cola refleja quién espera. P1 es el primero en entrar (t1), P2 se bloquea (t2), P3 también (t3). Cuando P1 sale (t4), se despierta a P2 — el semáforo FIFO asegura orden.

| Tiempo | P1 | P2 | P3 | `s.count` | Cola |
|:------:|:--:|:--:|:--:|:---------:|:----:|
| t1 | semWait → **SC** | — | — | 0 | vacía |
| t2 | **SC** | semWait → bloqueado | — | -1 | [P2] |
| t3 | **SC** | bloqueado | semWait → bloqueado | -2 | [P2,P3] |
| t4 | semSignal → sale | **despierta → SC** | bloqueado | -1 | [P3] |
| t5 | — | **SC** | bloqueado | -1 | [P3] |
| t6 | — | semSignal → sale | **despierta → SC** | 0 | vacía |

El semáforo actúa como **portero**: solo deja pasar a uno a la vez.

---

<!-- 🎤 Narrador: Con s inicializado a 1, el primer proceso que ejecuta semWait(s) entra a la SC. Los siguientes procesos que intenten semWait(s) se bloquean porque s.count se vuelve negativo. Cuando el proceso sale de SC y ejecuta semSignal(s), se despierta al siguiente proceso en la cola. El semáforo elimina el busy waiting que tenían los enfoques hardware — los procesos esperan bloqueados, no consumiendo CPU. -->

# **Exclusión Mutua con Semáforos**

```c
semaphore s = 1;

void P(int i) {
  while (true) {
    semWait(s);         // solicitar acceso
    /* sección crítica */;
    semSignal(s);       // liberar acceso
    /* resto */;
  }
}
```

- `s = 1` → primer proceso entra; los demás se **bloquean** en la cola
- `semSignal` **despierta** al siguiente proceso en cola

---
<!-- 🎤 Narrador: Este es el primer problema clásico de sincronización. El semáforo general n cuenta cuántos elementos hay en el buffer (inicializado a 0). El semáforo binario s protege el acceso al buffer (exclusión mutua). El productor produce, espera s, añade al buffer y libera s, luego señala n. El consumidor espera n primero (que haya algo que consumir), luego espera s, toma del buffer, libera s y consume. El orden importa: n cuenta recursos, s protege datos. -->


# **Problema del Productor/Consumidor**

![width:40%](img/ch5-page-0251.jpg)

**Buffer infinito:** productor coloca en `b[in]`, consumidor toma de `b[out]`
- Condición: consumidor no debe tomar si `in <= out`
- Solución con semáforo **general** `n` + semáforo **binario** `s`:

---


```c
semaphore n = 0, s = 1;

void producer() {          void consumer() {
  produce_item();            semWait(n);
  semWait(s); append();      semWait(s); take();
  semSignal(s);              semSignal(s);
  semSignal(n);              consume_item();
}                          }
```

---

<!-- 🎤 Narrador: El bounded buffer usa tres semáforos: e (empty) cuenta espacios vacíos, n (full) cuenta elementos ocupados, y s (mutex) protege el buffer. La regla de oro es crucial: primero esperar el recurso de condición (e o n), luego el mutex s. Si inviertes el orden, puedes causar deadlock — por ejemplo, el productor toma s pero espera e mientras el consumidor tiene e pero espera s. -->

# **Buffer Circular Finito (Bounded-Buffer)**

### Tres semáforos:
- `e` (empty) = tamaño del buffer → espacios vacíos
- `n` (full) = 0 → elementos ocupados  
- `s` (mutex) = 1 → exclusión mutua

```
Productor:  semWait(e) → semWait(s) → append() → semSignal(s) → semSignal(n)
Consumidor: semWait(n) → semWait(s) → take()    → semSignal(s) → semSignal(e)
```

> **Regla de oro:** pedir el recurso de condición (`e`/`n`) **antes** que el mutex (`s`). Invertir el orden puede causar **deadlock**.

---

<!-- 🎤 Narrador: Los semáforos se implementan con C&S en multiprocesador (microsegundos de busy waiting solo para modificar count y la cola) o deshabilitando interrupciones en uniprocesador. En la versión con IRQ disable, después de bloquear al proceso se re-habilitan las interrupciones antes de hacer el cambio de contexto. Esto evita el problema de sistema congelado. -->

# **Implementación de Semáforos**

### Con Compare&Swap (multiprocesador):
- Atomicidad garantizada por hardware (C&S, XCHG)
- Microsegundos de busy waiting (solo para modificar count/queue)

### Deshabilitando interrupciones (uniprocesador):
```c
void semWait(semaphore s) {
  inhibit_interrupts();
  s.count--;
  if (s.count < 0) {
    place_on_queue(s.queue);
    allow_interrupts();
    block();  // cambio de contexto
  } else allow_interrupts();
}
```

---

# **Diagrama de Transición de Estados**

![Transición de Estados en Semáforo](img/semaphore_states.svg)

**Ejecutando → Bloqueado:** cuando `semWait` encuentra `s.count < 0`
**Bloqueado → Listo:** cuando `semSignal` despierta un proceso

---

<!-- 🎤 Narrador: El semáforo binario es un caso especial con rango 0-1, ideal para exclusión mutua. El general sirve para contar recursos — por ejemplo, inicializado a N para modelar N instancias de un dispositivo. La diferencia clave está en semSignal: el general siempre incrementa count; el binario, si hay procesos esperando, solo despierta a uno sin cambiar el valor. -->

# **Semáforo Binario vs. General**

| Propiedad | Binario | General |
|:----------|:-------:|:-------:|
| **Rango** | 0 y 1 | Entero ≥ 0 |
| **Uso** | Exclusión mutua | Sincronización + control de recursos |
| **Inicialización** | `s = 1` | `s = N` |
| **semSignal sin espera** | value → one | count++ |
| **semSignal con espera** | Despierta proceso | count++ y despierta |

> **Un semáforo binario es un caso especial del general con cota superior 1.**

---

# **Patrones de Uso**

### 1. Exclusión Mutua (mutex)
```
semWait(mutex) → SC → semSignal(mutex)
```
### 2. Sincronización de Condición
```
Proceso A:               Proceso B:
/* código A */           semWait(s);  // espera
semSignal(s);            /* después de A */
```

---

<!-- 🎤 Narrador: Estos son los tres errores más frecuentes con semáforos. El primero (olvidar semSignal) es el más peligroso porque causa deadlock silencioso — un return temprano o una excepción puede saltarse el semSignal. El segundo (invertir orden en bounded buffer) produce deadlock. El tercero es conceptual: usar binario donde se necesita general. Ninguno da error de compilación, solo se manifiestan en ejecución. -->

# **Errores Comunes**

### 1. Olvidar `semSignal`
```c
semWait(s);
// SC con return temprano → ¡se salta semSignal(s)!
semSignal(s);
```
**→ Deadlock:** otros procesos se bloquean permanentemente.

### 2. Invertir orden en bounded buffer
```c
// MAL: semWait(s) antes de semWait(e) → deadlock si buffer lleno
semWait(s); semWait(e);

// BIEN: semWait(e) antes de semWait(s)
semWait(e); semWait(s);
```

### 3. Usar semáforo binario donde se necesita general
Ej.: N instancias de un dispositivo → usar semáforo general con `s = N`.

---

<!-- _class: lead -->
# **5. Monitores**

---

# **Estructura de un Monitor**

- **Encapsula:** datos compartidos + procedimientos + sincronización
- **Exclusión mutua automática:** solo un proceso puede ejecutar en el monitor a la vez

```c
monitor nombre {
  /* datos compartidos (privados) */
  int dato_compartido;

  void procedimiento1(...) { /* solo un proceso a la vez */ }
  void procedimiento2(...) { /* solo un proceso a la vez */ }
}
```

**Analogía:** una biblioteca con una sola sala de lectura — solo una persona a la vez.

---

# **Variables de Condición**

Mecanismo de señalización dentro del monitor:

- **`cwait(c)`**: suspende el proceso en la condición `c`, **libera el monitor**
- **`csignal(c)`**: reanuda un proceso bloqueado en `c`

### Diferencia clave con semáforos:
| Aspecto | Semáforo | Variable condición |
|:--------|:--------:|:------------------:|
| Señal sin espera | Se **acumula** (count++) | Se **pierde** |
| Contador | Sí (entero) | No (solo cola) |

---

# **Monitor para Buffer Acotado**

```c
monitor boundedbuffer;
cond notfull, notempty;

void append(char x) {
  if (count == N) cwait(notfull);
  buffer[nextin] = x;
  count++;
  csignal(notempty);
}

void take(char *x) {
  if (count == 0) cwait(notempty);
  *x = buffer[nextout];
  count--;
  csignal(notfull);
}
```
**Sin semáforos explícitos** — la exclusión mutua del buffer es **automática** en el monitor.

---

# **Modelo Mesa vs. Hoare**

| Característica | Hoare | Mesa |
|:--------------|:-----|:-----|
| Señal | `csignal` — inmediata | `cnotify` — diferida |
| Verificación | `if (condición)` | `while (condición)` |
| Control | Se transfiere al instante | El notificado compite por el monitor |

**Uso práctico:** Java (`wait/notify`), C# (`Monitor.Pulse`), Python (`Condition`) usan el modelo **Mesa**.

---

<!-- _class: lead -->
# **6. Paso de Mensajes**

<!--
**Sistemas de mensajes — concurrencia sin memoria compartida:**

Hasta ahora todos los mecanismos asumen **memoria compartida** (variables, semáforos, monitores). El paso de mensajes permite concurrencia incluso cuando los procesos no comparten espacio de direcciones — crucial para sistemas distribuidos.

**Características del modelo:**
1. **Send/receive como primitivas básicas**
2. **Sincronización:** bloqueante vs no bloqueante
3. **Direccionamiento:** directo (PID) vs indirecto (buzones)
4. **Formato del mensaje:** cabecera + cuerpo
5. **Propiedades de la cola:** FIFO, prioridad, etc.

**Ejemplos reales:**
- Microkernel Minix: servidores como procesos de usuario que se comunican por mensajes
- Windows: LPC (Local Procedure Call) → ALPC
- Mach: puertos + mensajes
-->

---

# **Características de los Sistemas de Mensajes**

| Característica | Descripción |
|:--------------|:-----------|
| **Send/Receive** | Primitivas básicas de comunicación |
| **Sincronización** | Bloqueante vs no bloqueante |
| **Direccionamiento** | Directo (PID) vs indirecto (buzones) |
| **Formato** | Cabecera + cuerpo del mensaje |
| **Propiedades de cola** | FIFO, prioridad, inspección |

**Ejemplos reales:**
- **Minix:** servidores como procesos de usuario que se comunican por mensajes
- **Windows:** LPC (Local Procedure Call) → ALPC
- **Mach:** puertos + mensajes

<!--
**Primitivas y modos de sincronización — compensaciones de diseño:**

**send(destination, message):** envía un mensaje a un destino
**receive(source, message):** recibe un mensaje de una fuente

**Modos de sincronización (Tabla comparativa):**

| Modo | Send | Receive | Uso típico |
|:----|:----|:--------|:-----------|
| **Bloqueante/Bloqueante (Rendezvous)** | Espera hasta recibido | Espera hasta recibir | RPC síncrono |
| **No bloqueante/Bloqueante** | Continúa inmediato | Espera hasta recibir | Servidor, productor |
| **No bloqueante/No bloqueante** | Continúa inmediato | Abandona si no hay | Sondeo (polling) |

**Rendezvous (cita):** ambos procesos se sincronizan en el intercambio. El send bloquea hasta que el receive correspondiente se ejecuta, y viceversa. Es el modo más seguro (no hay buffers) pero puede causar deadlock fácilmente.
-->

---

# **Primitivas de Paso de Mensajes**

```c
send(destination, message);
receive(source, message);
```

### Modos de Sincronización:

| Modo | Send | Receive |
|:----|:----|:--------|
| **Bloqueante/Bloqueante** | Espera hasta recibido | Espera hasta recibir |
| **No bloqueante/Bloqueante** | Continúa inmediato | Espera hasta recibir |
| **No bloqueante/No bloqueante** | Continúa inmediato | Abandona si no hay |

<!--
**Direccionamiento directo vs indirecto — ¿cómo encuentro al destinatario?:**

**Directo:**
- `send(P2, msg)` — especifico el proceso destino
- `receive(P1, msg)` — especifico la fuente (o implícito = cualquiera)
- Simétrico: ambos se conocen
- Asimétrico: solo el receptor especifica la fuente

**Indirecto (buzones/mailboxes/ports):**
- `send(box, msg)` — envío a un buzón
- `receive(box, msg)` — recibo de un buzón
- Los procesos no se conocen entre sí, solo conocen el buzón

**Ventaja del indirecto:** desacoplamiento — el productor no necesita saber quiénes son los consumidores. Permite añadir o quitar consumidores dinámicamente.

**Relaciones (muchos:muchos):** varios productores pueden enviar al mismo buzón, varios consumidores pueden recibir del mismo buzón.
-->


# **Formato de Mensaje**

- **Cabecera:** tipo, ID destino, ID fuente, longitud, control
- **Cuerpo:** contenido del mensaje

### Disciplina de Cola:
- FIFO (por defecto)
- Por prioridad
- El receptor puede inspeccionar y seleccionar

<!--
**Exclusión mutua con mensajes — el patrón del 'token':**

```c
void P(int i) {
  message msg;
  while (true) {
    receive(box, msg);       // espera el token
    /* critical section */;
    send(box, msg);          // libera el token
  }
}
```

**Mecanismo:**
- El buzón `box` contiene exactamente **un mensaje** (el token)
- `receive` = tomar el token (si no está, el proceso se bloquea)
- `send` = devolver el token al buzón
- Solo el proceso que tiene el token puede estar en SC

**Equivalencia con semáforo binario:**
- `semWait(s)` ≡ `receive(box, msg)`
- `semSignal(s)` ≡ `send(box, msg)`
- `s = 1` ≡ enviar el mensaje inicial al buzón

**Ventaja:** funciona en sistemas distribuidos sin memoria compartida. El buzón puede estar en otra máquina.
-->

---

# **Exclusión Mutua con Mensajes**

![width:80%](img/ch5-page-0268.jpg)

---

```c
void P(int i) {
  message msg;
  while (true) {
    receive(box, msg);       // Espera el token
    /* critical section */;
    send(box, msg);          // Libera el token
  }
}
```

<!--
**Inicialización y puesta en marcha del sistema de mensajes:**

```c
create_mailbox(box);         // crear el buzón
send(box, null);             // poner el token inicial
parbegin(P(1), P(2), ..., P(n));  // iniciar todos los procesos
```

**Detalles importantes:**
1. `create_mailbox` crea la cola de mensajes en el kernel
2. `send(box, null)` coloca el token inicial — el primer `receive` tomará este token y entrará a SC
3. `parbegin` inicia todos los procesos concurrentemente (es una construcción clásica de Dijkstra)

**Análisis de corrección:**
- Solo un proceso puede tener el token → exclusión mutua
- El token siempre se devuelve → ningún proceso se bloquea permanentemente
- Si N procesos están esperando y uno libera, exactamente uno lo recibe
- **Pero:** hay busy waiting si `receive` es no bloqueante (polling)
-->

---

# **Inicialización — Exclusión Mutua con Mensajes**

```c
// Inicialización:
create_mailbox(box);
send(box, null);
parbegin(P(1), P(2), ..., P(n));
```

**Mecanismo:**
- El buzón `box` contiene un token que da acceso a la SC
- Cada proceso recibe el token → entra en SC → libera el token
- Garantiza exclusión mutua

<!--
**Buffer acotado con mensajes — dos buzones de control:**

En lugar de usar semáforos `e` y `n`, usamos buzones mensajeros:

```c
create_mailbox(mayproduce);   // control de espacio
create_mailbox(mayconsume);   // control de elementos

// Inicializar mayproduce con 'capacity' mensajes vacíos
for (i = 0; i < capacity; i++) send(mayproduce, null);
```

**Flujo del productor:**
1. `receive(mayproduce, msg)` → espera espacio disponible
2. Produce el elemento y lo envía
3. `send(mayconsume, element)` → pone el elemento en el buzón de consumo

**Flujo del consumidor:**
1. `receive(mayconsume, msg)` → espera un elemento
2. Consume el elemento
3. `send(mayproduce, null)` → devuelve un espacio al buzón de producción

**Equivalencia con semáforos:**
- `mayproduce` ≡ semáforo `e` (empty)
- `mayconsume` ≡ semáforo `n` (full)
- Sin necesidad de un mutex separado — el paso de mensajes es intrínsecamente atómico
-->

---

# **Buffer Acotado con Mensajes**

- **mayproduce:** inicializado con `capacity` mensajes vacíos
- **mayconsume:** contiene los mensajes producidos
- Productor: recibe de `mayproduce`, envía a `mayconsume`
- Consumidor: recibe de `mayconsume`, envía a `mayproduce`

<!--
**Cómo funciona la solución con mensajes:**

La idea central es usar dos buzones (mailboxes) como "contadores" implícitos:

- `mayproduce` comienza con `capacity` mensajes vacíos (tokens). Cada token representa un espacio libre en el buffer.
- `mayconsume` comienza vacío.

**Flujo del productor:**
1. `receive(mayproduce, msg)` → bloquea si no hay espacios libres (mailbox vacío)
2. Produce el elemento
3. `send(mayconsume, element)` → pone el elemento en el buzón de consumo

**Flujo del consumidor:**
1. `receive(mayconsume, msg)` → bloquea si no hay elementos disponibles
2. Consume el elemento
3. `send(mayproduce, null)` → devuelve un token (espacio libre) al productor

**Equivalencia con semáforos:**
- `mayproduce` ≡ semáforo `e` (empty slots)
- `mayconsume` ≡ semáforo `n` (full slots)
- No se necesita mutex separado — el paso de mensajes es intrínsecamente atómico: solo un proceso puede recibir un mensaje a la vez.
-->

---

<!-- _class: lead -->
# **7. Problema de Lectores/Escritores**

<!--
**Problema de Lectores/Escritores — motivación y contexto:**

Es uno de los problemas clásicos de concurrencia más estudiados. Su importancia radica en que muchos sistemas reales tienen este patrón.

**Casos de uso reales:**
- Bases de datos: miles de lectores concurrentes, pocos escritores (actualizaciones)
- Sistemas de archivos: caché de directorios compartida
- Memoria caché: lectura frecuente, escritura ocasional
- Diccionarios en memoria: búsquedas constantes, actualizaciones periódicas

**Las 3 condiciones:**
1. Varios lectores pueden leer simultáneamente
2. Solo un escritor a la vez
3. Nadie lee mientras se escribe (consistencia de datos)

**Analogía:** una biblioteca pública — muchas personas pueden leer libros al mismo tiempo, pero si alguien está escribiendo en una pizarra, los lectores deben esperar a que termine.
-->

---

# **Definición del Problema**

- **Área de datos compartida** (archivo, memoria, etc.)
- **Lectores:** solo leen — pueden coexistir múltiples lectores
- **Escritores:** solo escriben — **exclusión mutua** total

### Condiciones:
1. Varios lectores pueden leer simultáneamente
2. Solo un escritor a la vez
3. Si un escritor escribe, ningún lector puede leer

<!--
**Solución: Lectores tienen prioridad — el problema de la inanición:**

```c
int readcount;              // contador de lectores activos
semaphore x = 1;            // mutex para readcount
semaphore wsem = 1;         // semáforo de escritura

void reader() {
  semWait(x); readcount++;  // incrementar contador
  if(readcount == 1) semWait(wsem);  // primer lector bloquea escritores
  semSignal(x);
  READUNIT();               // leer
  semWait(x); readcount--;  // decrementar contador
  if(readcount == 0) semSignal(wsem);  // último lector libera escritores
  semSignal(x);
}
```

**Mecanismo:**
- `wsem` protege el recurso de los escritores
- Solo el **primer** lector ejecuta `semWait(wsem)` — los demás lectores entran libremente
- Solo el **último** lector ejecuta `semSignal(wsem)` — libera a los escritores

**Problema:** si siempre hay al menos un lector en SC, los escritores nunca pueden escribir → **inanición de escritores**.
-->

---

# **Solución: Lectores tienen Prioridad**

```c
int readcount;
semaphore x = 1, wsem = 1;

void reader() {
  semWait(x); readcount++;
  if(readcount == 1) semWait(wsem);
  semSignal(x);
  READUNIT();
  semWait(x); readcount--;
  if(readcount == 0) semSignal(wsem);
  semSignal(x);
}
```

<!--
**Figura 5.xx — comportamiento de la solución lectores-prioritarios:**
Esta figura muestra una línea de tiempo con múltiples lectores y escritores.

**Observar:**
- Los lectores L1, L2, L3 entran simultáneamente (no hay exclusión entre lectores)
- El escritor W1 se bloquea porque `wsem` está tomado por L1
- L1 sale, pero L4 ya está esperando → `readcount` no llega a 0 → W1 sigue bloqueado
- Esto puede durar indefinidamente si siempre llegan nuevos lectores

**Pregunta de discusión:** ¿es siempre incorrecto que los lectores tengan prioridad? Depende del sistema: en un servidor web de solo lectura (catálogo), dar prioridad a lectores es óptimo. En un sistema bancario, los escritores deben tener prioridad para evitar datos obsoletos.
-->

---

# **Solución: Lectores tienen Prioridad (cont.)**

### Mecanismo:
- `wsem`: controla el acceso del escritor (los lectores lo bloquean solo el primero/último)
- `x`: protege `readcount`
- Los escritores solo pueden escribir si `readcount == 0`

<!--
**Tabla 5.6 — estado de las colas en la solución lector-prioritario:**
Esta tabla muestra, paso a paso, los valores de las variables y el estado de las colas.

**Columnas:**
- Acción: qué operación se ejecutó
- readcount: número de lectores activos
- Cola wsem: procesos bloqueados en el semáforo de escritura
- Cola x: procesos bloqueados en el mutex de readcount
- Estado: qué procesos están en SC

**Interpretación:** cuando readcount=3 y llega un escritor, el escritor se bloquea en wsem. Cuando readcount baja a 0 (último lector sale), el escritor se desbloquea.
-->

---

# **Tabla 5.6 — Estado de las Colas de Procesos**

| Acción | `readcount` | Cola `wsem` | Cola `x` | Estado (SC) |
|:-------|:-----------:|:-----------:|:--------:|:-----------|
| L1: reader() | 0 → 1 | — | — | L1 leyendo |
| L2: reader() | 1 → 2 | — | — | L1, L2 leyendo |
| L3: reader() | 2 → 3 | — | — | L1, L2, L3 leyendo |
| E1: writer() | 3 | E1 bloqueado | — | L1, L2, L3 leyendo |
| L1: sale | 3 → 2 | E1 bloqueado | — | L2, L3 leyendo |
| L4: reader() | 2 → 3 | E1 bloqueado | — | L2, L3, L4 leyendo |
| L2: sale | 3 → 2 | E1 bloqueado | — | L3, L4 leyendo |
| L3: sale | 2 → 1 | E1 bloqueado | — | L4 leyendo |
| L4: sale | 1 → 0 | E1 desbloqueado | — | E1 escribiendo |

**Interpretación:** mientras `readcount > 0` el escritor E1 permanece bloqueado en `wsem`. Nuevos lectores (L4) pueden seguir entrando, manteniendo `readcount > 0` y retrasando a E1 indefinidamente — esto es la **inanición de escritores**.

<!--
**Solución: Escritores tienen prioridad — más compleja pero más justa:**

**Mecanismos adicionales:**
- `rsem` — semáforo que inhibe a los lectores cuando hay escritores esperando
- `writecount` — contador de escritores esperando
- `z` — semáforo para encolar lectores adicionales (solo un lector espera en `rsem`)

**¿Cómo funciona?**
1. Cuando llega un escritor, incrementa `writecount`
2. Si es el primer escritor (`writecount == 1`), ejecuta `semWait(rsem)` — esto bloquea la entrada de nuevos lectores
3. Los lectores que ya están leyendo terminan (readcount baja a 0)
4. El escritor ejecuta `semWait(wsem)` y escribe
5. Al salir, si hay más escritores esperando, el siguiente escritor entra; si no, libera `rsem` para que los lectores puedan leer

**Problema:** puede causar inanición de lectores si siempre hay escritores esperando.

**Trade-off:** no hay solución perfecta — cualquier esquema puede causar inanición de un lado u otro.
-->

---

# **Solución: Escritores tienen Prioridad**

### Mecanismos adicionales:
- `rsem` — inhibe lectores cuando hay escritores esperando
- `writecount` — controla `rsem`
- `z` — encola lectores adicionales (solo uno espera en `rsem`)

<!--
**Solución con paso de mensajes — controlador centralizado:**

**Arquitectura:**
- Un proceso controlador gestiona el acceso a los datos
- Tres buzones: `readrequest`, `writerequest`, `finished`
- Variable `count`: >0 (lectores activos), =0 (inactivo), <0 (escritor activo)

**Protocolo del controlador:**
1. Recibe solicitudes de lectura/escritura o notificaciones de finalización
2. Si `count >= 0` (no hay escritor) y llega solicitud de lectura → incrementa `count` y permite leer
3. Si `count == 0` y llega solicitud de escritura → decrementa `count` a -1 y permite escribir
4. Cuando recibe `finished`, ajusta `count` y decide si admitir a la siguiente solicitud en espera

**Ventaja del controlador centralizado:** toda la lógica de decisión está en un solo lugar → fácil de verificar y modificar. Desventaja: el controlador es un punto único de fallo y cuello de botella.
-->

---

# **Solución con Paso de Mensajes**

### Controlador centralizado:
- Tres buzones: `readrequest`, `writerequest`, `finished`
- Variable `count`: >0 (lectores activos), =0 (escritor espera), <0 (escritor activo)
- Servicio de mensajes `finished` antes de nuevas solicitudes

<!--
**Resumen del Capítulo 5 — tabla comparativa final:**

Esta tabla es material de examen directo. Los estudiantes deben conocer las ventajas y desventajas de cada mecanismo.

**Mnemotecnia para el examen:**
- **Software:** simple pero complejo + busy waiting
- **Hardware:** atómico pero busy waiting + inanición
- **Semáforos:** flexibles pero fáciles de usar mal (errores comunes)
- **Monitores:** estructurados pero requieren soporte del lenguaje
- **Mensajes:** distribuibles pero overhead de comunicación

**Conexión con Tanenbaum (mos.md):** los conceptos aquí vistos son la base de los mecanismos de sincronización que se usan en sistemas reales: mutexes de pthreads (semáforo binario), variables de condición POSIX (monitores), y pipes/sockets (paso de mensajes).
-->

---

# **Resumen del Capítulo 5**

| Mecanismo | Ventajas | Desventajas |
|:----------|:---------|:------------|
| **Software** (Dekker, Peterson) | No requiere soporte HW/SO | Complejo, espera ocupada |
| **Hardware** (C&S, XCHG) | Simple, multiprocesador | Espera ocupada, inanición |
| **Semáforos** | Poderoso, flexible | Propenso a errores |
| **Monitores** | Estructurado, encapsulado | Soporte del lenguaje |
| **Mensajes** | Distribuido, comunicación | Sobrecarga |

<!--
**Términos clave — glosario para el examen:**

Estos términos aparecen con frecuencia en exámenes de SO. Los estudiantes deben poder definirlos y dar ejemplos.

**Los más importantes:**
- **Atomic:** indivisible — clave para semáforos y C&S
- **Busy waiting:** espera activa que consume CPU — el problema de los semáforos implementados con C&S
- **Condition variable:** mecanismo de bloqueo selectivo en monitores — se usa con `cwait`/`csignal`
- **Deadlock:** el clásico abrazo mortal — los 4 requisitos de Coffman
- **Livelock:** procesos que 'bailan' sin progresar — el cuarto intento de exclusión mutua
- **Mutex:** la cerradura más simple — equivalente a semáforo binario
- **Race condition:** el problema que motivó todo el capítulo
- **Semaphore:** la abstracción central — entender semWait/semSignal
- **Starvation:** cuando un proceso espera indefinidamente — el problema de dar prioridad a lectores
-->

---

# **Términos Clave**

| Término | Definición |
|:--------|:-----------|
| **Atomic** | Operación indivisible |
| **Busy waiting** | Proceso consume CPU esperando |
| **Condition variable** | Variable para bloquear/despertar en monitores |
| **Deadlock** | Procesos bloqueados esperándose mutuamente |
| **Livelock** | Procesos cambian estados sin progresar |
| **Mutex** | Cerradura de exclusión mutua |
| **Race condition** | Resultado depende del orden de ejecución |
| **Semaphore** | Entero para señalización entre procesos |
| **Starvation** | Proceso omitido indefinidamente |

---

<!-- _class: lead -->
# **Fin del Capítulo 5**
## Concurrencia: Exclusión Mutua y Sincronización

### William Stallings — Operating Systems: Internals and Design Principles (9ª Ed.)
