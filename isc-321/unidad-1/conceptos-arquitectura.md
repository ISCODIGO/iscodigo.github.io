---
layout: post
title: "Conceptos y arquitectura de los sistemas de bases de datos"
parent: "Unidad I: Introducción a las Bases de Datos Relacionales y conceptos básicos"
grand_parent: "ISC-321 Fundamentos de Bases de Datos"
nav_order: 2
mermaid: true
---

## Modelos de datos, esquemas e instancias


```mermaid
flowchart TD
    M["<b>Modelo de datos</b><br/>Conceptos para describir<br/>estructura y operaciones"]

    M --> ALTO["<b>Alto nivel</b><br/>o conceptuales"]
    M --> REP["<b>Representativos</b><br/>o de implementación"]
    M --> BAJO["<b>Bajo nivel</b><br/>o físicos"]

    ALTO --> ALTOD["Entidades, atributos y relaciones<br/><i>Ej.: modelo Entidad-Relación</i>"]
    REP --> REPD["Relacional, de red, jerárquico<br/>y orientado a objetos<br/><i>Los más usados en DBMS comerciales</i>"]
    BAJO --> BAJOD["Formatos de registro, ordenación<br/>y rutas de acceso"]

    classDef raiz fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef nivel fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef detalle fill:#fbfcfd,stroke:#c3ccd7,color:#33414f
    class M raiz
    class ALTO,REP,BAJO nivel
    class ALTOD,REPD,BAJOD detalle
```


**Esquema vs. estado de la base de datos:**

- El **esquema** es la descripción de la base de datos (tipos de registro, restricciones); se especifica en el diseño y no cambia con frecuencia. Un esquema visualizado es un **diagrama de esquema**. El DBMS guarda esta descripción (**metadatos**) en su **catálogo**.
- El **estado** (o *snapshot*) es el conjunto de datos reales en un momento dado; cambia con cada inserción, borrado o actualización. El **estado inicial** es cuando la base de datos se carga por primera vez.
- Un cambio de esquema (p. ej., añadir un campo) es **evolución del esquema**, distinto de una actualización normal de datos.

## Arquitectura de tres esquemas e independencia de los datos

La **arquitectura de tres esquemas** (ANSI/SPARC) separa las aplicaciones de usuario de la base de datos física. Para eso describe la base de datos en tres niveles:

```mermaid
flowchart TD
    U["Usuarios finales y aplicaciones"]

    U --> EXT1["<b>Vista externa 1</b><br/>p. ej. nómina"]
    U --> EXT2["<b>Vista externa 2</b><br/>p. ej. directorio público"]
    U --> EXTN["<b>Vista externa n</b>"]

    EXT1 -->|mapeo externo/conceptual| CONC
    EXT2 -->|mapeo externo/conceptual| CONC
    EXTN -->|mapeo externo/conceptual| CONC

    CONC["<b>Esquema conceptual</b><br/>Toda la base de datos:<br/>entidades, tipos de datos,<br/>relaciones y restricciones<br/>sin detalles físicos"]
    CONC -->|mapeo conceptual/interno| INT["<b>Esquema interno</b><br/>Almacenamiento físico:<br/>archivos, registros,<br/>índices y rutas de acceso"]
    INT --> BD[("Base de datos almacenada")]

    classDef ext fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef conc fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef fis fill:#fdf6e3,stroke:#c9a227,color:#4a3c00
    class U,EXT1,EXT2,EXTN ext
    class CONC conc
    class INT,BD fis
```

- El **nivel externo** tiene un **esquema externo** (o **vista de usuario**) por cada grupo de usuarios. Cada uno muestra solo la parte de la base de datos que le interesa a ese grupo y oculta el resto. Por ejemplo, nómina ve el salario de los empleados; el directorio público solo ve el nombre y el cargo.
- El **nivel conceptual** tiene un único **esquema conceptual**, que describe toda la base de datos para la comunidad de usuarios. Suele expresarse con un modelo de datos representativo (p. ej. el relacional).
- El **nivel interno** tiene el **esquema interno**, que describe cómo se almacenan los datos físicamente.

Los tres esquemas son solo **descripciones**: los datos reales existen únicamente en el nivel físico. El DBMS usa los **mapeos** entre niveles para traducir una consulta hecha sobre una vista externa a una consulta sobre el esquema conceptual y, de ahí, a operaciones sobre el almacenamiento.

**Independencia de los datos:** es la posibilidad de cambiar el esquema de un nivel sin tener que cambiar el esquema del nivel superior. Solo cambia el mapeo entre ambos.

- **Independencia lógica:** se puede cambiar el esquema conceptual (p. ej. agregar un atributo o una tabla) sin modificar los esquemas externos ni los programas que no usan lo que cambió.
- **Independencia física:** se puede cambiar el esquema interno (p. ej. crear un índice o reorganizar archivos) sin modificar el esquema conceptual. Es más fácil de lograr que la independencia lógica y la mayoría de los DBMS la ofrecen.

## Lenguajes e interfaces de bases de datos

```mermaid
flowchart TD
    L["Lenguajes de un DBMS"]

    L --> DDL["<b>DDL</b><br/>data definition language<br/>Define el esquema conceptual<br/>En la mayoría de los DBMS<br/>también define el esquema externo"]
    L --> SDL["<b>SDL</b><br/>storage definition language<br/>Define el esquema interno<br/>(cómo se almacenan los datos)<br/>En los DBMS relacionales actuales<br/>no es un lenguaje aparte: el DBA<br/>usa parámetros de almacenamiento"]
    L --> VDL["<b>VDL</b><br/>view definition language<br/>Define las vistas de usuario<br/>y su correspondencia<br/>con el esquema conceptual<br/>En la práctica lo hace SQL"]
    L --> DML["<b>DML</b><br/>data manipulation language<br/>Recupera, inserta, borra<br/>y modifica datos<br/>Hay dos tipos:"]

    DML --> ALTO["<b>Alto nivel</b><br/>no procedimental · declarativo<br/>Opera sobre conjuntos de registros<br/>(set-at-a-time) — p. ej. SQL<br/>Indica <i>qué</i> datos se quieren,<br/>no <i>cómo</i> obtenerlos"]
    DML --> BAJO["<b>Bajo nivel</b><br/>procedimental<br/>Opera sobre un registro a la vez<br/>(record-at-a-time) — p. ej. DL/1<br/>Recorre los registros con bucles"]

    ALTO --> QUERY["Cuando se usa de forma interactiva<br/>se le llama <b>lenguaje de consulta</b>"]
    BAJO --> HOST["Debe incrustarse en un lenguaje<br/>de programación de propósito<br/>general: el lenguaje <b>host</b>"]

    classDef raiz fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef leng fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef nota fill:#fdf6e3,stroke:#c9a227,color:#4a3c00
    class L raiz
    class DDL,SDL,VDL,DML,ALTO,BAJO leng
    class QUERY,HOST nota
```

## Arquitectura de un DBMS

**Interfaces para el usuario:** basadas en menús, en formularios, GUI, lenguaje natural, entrada/salida por voz, interfaces para usuarios paramétricos (teclas de función) y comandos privilegiados para el DBA.

![Arquitectura de un DBMS](../../assets/arquitectura-dbms.png)

Arquitectura de dos y tres capas: el DBMS puede estar en un solo computador (monolítico) o en varios (cliente/servidor). La arquitectura de tres capas añade una capa intermedia de procesamiento de aplicaciones, que puede estar en el cliente o en el servidor.
![Arquitectura de capas](../../assets/arquitectura-2y3-capas.png)

![Arquitectura de capas 2](../../assets/arquitectura-capas.png)

> **Nota (fuera del libro):** sobre esa base de 2/3 capas, la nube extendió el modelo de servidor de base de datos con nuevas variantes:
> - **DBaaS** (*Database as a Service*): el proveedor cloud administra el ciclo de vida completo del DBMS (aprovisionamiento, parches, backups, escalado); el "servidor" ya no lo opera el DBA local.
> - **Base de datos serverless**: separa cómputo de almacenamiento y escala automáticamente entre cero y el pico de demanda según conexiones/consultas, sin definir de antemano el tamaño del servidor.
> - **Microservicios con persistencia poliglota**: la capa intermedia de aplicación se descompone en servicios independientes, cada uno con su propia base de datos (a veces de un motor distinto — relacional, documental, clave-valor) en vez de una única base de datos compartida por toda la capa de aplicación.
>



## Clasificación de los DBMS

Se clasifican según varios criterios:

```mermaid
flowchart LR
    D["<b>Clasificación<br/>de los DBMS</b>"]

    D --> MD["<b>Modelo de datos</b>"]
    MD --> REL["Relacional"]
    MD --> OO["Orientado a objetos /<br/>objeto-relacional"]
    MD --> HER["Heredados"]
    HER --> RED["<b>Red (CODASYL DBTG)</b><br/>Tipos conjunto: relaciones 1:N<br/>con punteros; DML record-at-a-time<br/>embebido en COBOL"]
    HER --> JER["<b>Jerárquico</b><br/>Estructuras en árbol; DL/1 (IMS)<br/>dominó 1965–1985; aún en banca,<br/>salud y gobierno"]
    HER --> XML["<b>XML</b><br/>Árbol de elementos anidados;<br/>estándar de intercambio en Internet"]
    MD -.-> NOSQL["<b>NoSQL*</b>"]
    NOSQL -.-> KV["<b>Clave-valor</b><br/>(Redis, DynamoDB)"]
    NOSQL -.-> DOC["<b>Documental</b><br/>(MongoDB)"]
    NOSQL -.-> COL["<b>Columnar</b><br/>(Cassandra)"]
    NOSQL -.-> GRA["<b>Grafos</b><br/>(Neo4j)"]
    MD -.-> VEC["<b>Vectoriales*</b><br/>Embeddings y búsqueda por similitud<br/>(Pinecone, Milvus, pgvector)"]

    D --> U["<b>Usuarios</b><br/>Monousuario (típico en PC)<br/>vs. multiusuario"]
    D --> S["<b>Sitios</b><br/>Centralizado: un solo computador<br/>Distribuido (DDBMS): varios sitios en red<br/>Federado: une DBMS autónomos preexistentes"]
    D --> C["<b>Costo</b><br/>Código abierto (MySQL, PostgreSQL)<br/>hasta licencias de millones anuales"]
    D --> P["<b>Rutas de acceso y propósito</b><br/>General vs. especial<br/>(p. ej. OLTP de reservas de aerolíneas)"]
    D -.-> W["<b>Carga de trabajo*</b><br/>OLTP: transaccional, escritura intensiva<br/>OLAP: analítico, lectura sobre históricos<br/>HTAP: ambas en una plataforma"]
    D -.-> DE["<b>Despliegue*</b><br/>On-premises: hardware propio<br/>Cloud/administrado: Aurora, Cloud SQL<br/>Híbrido"]

    classDef raiz fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef nivel fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef detalle fill:#fbfcfd,stroke:#c3ccd7,color:#33414f
    class D raiz
    class MD,HER,NOSQL,U,S,C,P,W,DE nivel
    class REL,OO,RED,JER,XML,KV,DOC,COL,GRA,VEC detalle
```

## Gestión de transacciones

Una **transacción** es un conjunto de operaciones que forma una única unidad lógica de trabajo (p. ej., una transferencia de fondos con cargo en la cuenta *A* y abono en la cuenta *B*). Debe cumplir las propiedades **ACID**:

```mermaid
flowchart TD
    T["<b>Transacción</b><br/>Unidad lógica de trabajo"]
    T --> ACID["<b>Propiedades ACID</b>"]

    ACID --> A["<b>Atomicidad</b><br/>Todo o nada:<br/>se ejecuta completa<br/>o ninguna operación"]
    ACID --> C["<b>Consistencia</b><br/>Lleva la BD de un estado<br/>consistente a otro<br/>consistente"]
    ACID --> I["<b>Aislamiento</b><br/>Transacciones concurrentes<br/>se comportan como<br/>si fueran secuenciales"]
    ACID --> D["<b>Durabilidad</b><br/>Los cambios confirmados<br/>persisten aunque<br/>el sistema falle"]

    classDef raiz fill:#e8eef7,stroke:#4a6fa5,stroke-width:2px,color:#1b2b40
    classDef nivel fill:#f4f6f8,stroke:#8a9bb0,color:#1b2b40
    classDef detalle fill:#fbfcfd,stroke:#c3ccd7,color:#33414f
    class T raiz
    class ACID nivel
    class A,C,I,D detalle
```


Garantizar atomicidad y durabilidad es responsabilidad del **componente de gestión de transacciones**: si una transacción falla, el sistema debe realizar la **recuperación de fallos**, restaurando la base de datos al estado que tenía antes de que ocurriera el fallo.

[⬅️ Volver a Unidad I](./index.md)
