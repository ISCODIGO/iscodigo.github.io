---
layout: post
title: "Dependencias funcionales y normalización"
parent: "Unidad III: Normalización y Transacciones"
grand_parent: "ISC-321 Fundamentos de Bases de Datos"
nav_order: 1
mermaid: true
---

## ¿Por qué normalizar?

- Hasta ahora juzgábamos un diseño por **intuición**
- La normalización da criterios **formales** para decidir si un esquema de relación es bueno
- Se evalúa en dos niveles:
  - **Lógico**: ¿los usuarios entienden qué significa cada atributo?
  - **Implementación**: ¿cómo se almacenan y actualizan las tuplas?
- Hay dos formas de diseñar:
  - **Ascendente** (*bottom-up*, síntesis): se parte de los atributos sueltos y se agrupan
  - **Descendente** (*top-down*, análisis): se parte de agrupaciones naturales (facturas, formularios, informes) y se descomponen

## Esquema de trabajo: EMPRESA simplificada

```text
EMPLEADO(NombreE, Dni, FechaNac, Dirección, NúmeroDpto)
DEPARTAMENTO(NombreDpto, NúmeroDpto, DniDirector)
LOCALIZACIONES_DPTO(NúmeroDpto, UbicaciónDpto)
PROYECTO(NombreProyecto, NumProyecto, UbicaciónProyecto, NumDptoProyecto)
TRABAJA_EN(Dni, NumProyecto, Horas)
```

Relaciones mal diseñadas que se usan como ejemplo, con la forma normal que violan:

```text
DEPARTAMENTO(NombreDpto, NúmeroDpto, DniDirector, {UbicacionesDpto})             -- no 1FN
EMP_PROY(Dni, NombreE, {PROYS(NumProyecto, Horas)})                              -- no 1FN
EMP_PROY(Dni, NumProyecto, Horas, NombreE, NombreProyecto, UbicaciónProyecto)    -- no 2FN
EMP_DEPT(NombreE, Dni, FechaNac, Dirección, NúmeroDpto, NombreDpto, DniDirector) -- no 3FN
PARCELAS(IdPropiedad, NombreMunicipio, NúmeroParcela, Área, Precio, Impuestos)   -- no 2FN
PARCELAS1A(IdPropiedad, NombreMunicipio, NúmeroParcela, Área)                    -- no BCNF
ENSEÑAR(Estudiante, Curso, Profesor)                                             -- no BCNF
```

## Directrices informales de diseño

| # | Directriz | Problema que evita |
| --- | --- | --- |
| 1 | **Semántica clara**: cada relación describe una sola entidad o relación del modelo | Ambigüedad |
| 2 | **Sin anomalías** de inserción, borrado o modificación | Redundancia e inconsistencia |
| 3 | **Pocos NULL** en las relaciones base | Espacio desperdiciado; JOIN y agregados difíciles de interpretar |
| 4 | Concatenar solo por pares **clave principal – clave externa** | Tuplas falsas |

### Directriz 1: semántica clara

- Ejemplo de mal diseño:

```text
EMP_DEPT(NombreE, Dni, FechaNac, Dirección, NúmeroDpto, NombreDpto, DniDirector)
EMP_PROY(Dni, NumProyecto, Horas, NombreE, NombreProyecto, UbicaciónProyecto)
```

- `EMP_DEPT` mezcla empleado **y** departamento; `EMP_PROY` mezcla empleado, proyecto **y** `TRABAJA_EN`
- Están bien como **vistas**, no como relaciones base

✅ Diseño válido: una relación por entidad, unidas por una clave externa

```text
EMPLEADO(NombreE, Dni, FechaNac, Dirección, NúmeroDpto)
DEPARTAMENTO(NombreDpto, NúmeroDpto, DniDirector)
```

- `EMPLEADO` describe solo empleados y `DEPARTAMENTO` solo departamentos
- `EMPLEADO.NúmeroDpto` es la clave externa que las relaciona

### Directriz 2: redundancia y anomalías

En `EMP_DEPT` los datos del departamento se **repiten** por cada empleado:

| NombreE | Dni | NúmeroDpto | NombreDpto | DniDirector |
| --- | --- | --- | --- | --- |
| Pérez Pérez, José | 123456789 | 5 | Investigación | 333445555 |
| Campos Sastre, Alberto | 333445555 | 5 | Investigación | 333445555 |
| Jiménez Celaya, Alicia | 999887777 | 4 | Administración | 987654321 |
| Sainz Oreja, Juana | 987654321 | 4 | Administración | 987654321 |

| Anomalía | Ejemplo en `EMP_DEPT` |
| --- | --- |
| **Inserción** | Cada empleado nuevo obliga a copiar los datos de su departamento, y una errata deja datos contradictorios |
| **Inserción** | Un departamento sin empleados no se puede insertar: quedaría `NULL` en `Dni`, la **clave principal** |
| **Borrado** | Al borrar al último empleado de un departamento **se pierde** el departamento |
| **Modificación** | Cambiar el director del dpto. 5 obliga a actualizar **todas** sus tuplas; si falta una, hay inconsistencia |

✅ Diseño válido: los mismos datos en `EMPLEADO` y `DEPARTAMENTO`

| NombreE | Dni | NúmeroDpto |
| --- | --- | --- |
| Pérez Pérez, José | 123456789 | 5 |
| Campos Sastre, Alberto | 333445555 | 5 |
| Jiménez Celaya, Alicia | 999887777 | 4 |
| Sainz Oreja, Juana | 987654321 | 4 |

| NombreDpto | NúmeroDpto | DniDirector |
| --- | --- | --- |
| Investigación | 5 | 333445555 |
| Administración | 4 | 987654321 |
| Sede central | 1 | 888665555 |

- Cada departamento aparece **una sola vez**, así que desaparecen las anomalías:
  - **Inserción**: `Sede central` existe aunque todavía no tenga empleados en la tabla
  - **Borrado**: si se borra a Jiménez y a Sainz, el departamento 4 sigue en `DEPARTAMENTO`
  - **Modificación**: cambiar el director del dpto. 5 es actualizar **una** tupla

- A veces se acepta redundancia a propósito por **rendimiento**; en ese caso se documenta y se controla con triggers o procedimientos almacenados
- Lo habitual: relaciones base sin anomalías y **vistas** para los JOIN frecuentes

### Directriz 3: valores NULL

- `NULL` puede significar:
  - El atributo **no aplica**
  - El valor es **desconocido**
  - Existe pero **aún no se ha registrado**
- Como no se sabe cuál de los tres es, conviene evitarlo
- La decisión sale de los **requisitos**, no de contar datos: si un atributo, por regla del negocio, **no aplica** a la mayoría de las tuplas, va en una relación aparte
  - Ej.: solo el personal administrativo tiene oficina asignada; los técnicos de campo nunca la tienen. En vez de agregar `NúmeroOficina` a `EMPLEADO`, crear `OFICINAS_EMPS(DniEmpleado, NúmeroOficina)`

✅ Diseño válido: solo tienen tupla en `OFICINAS_EMPS` los empleados con oficina

| DniEmpleado | NúmeroOficina |
| --- | --- |
| 333445555 | B-204 |
| 987654321 | A-101 |

- `EMPLEADO` no tiene ningún `NULL` por oficina
- Los empleados sin oficina simplemente **no aparecen** en `OFICINAS_EMPS`
- Para listar empleados con su oficina (si la tienen): `EMPLEADO LEFT JOIN OFICINAS_EMPS`

### Directriz 4: tuplas falsas

- Descomponer `EMP_PROY` en:
  - `EMP_LOCS(NombreE, UbicaciónProyecto)`
  - `EMP_PROY1(Dni, NumProyecto, Horas, NombreProyecto, UbicaciónProyecto)`
- Al volver a unirlas (`NATURAL JOIN`) por `UbicaciónProyecto` aparecen **tuplas falsas**: tuplas que no estaban en la relación original
- Causa: `UbicaciónProyecto` **no** es clave principal ni clave externa en ninguna de las dos
- Una buena descomposición permite reconstruir la relación original sin tuplas falsas: es la **reunión no aditiva** (capítulo 11)

✅ Diseño válido: descomponer `EMP_PROY` de modo que cada JOIN use una clave

```text
EMPLEADO(Dni, NombreE)
PROYECTO(NumProyecto, NombreProyecto, UbicaciónProyecto)
TRABAJA_EN(Dni, NumProyecto, Horas)
```

- `TRABAJA_EN.Dni` → `EMPLEADO.Dni` y `TRABAJA_EN.NumProyecto` → `PROYECTO.NumProyecto` son pares clave externa – clave principal
- `TRABAJA_EN ⋈ EMPLEADO ⋈ PROYECTO` reconstruye exactamente `EMP_PROY`: cada tupla de `TRABAJA_EN` encuentra **un solo** empleado y **un solo** proyecto

## Dependencias funcionales

- **Dependencia funcional (DF)** `X → Y`: el valor de `X` determina el valor de `Y`
  - Dos tuplas con el mismo `X` **siempre** tienen el mismo `Y`
  - Ej.: `Dni → NombreE`; a cada `Dni` le corresponde un solo nombre
  - `X` es el lado izquierdo (determinante); `Y`, el lado derecho
- Si `X` es **clave candidata**, entonces `X → Y` para cualquier conjunto de atributos `Y`
- `X → Y` **no** implica `Y → X`
- Una DF sale del **significado** de los datos, no del contenido actual de la tabla
  - Mirar la tabla no la confirma, pero **un solo contraejemplo** la descarta

DF de `EMP_PROY`:

```text
DF1: {Dni, NumProyecto} → Horas
DF2: Dni → NombreE
DF3: NumProyecto → {NombreProyecto, UbicaciónProyecto}
```

**Diagrama de DF**: cada flecha sale del determinante y llega a lo que determina

```mermaid
flowchart LR
    K(["Dni + NumProyecto"]) -->|DF1| H[Horas]
    D([Dni]) -->|DF2| N[NombreE]
    P([NumProyecto]) -->|DF3| NP[NombreProyecto]
    P -->|DF3| U[UbicaciónProyecto]

    classDef det fill:#fff4e0,stroke:#c98a1b,stroke-width:2px,color:#1b2b40
    classDef dep fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    class K,D,P det
    class H,N,NP,U dep
```

### Contraejemplo: IMPARTIR

| Profesor | Curso | Texto |
| --- | --- | --- |
| Smith | Estructuras de datos | Bartram |
| Smith | Administración de datos | Martin |
| Hall | Compiladores | Hoffman |
| Brown | Estructuras de datos | Horowitz |

- `Texto → Curso` **parece** cumplirse, pero este estado de la tabla no basta para confirmarlo
- `Profesor → Curso` **no** se cumple: Smith imparte dos cursos

### Reglas de inferencia

- El diseñador escribe solo las DF **evidentes**, pero de ellas se deducen otras que nadie escribió
  - `NúmeroDpto → DniDirector` y `DniDirector → TeléfonoDirector` ⇒ `NúmeroDpto → TeléfonoDirector`
  - Esa DF implícita también es una restricción: la base de datos no puede violarla
- **F**: las DF que especifica el diseñador
- **Clausura F⁺**: F más todas las DF que se **deducen** de F
- Las **reglas de inferencia** dicen qué deducciones son válidas
- Notación: `{X, Y} → Z` se abrevia `XY → Z`

| Regla | Nombre | Enunciado | Idea | Ejemplo |
| --- | --- | --- | --- | --- |
| RI1 | **Reflexiva** | Si `X ⊇ Y` ⇒ `X → Y` | Un conjunto determina cualquier parte de sí mismo (DF **trivial**) | `{Dni, NombreE} → NombreE` |
| RI2 | **Aumento** | `X → Y` ⇒ `XZ → YZ` | Agregar el mismo atributo a ambos lados no rompe la DF | `Dni → NombreE` ⇒ `{Dni, NumProyecto} → {NombreE, NumProyecto}` |
| RI3 | **Transitiva** | `X → Y`, `Y → Z` ⇒ `X → Z` | Las DF se encadenan | `NúmeroDpto → DniDirector`, `DniDirector → TeléfonoDirector` ⇒ `NúmeroDpto → TeléfonoDirector` |
| RI4 | Descomposición | `X → YZ` ⇒ `X → Y` | Si determino un conjunto, determino cada parte | `NumProyecto → {NombreProyecto, UbicaciónProyecto}` ⇒ `NumProyecto → NombreProyecto` |
| RI5 | Unión | `X → Y`, `X → Z` ⇒ `X → YZ` | Lo que `X` determina por separado lo determina junto | `Dni → NombreE`, `Dni → Dirección` ⇒ `Dni → {NombreE, Dirección}` |
| RI6 | Seudotransitiva | `X → Y`, `WY → Z` ⇒ `WX → Z` | Se puede sustituir `Y` por algo que lo determina | `NombreE → Dni`, `{Dni, NumProyecto} → Horas` ⇒ `{NombreE, NumProyecto} → Horas` (si `NombreE` fuera único) |

- **Axiomas de Armstrong** (RI1–RI3): son **sólidos** y **completos**, así que bastan para obtener F⁺
  - **Sólidos**: nunca producen una DF falsa
  - **Completos**: aplicándolos repetidamente se obtienen **todas** las DF de F⁺
  - RI4–RI6 se demuestran a partir de RI1–RI3; son atajos

Ejemplo: demostrar la descomposición (RI4) con los axiomas

1. `X → YZ` (dada)
2. `YZ → Y` (reflexiva: `YZ ⊇ Y`)
3. `X → Y` (transitiva con 1 y 2)

Ejemplo: deducir una DF nueva. Con `F = {A → B, BC → D}`, ¿se cumple `AC → D`?

1. `A → B` (dada)
2. `AC → BC` (aumento con `C`)
3. `BC → D` (dada)
4. `AC → D` (transitiva con 2 y 3) ✅

- ⚠️ Errores comunes:
  - `XY → A` **no** implica `X → A` ni `Y → A`
    - Ej.: `{Dni, NumProyecto} → Horas`, pero ni `Dni → Horas` ni `NumProyecto → Horas`
  - En cambio, `X → A` y `Y → B` **sí** implican `XY → AB` (aumento y transitiva)
  - `X → Y` **no** implica `Y → X`
    - Ej.: `Dni → NombreE`, pero dos empleados pueden llamarse igual

### Clausura de un conjunto de atributos (X⁺)

- Calcular F⁺ completa no es práctico: puede tener una cantidad **exponencial** de DF
- En su lugar se calcula **X⁺**: todos los atributos que `X` determina, directa o indirectamente
- Para qué sirve:
  - **Comprobar una DF**: `X → Y` está en F⁺ si y solo si `Y ⊆ X⁺`
  - **Encontrar claves**: si X⁺ contiene **todos** los atributos de la relación, `X` es superclave; si además ningún subconjunto propio de `X` lo logra, es clave
  - **Comparar conjuntos de DF** y **calcular la cobertura mínima** (siguiente sección)

Algoritmo 10.1, en palabras:

1. Empezar con X⁺ = `X` (por la regla reflexiva)
2. Recorrer F: si el **lado izquierdo** de una DF ya está **dentro** de X⁺, agregar su lado derecho
3. Repetir el paso 2 mientras se agregue algo nuevo; cuando una pasada completa no agrega nada, X⁺ está terminado

```text
X⁺ := X
repetir
    antiguaX⁺ := X⁺
    por cada Y → Z en F:
        si Y ⊆ X⁺ entonces X⁺ := X⁺ ∪ Z
hasta que X⁺ = antiguaX⁺
```

Traza: `R(A, B, C, D, E)` con `F = {A → B, B → C, CD → E}`. Calcular `{A, D}⁺`:

| Paso | DF usada | ¿Lado izquierdo ⊆ X⁺? | X⁺ |
| --- | --- | --- | --- |
| inicio | — | — | `{A, D}` |
| 1 | `A → B` | `A` ✅ | `{A, B, D}` |
| 2 | `B → C` | `B` ✅ | `{A, B, C, D}` |
| 3 | `CD → E` | `C, D` ✅ | `{A, B, C, D, E}` |
| 4 | otra pasada | nada nuevo | fin |

```mermaid
flowchart LR
    S0["{A, D}"] -->|"A → B"| S1["{A, B, D}"]
    S1 -->|"B → C"| S2["{A, B, C, D}"]
    S2 -->|"CD → E"| S3["<b>{A, B, C, D, E}</b><br/>todos los atributos"]

    classDef paso fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef fin fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    class S0,S1,S2 paso
    class S3 fin
```

- `{A, D}⁺` contiene todos los atributos → `{A, D}` es superclave
- `A⁺ = {A, B, C}` y `D⁺ = {D}` no alcanzan → `{A, D}` es **clave**
- El orden de las DF solo cambia cuántas pasadas se necesitan, no el resultado

Con las DF de `EMP_PROY`:

| X | X⁺ | Conclusión |
| --- | --- | --- |
| `{Dni}` | `{Dni, NombreE}` | No es clave |
| `{NumProyecto}` | `{NumProyecto, NombreProyecto, UbicaciónProyecto}` | No es clave |
| `{Dni, NumProyecto}` | **todos** los atributos | Es clave |

### Equivalencia y cobertura mínima

- Dos diseñadores pueden escribir las mismas restricciones de formas distintas; hace falta saber si dicen **lo mismo**
- **F cubre a E**: toda DF de E se puede deducir de F
  - Se comprueba con clausuras: para cada `X → Y` de E, calcular `X⁺` **usando F** y verificar que `Y ⊆ X⁺`
- **E y F equivalentes**: F cubre a E **y** E cubre a F (`E⁺ = F⁺`)

Ejemplo: `F = {A → C, AC → D, E → AD, E → H}` y `G = {A → CD, E → AH}`

| ¿G cubre a F? | X⁺ con G | ¿Contiene el lado derecho? |
| --- | --- | --- |
| `A → C` | `A⁺ = {A, C, D}` | ✅ |
| `AC → D` | `AC⁺ = {A, C, D}` | ✅ |
| `E → AD` | `E⁺ = {E, A, H, C, D}` | ✅ |
| `E → H` | `E⁺ = {E, A, H, C, D}` | ✅ |

| ¿F cubre a G? | X⁺ con F | ¿Contiene el lado derecho? |
| --- | --- | --- |
| `A → CD` | `A⁺ = {A, C, D}` | ✅ |
| `E → AH` | `E⁺ = {E, A, D, H, C}` | ✅ |

- Se cubren mutuamente → son **equivalentes**; G dice lo mismo con menos DF

#### Cobertura mínima

- **Conjunto mínimo** de DF:
  1. Un **solo atributo** en el lado derecho
  2. Sin atributos **sobrantes** en el lado izquierdo
  3. Sin DF **redundantes**
- **Cobertura mínima** de E: un conjunto mínimo equivalente a E
  - Es la forma más compacta de escribir las restricciones: menos DF que el SGBD debe verificar
  - Es el punto de partida del algoritmo de síntesis en 3FN (capítulo 11)
  - No siempre es única: el resultado puede depender del orden en que se revisan las DF

Algoritmo 10.2, en palabras:

1. **Separar** los lados derechos: `X → AB` pasa a `X → A` y `X → B` (descomposición)
2. **Quitar atributos sobrantes** de los lados izquierdos: en `X → A`, el atributo `B ∈ X` sobra si `A ∈ (X − {B})⁺`, calculada con el conjunto **actual**
3. **Quitar DF redundantes**: `X → A` sobra si `A ∈ X⁺` calculada **sin** esa DF

- El paso 2 va **antes** que el 3: al acortar un lado izquierdo pueden aparecer DF redundantes nuevas

Ejemplo: `E = {B → A, D → A, AB → D}`

1. **Separar**: todas tienen ya un solo atributo a la derecha
2. **Sobrantes** (solo `AB → D` tiene más de un atributo a la izquierda):
   - ¿Sobra `A`? `B⁺ = {B, A, D}` contiene `D` → **sí**, se reemplaza `AB → D` por `B → D`
   - ¿Sobra `B`? `A⁺ = {A}` no contiene `D` → no
   - Queda `{B → A, D → A, B → D}`
3. **Redundantes**:
   - `B → A`: sin ella, `B⁺ = {B, D, A}` contiene `A` → **redundante**, se elimina
   - `D → A`: sin ella, `D⁺ = {D}` → se queda
   - `B → D`: sin ella, `B⁺ = {B}` → se queda
4. **Cobertura mínima**: `{B → D, D → A}`

```mermaid
flowchart LR
    subgraph E["E (original)"]
        direction LR
        EB([B]) -->|"B → A"| EA[A]
        ED([D]) -->|"D → A"| EA
        EAB(["A + B"]) -->|"AB → D"| ED
    end
    subgraph M["Cobertura mínima"]
        direction LR
        MB([B]) -->|"B → D"| MD([D]) -->|"D → A"| MA[A]
    end
    E ==>|"quitar A sobrante<br/>y B → A redundante"| M

    classDef orig fill:#fff4e0,stroke:#c98a1b,stroke-width:2px,color:#1b2b40
    classDef ok fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    class EB,ED,EA,EAB orig
    class MB,MD,MA ok
    style E fill:#fbfcfd,stroke:#c3ccd7,color:#33414f
    style M fill:#fbfcfd,stroke:#c3ccd7,color:#33414f
```

- En la cobertura mínima `B → A` ya no hace falta escribirla: se obtiene siguiendo la cadena `B → D → A`

## Claves y atributos

- **Superclave**: conjunto de atributos que identifica cada tupla (puede sobrar alguno)
- **Clave**: superclave mínima; si se quita cualquier atributo, deja de identificar
  - `{Dni}` es clave de `EMPLEADO`; `{Dni, NombreE}` es solo superclave
- **Clave candidata**: cualquiera de las claves de la relación; una se elige como **clave principal** y las demás son **secundarias**
- **Atributo primo**: forma parte de **alguna** clave candidata
- **Atributo no primo**: no forma parte de ninguna clave candidata
  - En `TRABAJA_EN`: `Dni` y `NumProyecto` son primos; `Horas` no

## Formas normales

- **Normalización** (Codd, 1972): someter cada relación a una serie de pruebas y **descomponer** las que no las pasan
- Objetivo: **minimizar la redundancia** y las **anomalías**
- La **forma normal** de una relación es la más alta que cumple
- Propiedades de una buena descomposición:
  - **Reunión no aditiva**: al unir las partes no aparecen tuplas falsas. **Obligatoria**
  - **Conservación de dependencias**: cada DF sigue pudiéndose comprobar en alguna de las partes. Deseable; a veces se sacrifica
- **Desnormalización**: volver a unir relaciones normalizadas para acelerar consultas frecuentes

```mermaid
flowchart LR
    N0["No normalizada"] -->|"atributos atómicos"| N1["<b>1FN</b>"]
    N1 -->|"sin dependencias<br/>parciales"| N2["<b>2FN</b>"]
    N2 -->|"sin dependencias<br/>transitivas"| N3["<b>3FN</b>"]
    N3 -->|"todo determinante<br/>es superclave"| NB["<b>BCNF</b>"]

    classDef fn fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef bad fill:#fbfcfd,stroke:#c3ccd7,color:#33414f
    class N1,N2,N3,NB fn
    class N0 bad
```

### Primera forma normal (1FN)

- Cada atributo de cada tupla tiene **un solo valor atómico**
- Prohíbe atributos **multivalor** (listas), **compuestos** (valores con partes) y **relaciones anidadas** (tablas dentro de tablas)

No está en 1FN:

| NombreDpto | NúmeroDpto | DniDirector | UbicacionesDpto |
| --- | --- | --- | --- |
| Investigación | 5 | 333445555 | {Valencia, Sevilla, Madrid} |
| Administración | 4 | 987654321 | {Gijón} |
| Sede central | 1 | 888665555 | {Madrid} |

Tres formas de llevarla a 1FN:

| Opción | Resultado | Desventaja |
| --- | --- | --- |
| ✅ **1. Nueva relación** `LOCALIZACIONES_DPTO(NúmeroDpto, UbicaciónDpto)` | Sin redundancia, general | — |
| 2. Expandir la clave a `{NúmeroDpto, UbicaciónDpto}` | Una tupla por ubicación | **Redundancia** |
| 3. Columnas `UbicaciónDpto1`, `UbicaciónDpto2`, `UbicaciónDpto3` | Máximo fijo | **NULL**, orden confuso, consultas difíciles |

#### Relaciones anidadas

```text
EMP_PROY(Dni, NombreE, {PROYS(NumProyecto, Horas)})
```

- La relación anidada pasa a una relación propia que **incluye la clave principal** de la externa:

```text
EMP_PROY1(Dni, NombreE)
EMP_PROY2(Dni, NumProyecto, Horas)
```

- Si hay varios atributos multivalor, se crea **una relación para cada uno**
  - `PERSONA(Dn#, {NumPermisoConducir#}, {Teléfono#})` → `P1(Dn#, NumPermisoConducir#)` y `P2(Dn#, Teléfono#)`
  - Ponerlos juntos en una sola relación genera redundancia (es el problema que resuelve la **4FN**, capítulo 11)

### Segunda forma normal (2FN)

- **Dependencia total** `X → Y`: si se quita cualquier atributo de `X`, la DF deja de cumplirse
- **Dependencia parcial**: una **parte** de `X` ya basta para determinar `Y`
  - `{Dni, NumProyecto} → Horas` es **total**
  - `{Dni, NumProyecto} → NombreE` es **parcial** (basta `Dni`)
- **2FN**: todo atributo no primo depende **totalmente** de la clave principal
- Si la clave principal tiene **un solo atributo**, la relación ya está en 2FN

`EMP_PROY` → 2FN:

```mermaid
flowchart TD
    EP["<b>EMP_PROY</b><br/>Dni, NumProyecto, Horas, NombreE,<br/>NombreProyecto, UbicaciónProyecto"]
    EP --> EP1["<b>EP1</b><br/><u>Dni</u>, <u>NumProyecto</u>, Horas<br/><i>DF1</i>"]
    EP --> EP2["<b>EP2</b><br/><u>Dni</u>, NombreE<br/><i>DF2</i>"]
    EP --> EP3["<b>EP3</b><br/><u>NumProyecto</u>, NombreProyecto,<br/>UbicaciónProyecto<br/><i>DF3</i>"]

    classDef orig fill:#fff4e0,stroke:#c98a1b,stroke-width:2px,color:#1b2b40
    classDef ok fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    class EP orig
    class EP1,EP2,EP3 ok
```

### Tercera forma normal (3FN)

- **Dependencia transitiva**: `X → Y` se cumple **a través de** un atributo `Z` que no es clave ni parte de una (`X → Z` y `Z → Y`)
  - `Dni → NúmeroDpto → DniDirector`
- **3FN** (Codd): está en 2FN **y** ningún atributo no primo depende transitivamente de la clave principal

`EMP_DEPT` → 3FN:

```mermaid
flowchart TD
    ED["<b>EMP_DEPT</b><br/>NombreE, Dni, FechaNac, Dirección,<br/>NúmeroDpto, NombreDpto, DniDirector"]
    ED --> ED1["<b>ED1</b><br/>NombreE, <u>Dni</u>, FechaNac,<br/>Dirección, NúmeroDpto"]
    ED --> ED2["<b>ED2</b><br/><u>NúmeroDpto</u>, NombreDpto, DniDirector"]

    classDef orig fill:#fff4e0,stroke:#c98a1b,stroke-width:2px,color:#1b2b40
    classDef ok fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    class ED orig
    class ED1,ED2 ok
```

- `ED1 NATURAL JOIN ED2` recupera `EMP_DEPT` **sin tuplas falsas**

### Resumen 1FN – 3FN

| Forma normal | Prueba | Remedio |
| --- | --- | --- |
| **1FN** | Sin atributos multivalor ni relaciones anidadas | Nueva relación por cada atributo multivalor o relación anidada |
| **2FN** | (Clave compuesta) ningún atributo no primo depende de **parte** de la clave | Una relación nueva por cada parte de la clave, con sus dependientes; la original conserva lo que depende de la clave completa |
| **3FN** | Ningún atributo no primo depende de **otro atributo no primo** | Una relación nueva con ese atributo y los que determina |

## Definiciones generales de 2FN y 3FN

- Las definiciones anteriores solo miran la **clave principal**; las generales consideran **todas las claves candidatas**
- **2FN general**: ningún atributo no primo depende **parcialmente** de **ninguna** clave
- **3FN general**: para toda DF no trivial `X → A`:
  - **(a)** `X` es **superclave**, o
  - **(b)** `A` es **atributo primo**
- **Definición alternativa de 3FN**: todo atributo no primo
  - depende **totalmente** de **cada** clave, y
  - **no** depende **transitivamente** de ninguna clave
- La definición general de 3FN se puede comprobar **directamente**, sin verificar antes la 2FN

### Ejemplo: PARCELAS

```text
PARCELAS(IdPropiedad, NombreMunicipio, NúmeroParcela, Área, Precio, Impuestos)
```

| DF | Significado |
| --- | --- |
| FD1: `IdPropiedad → resto` | Clave candidata (elegida como principal) |
| FD2: `{NombreMunicipio, NúmeroParcela} → resto` | Otra clave candidata |
| FD3: `NombreMunicipio → Impuestos` | Impuesto fijo por municipio |
| FD4: `Área → Precio` | El precio depende del área |

```mermaid
flowchart TD
    P["<b>PARCELAS</b> · 1FN"] -->|"FD3 es parcial<br/>(viola 2FN)"| P1["<b>PARCELAS1</b><br/>IdPropiedad, NombreMunicipio,<br/>NúmeroParcela, Área, Precio"]
    P --> P2["<b>PARCELAS2</b> · 3FN<br/>NombreMunicipio, Impuestos"]
    P1 -->|"FD4 es transitiva<br/>(viola 3FN)"| P1A["<b>PARCELAS1A</b> · 3FN<br/>IdPropiedad, NombreMunicipio,<br/>NúmeroParcela, Área"]
    P1 --> P1B["<b>PARCELAS1B</b> · 3FN<br/>Área, Precio"]

    classDef orig fill:#fff4e0,stroke:#c98a1b,stroke-width:2px,color:#1b2b40
    classDef mid fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef ok fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    class P orig
    class P1 mid
    class P2,P1A,P1B ok
```

- Las dependencias parciales y transitivas se pueden eliminar **en cualquier orden**

## Forma normal de Boyce-Codd (BCNF)

- **BCNF**: para toda DF no trivial `X → A`, `X` es **superclave**
  - Dicho de otro modo: todo determinante es superclave
- Es la 3FN general **sin** la condición (b): ya no basta con que `A` sea primo
- Toda relación en BCNF está en 3FN; **no** al revés
- En la práctica, la mayoría de las relaciones en 3FN también están en BCNF

### PARCELAS1A con FD5

- Supongamos que solo hay parcelas en Getafe y Alcorcón, y que los tamaños posibles de parcela no coinciden entre los dos municipios. Entonces el área indica el municipio: **FD5**: `Área → NombreMunicipio`
- La relación sigue en **3FN** (`NombreMunicipio` es primo), pero **no en BCNF** (`Área` no es superclave)
- Descomposición en BCNF:
  - `PARCELAS1AX(IdPropiedad, Área, NúmeroParcela)`
  - `PARCELAS1AY(Área, NombreMunicipio)`
- ⚠️ Se **pierde FD2**: sus atributos quedan en relaciones distintas

### ENSEÑAR

| Estudiante | Curso | Profesor |
| --- | --- | --- |
| Campos | Bases de datos | Marcos |
| Pérez | Bases de datos | María |
| Pérez | Sistemas operativos | Amanda |
| Pérez | Teoría | Sergio |
| Ochoa | Bases de datos | Marcos |
| Ochoa | Sistemas operativos | Aurora |
| Morera | Bases de datos | Eduardo |
| Celaya | Bases de datos | María |
| Campos | Sistemas operativos | Amanda |

- FD1: `{Estudiante, Curso} → Profesor`
- FD2: `Profesor → Curso`
- Está en 3FN (`Curso` es primo), pero **no** en BCNF (`Profesor` no es superclave)

| Descomposición | ¿Tuplas falsas? |
| --- | --- |
| `{Estudiante, Profesor}` y `{Estudiante, Curso}` | Sí |
| `{Curso, Profesor}` y `{Curso, Estudiante}` | Sí |
| ✅ `{Profesor, Curso}` y `{Profesor, Estudiante}` | **No** |

- Las tres pierden **FD1**, así que se elige la que garantiza la **reunión no aditiva**

## Resumen

- Directrices informales: semántica clara, sin anomalías, pocos NULL, sin tuplas falsas
- **DF**: restricción semántica entre atributos; las DF implícitas se deducen con los **axiomas de Armstrong**
- **1FN**: valores atómicos → **2FN**: sin dependencias parciales → **3FN**: sin dependencias transitivas → **BCNF**: todo determinante es superclave
- En la práctica se busca **3FN o BCNF**; 1FN y 2FN son pasos intermedios
- Siguiente paso: propiedades de la descomposición, **4FN** y **5FN** (capítulo 11)

[⬅️ Volver a Unidad III](./index.md)
