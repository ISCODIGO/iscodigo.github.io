---
layout: post
title: "SQL: definición de datos y restricciones"
parent: "Unidad II: Álgebra relacional, SQL y Normalización"
grand_parent: "ISC-321 Fundamentos de Bases de Datos"
nav_order: 2
---

## ¿Qué es SQL?

- **SQL** (*Structured Query Language*) es el lenguaje estándar de las bases de datos relacionales comerciales
- Es **declarativo**: se dice *qué* se quiere, no *cómo* obtenerlo (a diferencia del álgebra relacional, que indica una secuencia de operaciones)
- Combina varios sublenguajes en uno solo:
  - **DDL** (*Data Definition Language*): crear, modificar y eliminar esquemas, tablas, dominios y restricciones → `CREATE`, `ALTER`, `DROP`
  - **DML** (*Data Manipulation Language*): consultar y actualizar datos → `SELECT`, `INSERT`, `UPDATE`, `DELETE`
  - Además: vistas, seguridad y autorización, transacciones, triggers
- Esta página cubre la parte **DDL** (secciones 8.1–8.3 del libro)

### Terminología

| Modelo relacional | SQL |
| --- | --- |
| Relación | Tabla |
| Tupla | Fila |
| Atributo | Columna |

### SQL estándar vs. motores reales

- El libro usa **SQL-99 estándar**. Ningún motor lo implementa completo y cada uno tiene su propio **dialecto**
- Se consideran cuatro motores: **SQL Server**, **PostgreSQL**, **Oracle** y **SQLite**
- Las **notas** indican lo que no funciona en alguno de ellos y la alternativa. Si no hay nota, funciona en los cuatro

## Esquema y catálogo

- Un **esquema SQL** agrupa las tablas y demás elementos que pertenecen a la **misma aplicación** de base de datos
  - Tiene un **nombre**, un **identificador de autorización** (el usuario dueño) y **descriptores** de cada elemento
  - Sus **elementos** son: tablas, restricciones, vistas, dominios, autorizaciones…

```sql
CREATE SCHEMA EMPRESA AUTHORIZATION Jperez;
```

- No cualquier usuario puede crear esquemas: el **DBA** debe otorgar ese privilegio
- Un **catálogo** es una colección de esquemas con nombre dentro de un **entorno SQL** (una instalación de un DBMS)
  - Siempre contiene el esquema especial **`INFORMATION_SCHEMA`**, que describe todos los esquemas del catálogo y sus elementos
  - La integridad referencial solo se puede definir entre tablas de esquemas del **mismo catálogo**

> **Nota:**
>
> - **SQL Server**: `CREATE SCHEMA` debe ir sola en su lote (seguida de `GO`)
> - **Oracle**: cada esquema es un usuario; se crea con `CREATE USER`. No tiene `INFORMATION_SCHEMA` (usa el diccionario de datos: `USER_TABLES`, `ALL_TAB_COLUMNS`…)
> - **SQLite**: no tiene esquemas ni `INFORMATION_SCHEMA`. Cada base es un archivo; se usa `ATTACH DATABASE 'empresa.db' AS EMPRESA` y la tabla `sqlite_schema`

## CREATE TABLE

- Crea una nueva relación: nombre, atributos (cada uno con su **tipo de dato** y restricciones como `NOT NULL`) y restricciones de tabla
- Las restricciones de **clave**, **integridad de entidad** e **integridad referencial** se pueden declarar dentro del `CREATE TABLE` o agregarse después con `ALTER TABLE`
- La tabla se puede calificar con el esquema: `CREATE TABLE EMPRESA.EMPLEADO ...`; si no, se usa el esquema del entorno actual

### Esquema EMPRESA en SQL (Figura 8.1)

```sql
CREATE TABLE EMPLEADO (
  Nombre      VARCHAR(15)   NOT NULL,
  Apellido1   VARCHAR(15)   NOT NULL,
  Apellido2   VARCHAR(15),
  Dni         CHAR(9)       NOT NULL,
  FechaNac    DATE,
  Direccion   VARCHAR(30),
  Sexo        CHAR,
  Sueldo      DECIMAL(10,2),
  SuperDni    CHAR(9),
  Dno         INT           NOT NULL,
  PRIMARY KEY (Dni),
  FOREIGN KEY (SuperDni) REFERENCES EMPLEADO(Dni),
  FOREIGN KEY (Dno) REFERENCES DEPARTAMENTO(NumeroDpto)
);

CREATE TABLE DEPARTAMENTO (
  NombreDpto           VARCHAR(15) NOT NULL,
  NumeroDpto           INT         NOT NULL,
  DniDirector          CHAR(9)     NOT NULL,
  FechaIngresoDirector DATE,
  PRIMARY KEY (NumeroDpto),
  UNIQUE (NombreDpto),
  FOREIGN KEY (DniDirector) REFERENCES EMPLEADO(Dni)
);

CREATE TABLE LOCALIZACIONES_DPTO (
  NumeroDpto    INT         NOT NULL,
  UbicacionDpto VARCHAR(15) NOT NULL,
  PRIMARY KEY (NumeroDpto, UbicacionDpto),
  FOREIGN KEY (NumeroDpto) REFERENCES DEPARTAMENTO(NumeroDpto)
);

CREATE TABLE PROYECTO (
  NombreProyecto    VARCHAR(15) NOT NULL,
  NumProyecto       INT         NOT NULL,
  UbicacionProyecto VARCHAR(15),
  NumDptoProyecto   INT         NOT NULL,
  PRIMARY KEY (NumProyecto),
  UNIQUE (NombreProyecto),
  FOREIGN KEY (NumDptoProyecto) REFERENCES DEPARTAMENTO(NumeroDpto)
);

CREATE TABLE TRABAJA_EN (
  DniEmpleado CHAR(9)      NOT NULL,
  NumProy     INT          NOT NULL,
  Horas       DECIMAL(3,1) NOT NULL,
  PRIMARY KEY (DniEmpleado, NumProy),
  FOREIGN KEY (DniEmpleado) REFERENCES EMPLEADO(Dni),
  FOREIGN KEY (NumProy) REFERENCES PROYECTO(NumProyecto)
);

CREATE TABLE SUBORDINADO (
  DniEmpleado     CHAR(9)     NOT NULL,
  NombSubordinado VARCHAR(15) NOT NULL,
  Sexo            CHAR,
  FechaNac        DATE,
  Relacion        VARCHAR(8),
  PRIMARY KEY (DniEmpleado, NombSubordinado),
  FOREIGN KEY (DniEmpleado) REFERENCES EMPLEADO(Dni)
);
```

### Tablas base

- Las tablas creadas con `CREATE TABLE` son **tablas base** (relaciones base): el DBMS las **almacena** físicamente
- Se distinguen de las **relaciones virtuales** (vistas, `CREATE VIEW`), que pueden no corresponder a ningún archivo físico
- En una tabla base, las **columnas** se consideran ordenadas según aparecen en el `CREATE TABLE`, pero las **filas no** tienen orden

### Referencias circulares y tablas aún no creadas

- La Figura 8.1 da error si se ejecuta tal cual: `Dno` de EMPLEADO apunta a DEPARTAMENTO, que **todavía no existe**; y DEPARTAMENTO a su vez apunta a EMPLEADO (ciclo)
- Solución: crear EMPLEADO **sin** la FK de `Dno` y agregarla después de crear DEPARTAMENTO con `ALTER TABLE`:

```sql
ALTER TABLE EMPLEADO
  ADD CONSTRAINT EMPDEPTFK
  FOREIGN KEY (Dno) REFERENCES DEPARTAMENTO(NumeroDpto);
```

> **Nota (SQLite):** la Figura 8.1 se ejecuta tal cual, porque las claves foráneas solo se revisan al modificar datos; además no soporta `ALTER TABLE … ADD CONSTRAINT`. Las claves foráneas están **desactivadas** por defecto y hay que activarlas en cada conexión con `PRAGMA foreign_keys = ON;`

## Tipos de datos

| Categoría | Tipos | Notas |
| --- | --- | --- |
| Numérico entero | `INTEGER` / `INT`, `SMALLINT` | |
| Numérico real | `FLOAT` / `REAL`, `DOUBLE PRECISION` | Coma flotante |
| Numérico decimal | `DECIMAL(i,j)` / `DEC(i,j)` / `NUMERIC(i,j)` | `i` = **precisión** (total de dígitos), `j` = **escala** (dígitos después del punto). Escala por defecto 0 |
| Cadena de caracteres | `CHAR(n)` / `CHARACTER(n)` | Longitud **fija**: se rellena con blancos a la derecha |
| | `VARCHAR(n)` / `CHAR VARYING(n)` | Longitud **variable**, máximo `n` |
| | `CLOB` (*Character Large Object*) | Textos largos (documentos) |
| Cadena de bits | `BIT(n)`, `BIT VARYING(n)` | Literal: `B'10101'` (o hexadecimal `X'…'`) |
| | `BLOB` (*Binary Large Object*) | Binarios grandes (imágenes) |
| Booleano | `BOOLEAN` | `TRUE`, `FALSE` y **`UNKNOWN`** (lógica de tres valores por los `NULL`) |
| Fecha | `DATE` | `AAAA-MM-DD`. Literal: `DATE '2002-09-27'` |
| Hora | `TIME`, `TIME(i)`, `TIME WITH TIME ZONE` | `HH:MM:SS`; `i` = decimales de segundo. Literal: `TIME '09:12:47'` |
| Marca de tiempo | `TIMESTAMP` | Fecha + hora + fracciones de segundo. Literal: `TIMESTAMP '2002-09-27 09:12:47 648302'` |
| Intervalo | `INTERVAL` | Valor relativo para sumar/restar a fechas u horas; `AÑO/MES` o `DÍA/HORA` |

Detalles de las cadenas:

- Los literales van entre **comillas simples** y **distinguen** mayúsculas de minúsculas: `'Pérez'` ≠ `'PÉREZ'`
  - Las **palabras clave** de SQL (`CREATE`, `CHAR`…) **no** distinguen mayúsculas
- Se comparan en orden **lexicográfico** (alfabético): si `cad1` va antes que `cad2`, entonces `cad1 < cad2`
- Los blancos de relleno de `CHAR(n)` normalmente se **ignoran** al comparar
- Concatenación con `||`: `'abc' || 'XYZ'` → `'abcXYZ'`

Las fechas y horas se pueden comparar con `<`: una fecha anterior es **menor** que una posterior.

> **Nota:** tipos y expresiones que no funcionan en todos los motores
>
> | Del libro | No funciona en | Alternativa |
> | --- | --- | --- |
> | `CLOB` | SQL Server, PostgreSQL | `VARCHAR(MAX)`, `TEXT` |
> | `BLOB` | SQL Server, PostgreSQL | `VARBINARY(MAX)`, `BYTEA` |
> | `BIT(n)`, `BIT VARYING(n)` | Todos menos PostgreSQL | SQL Server: `BIT` es un solo 0/1; Oracle: `RAW(n)` |
> | `BOOLEAN` | SQL Server, Oracle (antes de 23ai) | `BIT`, `NUMBER(1)` |
> | `TIME` | Oracle | `DATE` o `TIMESTAMP` |
> | `TIMESTAMP` | SQL Server (ahí es un contador de versión de fila) | `DATETIME2` |
> | `… WITH TIME ZONE` | SQL Server, SQLite | SQL Server: `DATETIMEOFFSET` |
> | `INTERVAL` | SQL Server, SQLite | Funciones de fecha (`DATEADD`, `date()`) |
> | Literal `DATE '2002-09-27'` | SQL Server, SQLite | `'2002-09-27'` |
> | `'abc' \|\| 'XYZ'` | SQL Server | `'abc' + 'XYZ'` o `CONCAT('abc', 'XYZ')` |
> | `'Pérez' ≠ 'PÉREZ'` | SQL Server (por defecto no distingue mayúsculas) | Intercalación `…_CS_…` |
>
> - **Oracle**: `DATE` también guarda la hora
> - **SQLite**: no tiene tipos de fecha (se guardan como texto `'AAAA-MM-DD'`) y **no valida** longitudes ni precisión: un `VARCHAR(15)` acepta 100 caracteres

### Dominios

- En lugar de repetir el tipo en cada atributo, se puede declarar un **dominio** con nombre:

```sql
CREATE DOMAIN TIPO_DNI AS CHAR(9);
```

- Luego se usa `TIPO_DNI` en `Dni`, `SuperDni`, `DniDirector`, `DniEmpleado`…
- Ventajas: si cambia el tipo, se cambia en **un solo lugar**; el esquema es más **legible**
- Un dominio puede tener `DEFAULT` y `CHECK`

> **Nota:** `CREATE DOMAIN` solo existe en **PostgreSQL** (y en Oracle desde 23ai, con otra sintaxis). En SQL Server lo más parecido es `CREATE TYPE TIPO_DNI FROM CHAR(9);`, sin `CHECK` ni `DEFAULT`. SQLite no tiene nada equivalente.

## Restricciones en SQL

### NOT NULL, DEFAULT y CHECK de atributo

- **`NOT NULL`**: el atributo no admite `NULL`
  - Es **implícito** en los atributos de la **clave primaria**
- **`DEFAULT <valor>`**: valor que se usa si una nueva fila no trae uno explícito
  - Sin `DEFAULT`, el valor por defecto es `NULL` (para atributos sin `NOT NULL`)
- **`CHECK`** después del atributo o dominio: restringe los valores permitidos

```sql
NumeroDpto INT NOT NULL CHECK (NumeroDpto > 0 AND NumeroDpto < 21);

CREATE DOMAIN NUM_D AS INTEGER
  CHECK (VALUE > 0 AND VALUE < 21);
```

- Dentro del `CHECK` de un dominio, el valor se nombra con la palabra clave **`VALUE`** (el libro escribe `NUM_D`, que no es válido)

> **Nota (Oracle):** `DEFAULT` debe ir **antes** de `NOT NULL` (`Dno INT DEFAULT 1 NOT NULL`).

### Claves

- **`PRIMARY KEY`**: uno o más atributos que forman la clave primaria
  - Si es de un solo atributo, puede ir junto a él: `NumeroDpto INT PRIMARY KEY`
- **`UNIQUE`**: claves **alternativas** (candidatas secundarias), p. ej. `UNIQUE (NombreDpto)`

### Integridad referencial

- **`FOREIGN KEY (...) REFERENCES T(...)`** declara una clave foránea
- La integridad referencial se puede violar al **insertar** o **eliminar** filas, o al **modificar** una clave primaria o foránea
- Acción por defecto: **rechazar** la operación que provoca la violación
- El diseñador puede indicar otra **acción referencial** con `ON DELETE` u `ON UPDATE`:

| Acción | `ON DELETE` (se borra la fila referenciada) | `ON UPDATE` (cambia la clave referenciada) |
| --- | --- | --- |
| *(ninguna)* | Se rechaza el borrado | Se rechaza la actualización |
| `SET NULL` | La FK de las filas que la referenciaban pasa a `NULL` | Igual: pasa a `NULL` |
| `SET DEFAULT` | La FK pasa a su valor `DEFAULT` | Igual: pasa al `DEFAULT` |
| `CASCADE` | Se **borran** también las filas que la referenciaban | La FK se **actualiza** al nuevo valor de la clave |

- Regla general: `CASCADE` es adecuado para tablas que representan
  - **relaciones** M:N, como TRABAJA_EN
  - **atributos multivalor**, como LOCALIZACIONES_DPTO
  - **entidades débiles**, como SUBORDINADO

> **Nota:**
>
> - **Oracle**: no tiene `ON UPDATE` ni `ON DELETE SET DEFAULT`
> - **SQL Server**: no permite acciones en una FK hacia la misma tabla (`SuperDni`) ni en ciclos de FKs (error *"may cause cycles or multiple cascade paths"*)

### Nombrar restricciones

- Con la palabra clave **`CONSTRAINT nombre`** se le da nombre a una restricción
- Los nombres deben ser **únicos** dentro del esquema
- Es opcional, pero **necesario** si luego se quiere eliminar o reemplazar la restricción con `ALTER TABLE ... DROP CONSTRAINT`

Ejemplo con todo lo anterior (Figura 8.2):

```sql
CREATE TABLE EMPLEADO (
  ...,
  Dno INT DEFAULT 1 NOT NULL,
  CONSTRAINT EMPPK
    PRIMARY KEY (Dni),
  CONSTRAINT SUPERFKEMP
    FOREIGN KEY (SuperDni) REFERENCES EMPLEADO(Dni)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT EMPDEPTFK
    FOREIGN KEY (Dno) REFERENCES DEPARTAMENTO(NumeroDpto)
    ON DELETE SET DEFAULT ON UPDATE CASCADE
);

CREATE TABLE DEPARTAMENTO (
  ...,
  DniDirector CHAR(9) DEFAULT '888665555' NOT NULL,
  ...,
  CONSTRAINT DEPTPK
    PRIMARY KEY (NumeroDpto),
  CONSTRAINT DEPTSK
    UNIQUE (NombreDpto),
  CONSTRAINT DEPTMGRFK
    FOREIGN KEY (DniDirector) REFERENCES EMPLEADO(Dni)
    ON DELETE SET DEFAULT ON UPDATE CASCADE
);

CREATE TABLE LOCALIZACIONES_DPTO (
  ...,
  PRIMARY KEY (NumeroDpto, UbicacionDpto),
  FOREIGN KEY (NumeroDpto) REFERENCES DEPARTAMENTO(NumeroDpto)
    ON DELETE CASCADE ON UPDATE CASCADE
);
```

Lectura de `SUPERFKEMP`:

- Si se **elimina** un supervisor → el `SuperDni` de sus supervisados pasa a `NULL`
- Si se **corrige** el `Dni` de un supervisor → el nuevo valor se propaga en **cascada** al `SuperDni` de sus supervisados

> **Nota:** la Figura 8.2 no funciona tal cual en **SQL Server** (`SUPERFKEMP` y el ciclo EMPLEADO ↔ DEPARTAMENTO deben quedar sin acciones) ni en **Oracle** (quitar los `ON UPDATE` y los `SET DEFAULT`).

### CHECK sobre tuplas

- Un `CHECK` al **final** del `CREATE TABLE` puede involucrar **varios atributos** de la misma fila
- Se evalúa **fila por fila**, cada vez que se inserta o modifica una tupla
- Ej.: si DEPARTAMENTO tuviera `FechaCreacionDpto`, el director no puede haber ingresado antes de que existiera el departamento:

```sql
CHECK (FechaCreacionDpto <= FechaIngresoDirector)
```

- Para restricciones que abarcan **varias filas o tablas** el estándar tiene `CREATE ASSERTION` (sección 8.7)

> **Nota:** `CREATE ASSERTION` no existe en **ninguno** de los cuatro motores; en la práctica se usan triggers.

## Cambiar el esquema: DROP y ALTER

Los comandos de **evolución del esquema** permiten agregar o quitar tablas, atributos, restricciones y otros elementos sin recrear todo.

### DROP

- Elimina elementos con nombre: esquemas, tablas, dominios, restricciones
- Dos comportamientos:
  - **`CASCADE`**: elimina el elemento **y todo lo que depende de él**
  - **`RESTRICT`**: solo lo elimina si **nada** depende de él; si no, el comando falla

```sql
DROP SCHEMA EMPRESA CASCADE;    -- el esquema y todas sus tablas, dominios, etc.
DROP TABLE SUBORDINADO CASCADE; -- la tabla y las FK / vistas que la referencian
```

| | `DROP SCHEMA` | `DROP TABLE` |
| --- | --- | --- |
| `RESTRICT` | Solo si el esquema está **vacío** | Solo si **ninguna** restricción (FK) ni vista la referencia |
| `CASCADE` | Borra todos sus elementos | Borra también esas restricciones y vistas |

`DROP TABLE` vs `DELETE`:

- `DROP TABLE` elimina los datos **y la definición** de la tabla del catálogo
- `DELETE` (sección 8.6) elimina **solo las filas**; la tabla sigue existiendo

> **Nota:** `CASCADE` y `RESTRICT` solo existen en **PostgreSQL**. En los demás se escribe `DROP TABLE SUBORDINADO;` sin opción, y falla si una FK la referencia (Oracle permite `CASCADE CONSTRAINTS`). Para `DROP SCHEMA`: en SQL Server el esquema debe estar vacío, en Oracle se usa `DROP USER EMPRESA CASCADE` y en SQLite `DETACH DATABASE EMPRESA`.

### ALTER

Cambia la definición de una tabla base u otro elemento del esquema.

**Agregar una columna**

```sql
ALTER TABLE EMPRESA.EMPLEADO ADD COLUMN Trabajo VARCHAR(12);
```

- Las filas existentes quedan con `NULL` en la nueva columna (o con su `DEFAULT`, si se declara)
- Por eso **no** se permite `NOT NULL` sin `DEFAULT` al agregar una columna
- Los valores se cargan después con `UPDATE`

> **Nota:** **SQL Server** y **Oracle** no aceptan la palabra `COLUMN`: `ALTER TABLE EMPLEADO ADD Trabajo VARCHAR(12);`

**Eliminar una columna** (hay que elegir `CASCADE` o `RESTRICT`)

```sql
ALTER TABLE EMPRESA.EMPLEADO DROP COLUMN Direccion CASCADE;
```

- `CASCADE`: borra también las vistas y restricciones que usan la columna
- `RESTRICT`: falla si algo la referencia

> **Nota:** `CASCADE` / `RESTRICT` solo existen en **PostgreSQL**; en los demás se omiten (`DROP COLUMN Direccion;`). **SQLite** no permite eliminar columnas que formen parte de una clave, `UNIQUE`, índice o FK.

**Cambiar el valor por defecto**

```sql
ALTER TABLE EMPRESA.DEPARTAMENTO ALTER COLUMN DniDirector DROP DEFAULT;
ALTER TABLE EMPRESA.DEPARTAMENTO ALTER COLUMN DniDirector SET DEFAULT '333445555';
```

> **Nota:** esta forma solo funciona en **PostgreSQL**.
>
> ```sql
> -- SQL Server: el DEFAULT es una restricción con nombre
> ALTER TABLE DEPARTAMENTO DROP CONSTRAINT DF_DniDirector;
> ALTER TABLE DEPARTAMENTO ADD CONSTRAINT DF_DniDirector DEFAULT '333445555' FOR DniDirector;
>
> -- Oracle
> ALTER TABLE DEPARTAMENTO MODIFY (DniDirector DEFAULT NULL);
> ALTER TABLE DEPARTAMENTO MODIFY (DniDirector DEFAULT '333445555');
>
> -- SQLite: no se puede; hay que recrear la tabla
> ```

**Quitar y agregar restricciones** (para quitarla, debe tener **nombre**)

```sql
ALTER TABLE EMPRESA.EMPLEADO DROP CONSTRAINT SUPERFKEMP CASCADE;
```

- Después se puede agregar una restricción nueva con `ALTER TABLE ... ADD CONSTRAINT ...` (con o sin nombre)

> **Nota:** `CASCADE` no existe en **SQL Server**. **SQLite** no permite agregar ni quitar restricciones: hay que crear una tabla nueva, copiar los datos y renombrarla.

## Resumen de comandos DDL

| Comando | Uso |
| --- | --- |
| `CREATE SCHEMA` | Crear un esquema con su dueño |
| `CREATE TABLE` | Crear una tabla base con columnas y restricciones |
| `CREATE DOMAIN` | Definir un tipo con nombre (con `DEFAULT` / `CHECK` opcionales) |
| `DROP SCHEMA / TABLE / DOMAIN` | Eliminar el elemento (`CASCADE` o `RESTRICT`) |
| `ALTER TABLE ... ADD COLUMN` | Agregar una columna |
| `ALTER TABLE ... DROP COLUMN` | Quitar una columna (`CASCADE` o `RESTRICT`) |
| `ALTER TABLE ... ALTER COLUMN ... SET/DROP DEFAULT` | Cambiar el valor por defecto |
| `ALTER TABLE ... ADD / DROP CONSTRAINT` | Agregar o quitar una restricción |

[⬅️ Volver a Unidad II](./index.md)
