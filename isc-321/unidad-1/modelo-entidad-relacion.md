---
layout: post
title: "Modelado de datos con el modelo Entidad-Relación (ER)"
parent: "Unidad I: Introducción a las Bases de Datos Relacionales y conceptos básicos"
grand_parent: "ISC-321 Fundamentos de Bases de Datos"
nav_order: 3
mermaid: true
---

## Proceso de diseño de una base de datos

- **Requisitos de datos** y **requisitos funcionales** → entrevistas con los usuarios
- **Esquema conceptual**: entidades, relaciones y restricciones → *independiente del DBMS*
- **Diseño lógico**: mapeo al modelo del DBMS (relacional…)
- **Diseño físico**: almacenamiento, índices, rutas de acceso

```mermaid
flowchart TD
    MM["<b>Minimundo</b>"] --> REQ["<b>Recopilación y análisis<br/>de requisitos</b>"]
    REQ --> FR["Requisitos funcionales"]
    REQ --> DR["Requisitos de datos"]

    FR --> AF["<b>Análisis funcional</b><br/>Especificación de transacción<br/>de alto nivel"]
    DR --> DC["<b>Diseño conceptual</b><br/>Esquema conceptual<br/><i>independiente del DBMS</i>"]

    DC --> DL["<b>Diseño lógico</b><br/>(mapeado del modelo de datos)<br/>Esquema lógico<br/><i>específico del DBMS</i>"]
    AF --> DA["<b>Diseño de la aplicación</b>"]
    DL --> DF["<b>Diseño físico</b><br/>Esquema interno"]
    DA --> IT["<b>Implementación<br/>de la transacción</b>"]
    DF --> APP["Aplicaciones"]
    IT --> APP

    classDef raiz fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef fase fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef detalle fill:#fbfcfd,stroke:#c3ccd7,color:#33414f
    class MM raiz
    class REQ,DC,DL,DF fase
    class FR,DR,AF,DA,IT,APP detalle
```

## Caso de estudio: EMPRESA

- **DEPARTAMENTO**: nombre y número únicos, un director (con fecha de inicio), varias ubicaciones
- **PROYECTO**: nombre y número únicos, una ubicación, controlado por un departamento
- **EMPLEADO**: nombre, DNI, dirección, sueldo, sexo, fecha de nacimiento
  - Pertenece a un departamento, trabaja en varios proyectos (horas/semana), tiene un supervisor
- **SUBORDINADO**: nombre, sexo, fecha de nacimiento, relación con el empleado

## Entidades y atributos

- **Entidad**: objeto del mundo real con existencia independiente
  - Física (persona, coche) o conceptual (empresa, curso)
- **Atributo**: propiedad que describe a la entidad

### Tipos de atributos

```mermaid
flowchart TD
    A["<b>Atributo</b>"]

    A --> P1["<b>Simple (atómico)</b><br/>vs<br/><b>Compuesto</b>"]
    A --> P2["<b>Monovalor</b><br/>vs<br/><b>Multivalor</b>"]
    A --> P3["<b>Almacenado</b><br/>vs<br/><b>Derivado</b>"]

    P1 --> D1["Compuesto: se divide en subpartes<br/>con significado propio y puede formar<br/>jerarquías<br/><i>Dirección → DirCalle, Ciudad,<br/>Provincia, CP</i>"]
    P2 --> D2["Multivalor: conjunto de valores<br/>para la misma entidad; puede tener<br/>límites superior e inferior<br/><i>Colores, Licenciaturas</i>"]
    P3 --> D3["Derivado: se obtiene de otro atributo<br/>o de entidades relacionadas<br/><i>Edad ← FechaNac;<br/>NumEmpleados ← empleados del dpto.</i>"]

    D1 --> C["<b>Atributos complejos</b><br/>Anidamiento arbitrario de<br/>compuestos y multivalor"]
    D2 --> C

    classDef raiz fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef tipo fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef detalle fill:#fbfcfd,stroke:#c3ccd7,color:#33414f
    class A raiz
    class P1,P2,P3 tipo
    class D1,D2,D3,C detalle
```

---

#### Jerarquía de un atributo compuesto

![Jerarquía del atributo compuesto Dirección: DirCalle (Número, Calle, NumApto), Ciudad, Provincia y CP](../../assets/jerarquia-atributos.png)

- Las hojas son **atributos simples**
- Útil cuando se consulta la dirección completa *o* una parte (`Ciudad`, `CP`)
- Notación: compuesto `()`, multivalor `{}`

```text
{TlfDir( {Tlf(CodÁrea, NumTlf)}, Dir(DirCalle(Número, Calle, NumApto), Ciudad, Provincia, CP) )}
```

#### Entidades y valores

![Dos entidades con los valores de sus atributos: el empleado e1 y la empresa c1](../../assets/dos-entidades.png)

- Cada entidad tiene un **valor** por atributo
- **NULL** cuando:
  - No aplica (`NumApto` en una casa)
  - Existe pero se desconoce (`Altura`)
  - No se sabe si existe (`TlfCasa`)

### Tipo de entidad, clave y dominio

- **Tipo de entidad** = esquema (*intención*); **conjunto de entidades** = instancias (*extensión*)
- **Atributo clave**: valor único por entidad
  - Puede haber varias claves; una clave compuesta debe ser **mínima**
  - Sin clave → **entidad débil**
- **Dominio**: valores permitidos del atributo (no se dibuja en el ER)

### Diseño inicial de EMPRESA

| Tipo de entidad | Atributos | Notas |
| --- | --- | --- |
| `DEPARTAMENTO` | Nombre, Número, Ubicaciones, Director, FechaIngresoDirector | `Ubicaciones` multivalor |
| `PROYECTO` | Nombre, Número, Ubicación, DepartamentoControl | |
| `EMPLEADO` | Nombre (NombreP, Apellido1, Apellido2), Dni, Sexo, Dirección, Sueldo, FechaNac, Departamento, Supervisor, TrabajaEn (Proyecto, Horas) | `TrabajaEn` compuesto multivalor |
| `SUBORDINADO` | Empleado, NombreSubordinado, Sexo, FechaNac, Relación | |

> Los atributos que referencian otra entidad se convertirán en relaciones.

## Relaciones

- Atributo que **referencia otra entidad** → debe ser **relación**
- **Instancia de relación**: *(e₁, e₂, …, eₙ)*, una entidad de cada tipo
- Se dibuja como **rombo**

### Grado, roles y recursividad

- **Grado**: nº de entidades participantes → binaria (2), ternaria (3)
- **Nombre de rol**: papel de cada entidad (*trabajador*, *empleador*)
- **Relación recursiva**: la misma entidad participa dos veces
  - `CONTROL`: EMPLEADO como *supervisor* y *supervisado*

### Restricciones estructurales

- **Razón de cardinalidad** (máximo): 1:1, 1:N, M:N
- **Participación** (mínimo):
  - **Total** (línea doble) = dependencia de existencia
  - **Parcial** (línea sencilla)

| Relación | Razón | Significado |
| --- | --- | --- |
| `ADMINISTRA` | 1:1 | Un director por departamento |
| `TRABAJA_PARA` | 1:N | Un departamento, muchos empleados |
| `TRABAJA_EN` | M:N | Muchos empleados, muchos proyectos |

### Atributos de relación

- Ej.: `Horas` en `TRABAJA_EN`, `FechaInicio` en `ADMINISTRA`
- **1:1** → puede migrar a cualquiera de las dos entidades
- **1:N** → solo al lado **N**
- **M:N** → debe quedarse en la relación

## Entidades débiles

- **Sin clave propia**; se identifican por su **propietario** + **clave parcial**
- **Relación identificativa**: participación **siempre total**
- Ej.: `SUBORDINADO` (clave parcial `Nombre`) ← `EMPLEADO`
- Notación: rectángulo y rombo **dobles**; clave parcial con subrayado **discontinuo**
- Dependencia de existencia ≠ entidad débil (`PERMISO_CONDUCIR` tiene clave propia)

## Refinamiento de EMPRESA

| Relación | Participantes | Razón | Participación | Atributos |
| --- | --- | --- | --- | --- |
| `ADMINISTRA` | EMPLEADO – DEPARTAMENTO | 1:1 | EMP parcial, DEP total | `FechaInicio` |
| `TRABAJA_PARA` | DEPARTAMENTO – EMPLEADO | 1:N | ambas totales | |
| `CONTROLA` | DEPARTAMENTO – PROYECTO | 1:N | PROY total, DEP parcial | |
| `CONTROL` | EMPLEADO – EMPLEADO | 1:N | ambas parciales | |
| `TRABAJA_EN` | EMPLEADO – PROYECTO | M:N | ambas totales | `Horas` |
| `SUBORDINADOS_DE` | EMPLEADO – SUBORDINADO | 1:N | EMP parcial, SUB total | |

- Se eliminan los atributos convertidos en relaciones
- Objetivo: **mínima redundancia**

```mermaid
erDiagram
    DEPARTAMENTO ||--|{ EMPLEADO : "TRABAJA_PARA 1:N"
    EMPLEADO |o--|| DEPARTAMENTO : "ADMINISTRA 1:1 (FechaInicio)"
    DEPARTAMENTO |o--|{ PROYECTO : "CONTROLA 1:N"
    EMPLEADO }o--o{ PROYECTO : "TRABAJA_EN M:N (Horas)"
    EMPLEADO |o--o{ EMPLEADO : "CONTROL 1:N (supervisor/supervisado)"
    EMPLEADO |o--|{ SUBORDINADO : "SUBORDINADOS_DE (identificativa)"

    EMPLEADO {
        string Dni PK
        string Nombre "compuesto: NombreP, Apellido1, Apellido2"
        string Direccion
        string Sexo
        decimal Sueldo
        date FechaNac
    }
    DEPARTAMENTO {
        string Nombre UK
        int Numero PK
        string Ubicaciones "multivalor"
        int NumEmpleados "derivado"
    }
    PROYECTO {
        string Nombre UK
        int Numero PK
        string Ubicacion
    }
    SUBORDINADO {
        string Nombre "clave parcial"
        string Sexo
        date FechaNac
        string Relacion
    }
```

## Notación del diagrama ER

| Símbolo | Significado |
| --- | --- |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="10" y="8" width="80" height="24"/></svg> | Tipo de entidad |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="10" y="6" width="80" height="28"/><rect x="14" y="10" width="72" height="20"/></svg> | Tipo de entidad débil |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="50,4 90,20 50,36 10,20"/></svg> | Tipo de relación |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="50,4 90,20 50,36 10,20"/><polygon points="50,10 78,20 50,30 22,20"/></svg> | Relación identificativa |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="50" cy="20" rx="38" ry="14"/></svg> | Atributo |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="50" cy="20" rx="38" ry="14"/><text x="50" y="24" font-size="11" text-anchor="middle" fill="currentColor" stroke="none" text-decoration="underline">Clave</text></svg> | Atributo clave (subrayado punteado = clave parcial) |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="50" cy="20" rx="40" ry="16"/><ellipse cx="50" cy="20" rx="34" ry="11"/></svg> | Atributo multivalor |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="50" cy="20" rx="38" ry="14" stroke-dasharray="4 3"/></svg> | Atributo derivado |
| <svg width="100" height="60" viewBox="0 0 100 60" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="50" cy="12" rx="24" ry="9"/><ellipse cx="22" cy="48" rx="18" ry="8"/><ellipse cx="78" cy="48" rx="18" ry="8"/><line x1="40" y1="20" x2="26" y2="40"/><line x1="60" y1="20" x2="74" y2="40"/></svg> | Atributo compuesto |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="10" y1="17" x2="90" y2="17"/><line x1="10" y1="23" x2="90" y2="23"/></svg> | Participación total (dependencia de existencia) |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="10" y1="20" x2="90" y2="20"/></svg> | Participación parcial |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="10" y1="26" x2="90" y2="26"/><text x="20" y="18" font-size="11" text-anchor="middle" fill="currentColor" stroke="none">1</text><text x="80" y="18" font-size="11" text-anchor="middle" fill="currentColor" stroke="none">N</text></svg> | Razón de cardinalidad |
| <svg width="100" height="40" viewBox="0 0 100 40" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="10" y1="28" x2="90" y2="28"/><text x="50" y="18" font-size="11" text-anchor="middle" fill="currentColor" stroke="none">(0,N)</text></svg> | Restricción estructural alternativa |

### Convenciones de nombres

- Tipos de entidad en **singular**
- ENTIDADES y RELACIONES en mayúsculas; Atributos con inicial mayúscula; roles en minúsculas
- **Sustantivos** → entidades; **verbos** → relaciones
- Leer de **izquierda a derecha** y de **arriba abajo**

### Opciones de diseño

- Atributo → **relación** (si referencia otra entidad)
- Atributo repetido en varias entidades → **nueva entidad**
- Entidad con un solo atributo → **atributo**

### Notación (mín, máx)

- `mín = 0` → parcial; `mín > 0` → total
- Más precisa que la razón de cardinalidad

| Relación | Participaciones |
| --- | --- |
| `TRABAJA_PARA` | EMPLEADO (1,1), DEPARTAMENTO (4,N) |
| `ADMINISTRA` | EMPLEADO (0,1), DEPARTAMENTO (1,1) |
| `CONTROLA` | DEPARTAMENTO (0,N), PROYECTO (1,1) |
| `TRABAJA_EN` | EMPLEADO (1,N), PROYECTO (1,N) |
| `CONTROL` | supervisor (0,N), supervisado (0,1) |
| `SUBORDINADOS_DE` | EMPLEADO (0,N), SUBORDINADO (1,1) |

## ER vs UML

| Modelo ER | UML |
| --- | --- |
| Tipo de entidad | **Clase** (nombre, atributos, operaciones) |
| Entidad | **Objeto** |
| Atributo multivalor | **Clase separada** |
| Tipo de relación | **Asociación** |
| Instancia de relación | **Vínculo** |
| (mín, máx) | **Multiplicidad** `mín..máx` (en el extremo opuesto) |
| Relación recursiva | **Asociación reflexiva** |
| Entidad débil | **Asociación cualificada** |

## Relaciones de grado > 2

- Una ternaria **≠** tres binarias
  - `SUMINISTRO(s, j, p)` no se deduce de `PUEDE_SUMINISTRAR`, `USA`, `SUMINISTRA`
- Solución típica: ternaria **+** las binarias necesarias
- Alternativas:
  - Entidad débil con **tres relaciones identificativas**
  - Entidad regular con **clave sustituta** (`IdSuministro`)
- Restricciones: usar **ambas** notaciones (razón de cardinalidad y (mín, máx))

## Resumen

- Entidades, atributos, claves, relaciones, restricciones y entidades débiles
- Suficiente para aplicaciones empresariales típicas
- Siguiente paso: **modelo ER mejorado (EER)** → especialización, generalización, herencia

[⬅️ Volver a Unidad I](./index.md)
