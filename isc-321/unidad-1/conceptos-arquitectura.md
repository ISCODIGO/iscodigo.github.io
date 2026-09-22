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

## Lenguajes e interfaces de bases de datos

**Lenguajes:**

- **DDL** (*data definition language*): define el esquema conceptual (y, en muchos DBMS, también el externo).
- **SDL** (*storage definition language*): define el esquema interno; en los DBMS relacionales actuales no existe como lenguaje separado, se maneja con parámetros de almacenamiento controlados por el DBA.
- **VDL** (*view definition language*): define las vistas externas y sus mapeados; en la práctica, SQL cumple este rol.
- **DML** (*data manipulation language*): recuperación, inserción, borrado y modificación de datos. Puede ser:
  - **Alto nivel / no procedimental / declarativo / set-at-a-time** (p. ej., SQL): especifica *qué* se quiere, no *cómo* obtenerlo. Usado de forma interactiva se llama **lenguaje de consulta**.
  - **Bajo nivel / procedimental / record-at-a-time** (p. ej., DL/1): debe incrustarse en un lenguaje **host** y procesa un registro a la vez con construcciones tipo bucle.

```mermaid
flowchart TD
    L["Lenguajes de un DBMS"]

    L --> DDL["<b>DDL</b><br/>data definition language<br/>Define el esquema conceptual<br/>y, en muchos DBMS, el externo"]
    L --> SDL["<b>SDL</b><br/>storage definition language<br/>Define el esquema interno<br/>En los DBMS relacionales actuales<br/>no existe como lenguaje aparte"]
    L --> VDL["<b>VDL</b><br/>view definition language<br/>Define vistas externas y mapeados<br/>En la práctica lo cubre SQL"]
    L --> DML["<b>DML</b><br/>data manipulation language<br/>Recuperar, insertar,<br/>borrar y modificar datos"]

    DML --> ALTO["<b>Alto nivel</b><br/>no procedimental · declarativo<br/>set-at-a-time — p. ej. SQL<br/>Especifica <i>qué</i>, no <i>cómo</i>"]
    DML --> BAJO["<b>Bajo nivel</b><br/>procedimental<br/>record-at-a-time — p. ej. DL/1<br/>Un registro a la vez, con bucles"]

    ALTO --> QUERY["Usado de forma interactiva<br/>se llama <b>lenguaje de consulta</b>"]
    BAJO --> HOST["Debe incrustarse en<br/>un lenguaje <b>host</b>"]

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

1. **Modelo de datos**: relacional, orientado a objetos, objeto-relacional, jerárquico, de red, y (fuera del libro) **NoSQL** — clave-valor (p. ej. Redis, Amazon DynamoDB), documental (p. ej. MongoDB), columnar (p. ej. Apache Cassandra) y de grafos (p. ej. Neo4j).
2. **Número de usuarios**: monousuario (típico en PC) vs. multiusuario.
3. **Número de sitios**: centralizado (un solo computador) vs. **distribuido (DDBMS)** (datos y software repartidos en varios sitios conectados por red); un **DBMS federado** conecta DBMS autónomos preexistentes con cierta autonomía local.
4. **Costo**: desde código abierto (MySQL, PostgreSQL) hasta licencias de varios millones anuales para sistemas empresariales modulares.
5. **Tipo de rutas de acceso** y **propósito**: general vs. propósito especial (p. ej., sistemas OLTP de alto volumen de transacciones simultáneas, como reservas de aerolíneas).

> **Nota (fuera del libro):** hoy se suelen agregar dos criterios más:
> - **Tipo de carga de trabajo**: **OLTP** (transaccional, escritura intensiva) vs. **OLAP** (analítico, lectura intensiva sobre grandes volúmenes históricos) vs. **HTAP** (*Hybrid Transactional/Analytical Processing*), que intenta soportar ambas cargas en una sola plataforma.
> - **Modelo de despliegue**: on-premises (hardware propio) vs. **cloud-native / administrado** (p. ej. Amazon Aurora, Google Cloud SQL, con escalado y mantenimiento a cargo del proveedor) vs. híbrido.
>

**Modelos de datos heredados** (contexto histórico):

- **Red (CODASYL DBTG)**: registros relacionados mediante *tipos conjunto* (relaciones 1:N con punteros); DML record-at-a-time embebido en COBOL.
- **Jerárquico**: estructuras en árbol; DL/1 (IMS de IBM) dominó el mercado entre 1965 y 1985 y aún se usa en banca, salud y gobierno.
- **XML**: estructura jerárquica (árbol de elementos anidados), estándar para intercambio de datos por Internet; conceptualmente parecido al modelo de objetos.

## Gestión de transacciones

Una **transacción** es un conjunto de operaciones que forma una única unidad lógica de trabajo (p. ej., una transferencia de fondos con cargo en la cuenta *A* y abono en la cuenta *B*). Debe cumplir las propiedades **ACID**:

![Propiedades ACID](../../assets/acid-propiedades.png)


Garantizar atomicidad y durabilidad es responsabilidad del **componente de gestión de transacciones**: si una transacción falla, el sistema debe realizar la **recuperación de fallos**, restaurando la base de datos al estado que tenía antes de que ocurriera el fallo.

[⬅️ Volver a Unidad I](./index.md)
