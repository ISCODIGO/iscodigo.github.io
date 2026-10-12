---
layout: post
title: "Dependencias funcionales y normalización"
parent: "Unidad I: Introducción a las Bases de Datos Relacionales y conceptos básicos"
grand_parent: "ISC-321 Fundamentos de Bases de Datos"
nav_order: 5
mermaid: true
---

## ¿Por qué normalizar?

- Hasta ahora la calidad del diseño dependía de la **intuición** del diseñador
- La normalización da una forma **formal** de medir si un esquema de relación es bueno
- Dos niveles de calidad:
  - **Lógico**: los usuarios entienden el significado de los atributos
  - **Implementación**: cómo se almacenan y actualizan las tuplas
- Dos metodologías:
  - **Ascendente** (*bottom-up*, síntesis): parte de relaciones entre atributos individuales
  - **Descendente** (*top-down*, análisis): parte de agrupaciones naturales (facturas, formularios, informes) y las descompone

## Esquema de trabajo: EMPRESA simplificada

```text
EMPLEADO(NombreE, Dni, FechaNac, Dirección, NúmeroDpto)
DEPARTAMENTO(NombreDpto, NúmeroDpto, DniDirector)
LOCALIZACIONES_DPTO(NúmeroDpto, UbicaciónDpto)
PROYECTO(NombreProyecto, NumProyecto, UbicaciónProyecto, NumDptoProyecto)
TRABAJA_EN(Dni, NumProyecto, Horas)
```

## Directrices informales de diseño

| # | Directriz | Problema que evita |
| --- | --- | --- |
| 1 | **Semántica clara**: no mezclar atributos de varias entidades/relaciones en una sola relación | Ambigüedad |
| 2 | **Sin anomalías** de inserción, borrado o modificación | Redundancia e inconsistencia |
| 3 | **Evitar NULL** frecuentes en relaciones base | Espacio desperdiciado, JOIN y agregados confusos |
| 4 | Concatenar solo por pares **clave principal – foreign key** | Tuplas falsas |

### Directriz 1: semántica clara

- Mal diseño: mezclar entidades en una sola relación

```text
EMP_DEPT(NombreE, Dni, FechaNac, Dirección, NúmeroDpto, NombreDpto, DniDirector)
EMP_PROY(Dni, NumProyecto, Horas, NombreE, NombreProyecto, UbicaciónProyecto)
```

- `EMP_DEPT` mezcla empleado **y** departamento; `EMP_PROY` mezcla empleado, proyecto **y** `TRABAJA_EN`
- Sirven como **vistas**, no como relaciones base

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
| **Inserción** | Nuevo empleado → repetir datos del departamento *sin errores* |
| **Inserción** | Nuevo departamento sin empleados → `NULL` en `Dni`, que es la **clave principal** |
| **Borrado** | Borrar al último empleado de un departamento → **se pierde** el departamento |
| **Modificación** | Cambiar el director del dpto. 5 → actualizar **todas** sus tuplas o queda inconsistente |

- A veces se viola a propósito por **rendimiento** → documentarlo y controlarlo (triggers, procedimientos almacenados)
- Mejor: relaciones base sin anomalías + **vistas** con los JOIN frecuentes

### Directriz 3: valores NULL

- `NULL` puede significar:
  - El atributo **no aplica**
  - El valor es **desconocido**
  - Se conoce pero **aún no se ha grabado**
- Ej.: si solo el 10 % de empleados tiene oficina → crear `OFICINAS_EMPS(DniEmpleado, NúmeroOficina)` en vez de agregar `NúmeroOficina` a `EMPLEADO`

### Directriz 4: tuplas falsas

- Descomponer `EMP_PROY` en:
  - `EMP_LOCS(NombreE, UbicaciónProyecto)`
  - `EMP_PROY1(Dni, NumProyecto, Horas, NombreProyecto, UbicaciónProyecto)`
- Al volver a unirlas (`NATURAL JOIN`) por `UbicaciónProyecto` aparecen **tuplas falsas**: filas inventadas que nunca existieron
- Causa: `UbicaciónProyecto` **no** es clave principal ni foreign key en ninguna de las dos
- Separar bien = poder unir de nuevo sin inventar filas → **reunión no aditiva** (capítulo 11)

## Dependencias funcionales

- **Dependencia funcional (DF)** `X → Y`: *si conozco X, conozco Y*
  - Dos filas con el mismo `X` **siempre** tienen el mismo `Y`
  - Ej.: con el `Dni` sé el `NombreE`
  - `X` = lado izquierdo, `Y` = lado derecho
- Si `X` es **clave candidata** ⇒ `X → Y` para cualquier `Y`
- `X → Y` **no** implica `Y → X`
- Sale del **significado** de los datos, no de lo que hay guardado hoy
  - No se confirma mirando la tabla, pero **un solo contraejemplo** la descarta

DF de `EMP_PROY`:

```text
DF1: {Dni, NumProyecto} → Horas
DF2: Dni → NombreE
DF3: NumProyecto → {NombreProyecto, UbicaciónProyecto}
```

### Contraejemplo: IMPARTIR

| Profesor | Curso | Texto |
| --- | --- | --- |
| Smith | Estructuras de datos | Bartram |
| Smith | Administración de datos | Martin |
| Hall | Compiladores | Hoffman |
| Brown | Estructuras de datos | Horowitz |

- `Texto → Curso` **parece** cumplirse, pero no se puede confirmar solo con este estado
- `Profesor → Curso` **no** se cumple: Smith imparte dos cursos

### Reglas de inferencia

- **F**: las DF que escribe el diseñador
- **Clausura F⁺**: F más todas las DF que se **deducen** de ella
  - `NúmeroDpto → DniDirector` y `DniDirector → TeléfonoDirector` ⇒ `NúmeroDpto → TeléfonoDirector`
- Notación abreviada: `{X, Y} → Z` se escribe `XY → Z`

| Regla | Nombre | Enunciado |
| --- | --- | --- |
| RI1 | **Reflexiva** | Si `X ⊇ Y` ⇒ `X → Y` (DF **trivial**) |
| RI2 | **Aumento** | `X → Y` ⇒ `XZ → YZ` |
| RI3 | **Transitiva** | `X → Y`, `Y → Z` ⇒ `X → Z` |
| RI4 | Descomposición | `X → YZ` ⇒ `X → Y` |
| RI5 | Unión | `X → Y`, `X → Z` ⇒ `X → YZ` |
| RI6 | Seudotransitiva | `X → Y`, `WY → Z` ⇒ `WX → Z` |

- **Axiomas de Armstrong** (RI1–RI3): **sólidos** y **completos** → bastan para obtener F⁺
- ⚠️ `X → A` y `Y → B` **no** implican `XY → AB`; `XY → A` **no** implica `X → A` ni `Y → A`

### Clausura de un conjunto de atributos (X⁺)

- **X⁺**: todo lo que puedo conocer si conozco `X`
- Se calcula sumando atributos hasta que ya no aparece nada nuevo; si X⁺ trae **todos**, `X` es clave

```text
Algoritmo 10.1
X⁺ := X
repetir
    antiguaX⁺ := X⁺
    por cada Y → Z en F:
        si Y ⊆ X⁺ entonces X⁺ := X⁺ ∪ Z
hasta que X⁺ = antiguaX⁺
```

Con las DF de `EMP_PROY`:

| X | X⁺ |
| --- | --- |
| `{Dni}` | `{Dni, NombreE}` |
| `{NumProyecto}` | `{NumProyecto, NombreProyecto, UbicaciónProyecto}` |
| `{Dni, NumProyecto}` | **todos** los atributos → es clave |

### Equivalencia y cobertura mínima

- **F cubre a E**: toda DF de E se puede deducir de F
- **E y F equivalentes**: dicen lo mismo aunque estén escritos distinto (`E⁺ = F⁺`)
- **Conjunto mínimo** de DF:
  1. Un **solo atributo** en el lado derecho
  2. Sin atributos **sobrantes** en el lado izquierdo
  3. Sin DF **redundantes**
- **Cobertura mínima** de E: la versión más corta que dice lo mismo que E

Ejemplo: `E = {B → A, D → A, AB → D}`

1. Ya están en forma canónica
2. `B → A` ⇒ (aumento) `B → AB`; con `AB → D` ⇒ (transitiva) `B → D` → se reemplaza `AB → D` por `B → D`
3. `B → D` y `D → A` ⇒ `B → A` es **redundante**
4. **Cobertura mínima**: `{B → D, D → A}`

## Claves y atributos

- **Superclave**: columnas que identifican una fila (puede sobrar alguna)
- **Clave**: superclave sin nada de sobra (si quitas una columna, ya no identifica)
  - `{Dni}` es clave de `EMPLEADO`; `{Dni, NombreE}` es solo superclave
- **Clave candidata**: cualquiera de las claves; una se elige como **clave principal**, el resto son **secundarias**
- **Atributo primo**: forma parte de **alguna** clave candidata
- **Atributo no primo**: un dato común, no está en ninguna clave
  - En `TRABAJA_EN`: `Dni` y `NumProyecto` son primos; `Horas` no

## Formas normales

- **Normalización** (Codd, 1972): revisar cada tabla y **partirla en tablas más pequeñas** si no pasa las pruebas
- Objetivos: **minimizar redundancia** y **anomalías**
- La **forma normal** de una relación = la más alta que cumple
- Propiedades que debe cumplir la descomposición:
  - **Reunión no aditiva**: al unir las partes no salen filas inventadas → **obligatoria**
  - **Conservación de dependencias**: ninguna DF se pierde al partir → deseable, a veces se sacrifica
- **Desnormalización**: volver a juntar tablas ya normalizadas para que las consultas sean más rápidas

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

- Cada celda guarda **un solo valor** (atómico)
- Prohíbe listas (**multivalor**), valores con partes (**compuestos**) y tablas dentro de tablas (**relaciones anidadas**)

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

- Se saca la relación anidada a otra relación y se **propaga la clave principal**:

```text
EMP_PROY1(Dni, NombreE)
EMP_PROY2(Dni, NumProyecto, Horas)
```

- Varios atributos multivalor → **una relación por cada uno**
  - `PERSONA(Dn#, {NumPermisoConducir#}, {Teléfono#})` → `P1(Dn#, NumPermisoConducir#)` y `P2(Dn#, Teléfono#)`
  - Juntarlos en una sola relación genera redundancia (problema de la **4FN**, capítulo 11)

### Segunda forma normal (2FN)

- **Dependencia total**: `Y` necesita **todo** `X`
- **Dependencia parcial**: a `Y` le basta **un pedazo** de `X`
  - `{Dni, NumProyecto} → Horas` es **total**
  - `{Dni, NumProyecto} → NombreE` es **parcial** (basta `Dni`)
- **2FN**: cada dato depende de **toda** la clave, no de un pedazo
- Si la clave tiene **un solo atributo**, ya está en 2FN

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

- **Dependencia transitiva**: `Y` depende de `X` **a través de** otro dato `Z` que no es clave (`X → Z → Y`)
  - `Dni → NúmeroDpto → DniDirector`
- **3FN** (Codd): está en 2FN **y** ningún dato depende de **otro dato** que no es clave

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
| **2FN** | (Clave compuesta) ningún atributo no clave depende de **parte** de la clave | Nueva relación por cada parte de la clave con sus dependientes; mantener la original con lo que depende de la clave completa |
| **3FN** | Ningún atributo no clave depende de **otro atributo no clave** | Nueva relación con el atributo no clave y lo que determina |

## Definiciones generales de 2FN y 3FN

- Las anteriores solo miran la **clave principal**; las generales consideran **todas las claves candidatas**
- **2FN general**: ningún atributo no primo depende **parcialmente** de **ninguna** clave
- **3FN general**: para toda DF no trivial `X → A`:
  - **(a)** `X` es **superclave**, o
  - **(b)** `A` es **atributo primo**
- **Definición alternativa de 3FN**: todo atributo no primo
  - depende **totalmente** de **cada** clave, y
  - **no** depende **transitivamente** de ninguna clave
- La definición general se aplica **directamente**, sin pasar antes por 2FN

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

- **BCNF**: solo una **clave** (superclave) puede decidir el valor de otra columna
  - Formal: para toda DF no trivial `X → A`, `X` es **superclave**
- Es 3FN **sin** la condición (b): ya no basta que `A` sea primo
- Toda relación en BCNF está en 3FN; **no** al revés
- En la práctica, casi todas las relaciones en 3FN también están en BCNF

### PARCELAS1A con FD5

- Parcelas solo en Getafe y Alcorcón, con áreas distintas en cada municipio → **FD5**: `Área → NombreMunicipio`
- Sigue en **3FN** (`NombreMunicipio` es primo), pero **no en BCNF** (`Área` no es superclave)
- Descomposición BCNF:
  - `PARCELAS1AX(IdPropiedad, Área, NúmeroParcela)`
  - `PARCELAS1AY(Área, NombreMunicipio)`
- ⚠️ Se **pierde FD2**: sus atributos ya no están juntos

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
- 3FN pero **no** BCNF (`Profesor` no es superclave)

| Descomposición | ¿Tuplas falsas? |
| --- | --- |
| `{Estudiante, Profesor}` y `{Estudiante, Curso}` | Sí |
| `{Curso, Profesor}` y `{Curso, Estudiante}` | Sí |
| ✅ `{Profesor, Curso}` y `{Profesor, Estudiante}` | **No** |

- Las tres pierden **FD1**; se prefiere la que garantiza la **reunión no aditiva**

## Resumen

- Directrices informales: semántica clara, sin anomalías, pocos NULL, sin tuplas falsas
- **DF**: restricción semántica entre atributos; se infieren con los **axiomas de Armstrong**
- **1FN** atómico → **2FN** sin parciales → **3FN** sin transitivas → **BCNF** todo determinante es superclave
- Meta práctica: **3FN o BCNF**; 1FN y 2FN son solo pasos intermedios
- Siguiente paso: propiedades de la descomposición, **4FN** y **5FN** (capítulo 11)

[⬅️ Volver a Unidad I](./index.md)
