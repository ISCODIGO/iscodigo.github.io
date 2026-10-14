---
layout: post
title: "Modelo Entidad-Relación Extendido (EER)"
parent: "Unidad I: Introducción a las Bases de Datos Relacionales y conceptos básicos"
grand_parent: "ISC-321 Fundamentos de Bases de Datos"
nav_order: 4
mermaid: true
---

## ¿Por qué extender el ER?

- Algunas aplicaciones (CAD, telecomunicaciones, mapas) necesitan modelar **más detalles**
- **EER** = el modelo ER **+**:
  - **Subclases y superclases**
  - **Especialización** y **generalización**
  - **Categorías**
  - **Herencia**

## Subclases, superclases y herencia

- **Superclase**: tipo general (`EMPLEADO`)
- **Subclase**: grupo dentro de ese tipo (`SECRETARIA`, `INGENIERO`, `TÉCNICO`)
- Se leen como **ES-UN**: *una SECRETARIA **es un** EMPLEADO*
- Es **la misma persona** vista en otro papel
  - La secretaria ‘Laura Logano’ *es* el empleado ‘Laura Logano’
- Reglas:
  - Todo lo que está en la subclase también está en la superclase
  - Una entidad puede estar en **varias** subclases
  - Una entidad puede **no** estar en ninguna subclase
- **Herencia**: la subclase recibe **todos** los atributos y relaciones de la superclase

| Clase/subclase | Relación 1:1 |
| --- | --- |
| **Una** entidad en otro papel | **Dos** entidades distintas |

## Especialización y generalización

### Especialización

- Dividir un tipo de entidad en **subclases** según una característica
- Se puede dividir de **varias formas**:
  - Por trabajo → {`SECRETARIA`, `INGENIERO`, `TÉCNICO`}
  - Por contrato → {`PERSONAL_FIJO`, `PERSONAL_TEMPORAL`}
- Sirve para:
  - Atributos propios: `Idiomas` solo en `SECRETARIA`
  - Relaciones propias: solo `PERSONAL_TEMPORAL` se relaciona con `SINDICATO`

```mermaid
flowchart TD
    E["<b>EMPLEADO</b><br/>Nombre, Dni, FechaNac, Dirección, TipoTrabajo"]

    E --- D1(("d"))
    D1 --> S["<b>SECRETARIA</b><br/>Idiomas"]
    D1 --> T["<b>TÉCNICO</b><br/>GradoE"]
    D1 --> I["<b>INGENIERO</b><br/>Especialización"]

    E --> DI["<b>DIRECTOR</b>"]

    E === D2(("d"))
    D2 --> PF["<b>PERSONAL_FIJO</b>"]
    D2 --> PT["<b>PERSONAL_TEMPORAL</b>"]
    PT --- PA{"PERTENECE_A"} --- SI["SINDICATO"]

    classDef sup fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef sub fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    class E sup
    class S,T,I,DI,PF,PT sub
```

> Línea doble = especialización **total**. Si hay **una sola** subclase (`DIRECTOR`), no se dibuja el círculo.

### Generalización

- Lo **contrario**: juntar lo común de varias entidades en una superclase
- `COCHE` + `CAMIÓN` → `VEHÍCULO`

| Especialización | Generalización |
| --- | --- |
| De arriba hacia abajo | De abajo hacia arriba |
| Superclase → subclases | Subclases → superclase |

- El resultado puede ser **el mismo**; en la práctica se usan ambas

## Restricciones de la especialización

### ¿Quién entra en cada subclase?

- **Por condición**: se cumple una regla sobre un atributo
  - `SECRETARIA` si `TipoTrabajo = 'Secretaria'`
- **Por atributo**: todas las subclases usan el **mismo** atributo (en UML: *discriminador*)
- **Por usuario**: no hay regla; el usuario decide

### Disyunción y completitud

- **Disjunta** (`d`): la entidad está en **una sola** subclase como máximo
- **Solapada** (`o`): puede estar en **varias**
- **Total** (línea doble): toda entidad está en **al menos una** subclase
- **Parcial** (línea sencilla): puede no estar en ninguna

| | Total | Parcial |
| --- | --- | --- |
| **Disjunta** | {`PERSONAL_FIJO`, `PERSONAL_TEMPORAL`} | {`SECRETARIA`, `INGENIERO`, `TÉCNICO`} |
| **Solapada** | — | {`EMPLEADO`, `EX_ALUMNO`, `ESTUDIANTE`} |

- Son dos restricciones independientes → 4 combinaciones
- La generalización suele ser **total**

### Insertar y borrar

- **Borrar** de la superclase → se borra también de sus subclases
- **Insertar** en la superclase → entra automáticamente en las subclases cuya condición cumpla
- En una especialización **total**, debe entrar en **al menos una** subclase

## Jerarquías y entramados

- **Jerarquía**: cada subclase tiene **un solo padre** (herencia simple)
- **Entramado**: una subclase tiene **varios padres** (herencia múltiple)
  - `INGENIERO_JEFE` es `INGENIERO`, `DIRECTOR` y `PERSONAL_FIJO`
- La subclase hereda de **todos** sus ancestros
- Si un atributo llega por varios caminos, se incluye **una sola vez**

### Ejemplo: UNIVERSIDAD

```mermaid
flowchart TD
    P["<b>PERSONA</b><br/>Nombre, Dni, Sexo, Dirección, FechaNac"]
    P --- O(("o"))
    O --> EM["<b>EMPLEADO</b><br/>Salario"]
    O --> AL["<b>EX_ALUMNO</b><br/>{Licenciatura(Año, Grado, Especialidad)}"]
    O --> ES["<b>ESTUDIANTE</b><br/>DptoEspec"]

    EM === D1(("d"))
    D1 --> AD["<b>ADMINISTRATIVO</b><br/>Posición"]
    D1 --> DO["<b>DOCENTE</b><br/>Rango"]
    D1 --> AJ["<b>ADJUNTO</b><br/>PorcenTiempo"]
    ES --> AJ

    ES --- D2(("d"))
    D2 --> ED["<b>ESTUDIANTE_DIPLOMADO</b><br/>ProgGrado"]
    D2 --> EN["<b>ESTUDIANTE_NO_DIPLOMADO</b><br/>Clase"]

    AJ --- D3(("d"))
    D3 --> AI["<b>ADJUNTO_INVESTIGACIÓN</b><br/>Proyecto"]
    D3 --> AE["<b>ADJUNTO_ENSEÑANZA</b><br/>Curso"]

    classDef sup fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef sub fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef comp fill:#fff4e0,stroke:#c98a1b,stroke-width:2px,color:#1b2b40
    class P sup
    class EM,AL,ES,AD,DO,AI,AE,ED,EN sub
    class AJ comp
```

- `ADJUNTO` tiene dos padres (`EMPLEADO` y `ESTUDIANTE`) → es un **entramado**

## Categorías

- **Categoría**: subclase que viene de **una de varias** superclases distintas
- Ej.: el `PROPIETARIO` de un vehículo puede ser una `PERSONA`, un `BANCO` **o** una `EMPRESA`
- Se dibuja con un círculo con **∪**

```mermaid
flowchart TD
    PE["<b>PERSONA</b><br/>Dni, Nombre, Dirección"] --- U1(("∪"))
    BA["<b>BANCO</b><br/>NombreB, DireccB"] --- U1
    EMP["<b>EMPRESA</b><br/>NombreE, DireccE"] --- U1
    U1 --> PRO["<b>PROPIETARIO</b>"]

    CO["<b>COCHE</b><br/>IdVehic, EstiloC, MarcaC…"] --- U2(("∪"))
    CA["<b>CAMIÓN</b><br/>IdVehic, Tonelaje, MarcaT…"] --- U2
    U2 --> VR["<b>VEHÍCULO_REGISTRADO</b><br/>Matrícula"]

    PRO ---|M| R{"PROPIEDAD<br/>FechaCompra"} ---|N| VR

    classDef sup fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef cat fill:#fff4e0,stroke:#c98a1b,stroke-width:2px,color:#1b2b40
    class PE,BA,EMP,CO,CA sup
    class PRO,VR cat
```

| Herencia múltiple | Categoría |
| --- | --- |
| Está en **todas** sus superclases | Está en **solo una** |
| Hereda de **todas** | Hereda solo de la suya |

## Consejos de diseño

- Demasiadas subclases confunden
- Si una subclase no tiene relaciones propias → mejor un **atributo tipo** en la superclase
  - Ej.: `EMPLEADO` con `TipoTrabajo` y `TipoContrato`
- Usar categorías solo si son **necesarias**
- Si no hay reglas claras → usar **solapada y parcial**

## EER vs UML

| EER | UML |
| --- | --- |
| Círculo de especialización | **Triángulo** hacia la superclase |
| Disjunta `d` | Triángulo **vacío** |
| Solapada `o` | Triángulo **relleno** |
| Atributo de especialización | **Discriminador** |

## Abstracción de datos

| Concepto | En EER | Se lee como |
| --- | --- | --- |
| **Clasificación** | Tipos de entidad | ES-UNA-INSTANCIA-DE |
| **Identificación** | Claves | — |
| **Especialización** | Subclases | ES-UN |
| **Agregación** | Atributos compuestos | ES-UNA-PARTE-DE |
| **Asociación** | Relaciones | ESTÁ-ASOCIADA-CON |

- Al **borrar**:
  - **Asociación** → lo relacionado **sigue existiendo**
  - **Agregación** → borrar `COCHE` borra `MOTOR` y `RUEDAS`

## Resumen

- EER = ER **+** subclases, herencia, especialización/generalización y categorías
- Restricciones: **disjunta/solapada** y **total/parcial**
- Jerarquía = un padre; entramado = varios padres
- Siguiente paso: **pasar el EER a tablas**

[⬅️ Volver a Unidad I](./index.md)
