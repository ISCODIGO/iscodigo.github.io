---
layout: post
title: "SQL: consultas y manipulación de datos"
parent: "Unidad II: Álgebra relacional, SQL y Normalización"
grand_parent: "ISC-321 Fundamentos de Bases de Datos"
nav_order: 3
---

## ¿Qué es el DML?

- El **DML** (*Data Manipulation Language*) es la parte de SQL que **consulta** y **modifica** los datos (no la estructura)
  - Consultar → `SELECT`
  - Modificar → `INSERT`, `UPDATE`, `DELETE`
- Esta página resume las secciones **8.4–8.6** del libro (Elmasri & Navathe) y lo complementa con `CASE`, `LIMIT`/`OFFSET` y funciones, que el libro no cubre
- Todos los ejemplos usan el esquema **EMPRESA** de la [página de DDL](./sql-ddl.md)
- Igual que en la página de DDL, las **notas** indican diferencias entre **SQL Server**, **PostgreSQL**, **Oracle** y **SQLite**

## Estructura SELECT-FROM-WHERE

```sql
SELECT <lista de atributos>
FROM   <lista de tablas>
WHERE  <condición>;
```

- `SELECT`: columnas a recuperar → equivale a la **proyección** (π) del álgebra relacional
- `FROM`: tablas necesarias para la consulta
- `WHERE` (opcional): condición booleana que deben cumplir las filas → equivale a la **selección** (σ)
- Diferencia con el álgebra: SQL **no elimina duplicados**; una tabla SQL es un **multiconjunto** (bolsa) de filas

**C0.** Fecha de nacimiento y dirección de José Pérez Pérez

```sql
SELECT FechaNac, Dirección
FROM   EMPLEADO
WHERE  Nombre = 'José' AND Apellido1 = 'Pérez' AND Apellido2 = 'Pérez';
```

**C1.** Nombre y dirección de los empleados del departamento 'Investigación' (selección + concatenación)

```sql
SELECT Nombre, Apellido1, Dirección
FROM   EMPLEADO, DEPARTAMENTO
WHERE  NombreDpto = 'Investigación' AND NúmeroDpto = Dno;
```

- `NombreDpto = 'Investigación'` es una **condición de selección**
- `NúmeroDpto = Dno` es una **condición de concatenación** (*join*)
- Si se omite la condición de concatenación se obtiene el **producto cartesiano** de las tablas: resultados incorrectos y enormes

### Alias, asterisco y DISTINCT

```sql
-- Alias de tabla (variables de tupla): empleado y su supervisor
SELECT E.Nombre, E.Apellido1, S.Nombre AS NombreSup, S.Apellido1 AS ApellidoSup
FROM   EMPLEADO AS E, EMPLEADO AS S
WHERE  E.SuperDni = S.Dni;

-- * = todas las columnas
SELECT * FROM EMPLEADO WHERE Dno = 5;

-- DISTINCT elimina filas duplicadas (ALL es el valor por defecto)
SELECT DISTINCT Sueldo FROM EMPLEADO;
```

- Si dos tablas tienen columnas con el mismo nombre, se **califican**: `EMPLEADO.Dno`
- `AS` también renombra columnas del resultado (`S.Nombre AS NombreSup`)

> **Nota:** **Oracle** no acepta `AS` en alias de **tabla**: se escribe `FROM EMPLEADO E, EMPLEADO S`. Sin `AS` funciona en los cuatro motores.

## Operadores lógicos y de comparación

| Operador | Significado |
| --- | --- |
| `=`, `<>` | Igual, distinto (`!=` también funciona en los cuatro motores, pero no es estándar) |
| `<`, `<=`, `>`, `>=` | Menor, menor o igual, mayor, mayor o igual |
| `AND` | Verdadero si **ambas** condiciones son verdaderas |
| `OR` | Verdadero si **al menos una** es verdadera |
| `NOT` | Niega la condición |
| `BETWEEN a AND b` | Rango **inclusivo**: equivale a `>= a AND <= b` |

- Precedencia: `NOT` → `AND` → `OR`. Usar **paréntesis** para evitar sorpresas

```sql
-- Empleados del departamento 5 que ganan entre 30 000 y 40 000
SELECT *
FROM   EMPLEADO
WHERE  (Sueldo BETWEEN 30000 AND 40000) AND Dno = 5;

-- Sin paréntesis, AND se evalúa primero: devuelve TODAS las mujeres
-- y solo los hombres del departamento 5
SELECT * FROM EMPLEADO WHERE Sexo = 'M' OR Sexo = 'H' AND Dno = 5;

-- Con paréntesis: hombres y mujeres, solo del departamento 5
SELECT * FROM EMPLEADO WHERE (Sexo = 'M' OR Sexo = 'H') AND Dno = 5;

-- Empleados que NO son del departamento 5
SELECT * FROM EMPLEADO WHERE NOT Dno = 5;
```

## Patrones de búsqueda: LIKE

- `LIKE` compara una cadena con un **patrón**. Dos comodines:
  - `%` → cualquier cantidad de caracteres (cero o más)
  - `_` → **exactamente un** carácter

| Patrón | Coincide con |
| --- | --- |
| `'P%'` | Empieza con P |
| `'%ez'` | Termina en "ez" |
| `'%Madrid%'` | Contiene "Madrid" |
| `'_a%'` | La segunda letra es "a" |
| `'___'` | Exactamente tres caracteres |

```sql
-- C12. Empleados cuya dirección está en Madrid
SELECT Nombre, Apellido1
FROM   EMPLEADO
WHERE  Dirección LIKE '%Madrid%';

-- Empleados cuyo apellido NO empieza con P
SELECT Nombre, Apellido1
FROM   EMPLEADO
WHERE  Apellido1 NOT LIKE 'P%';
```

- Para buscar un `%` o `_` literal se usa un **carácter de escape** declarado con `ESCAPE`:

```sql
-- Coincide con la cadena literal 'AB_CD%EF'
WHERE Código LIKE 'AB\_CD\%EF' ESCAPE '\'
```

- Un apóstrofe dentro de una cadena se escribe **doble**: `'O''Brien'`

> **Nota:**
>
> - **Mayúsculas/minúsculas**: en **PostgreSQL** y **Oracle** `LIKE` las distingue (`'p%'` no encuentra "Pérez"); PostgreSQL ofrece `ILIKE` para ignorarlas. En **SQL Server** y **SQLite** depende de la intercalación (*collation*), y por defecto **no** las distingue
> - **SQL Server** además acepta `[abc]` y `[^abc]` dentro del patrón (un carácter del conjunto / fuera del conjunto)
> - El libro usa `FechaNac LIKE '________5_'` para buscar nacidos en los 50: solo funciona si la fecha se guarda como texto. Con un tipo `DATE` real se usa `BETWEEN '1950-01-01' AND '1959-12-31'` o una función de fecha (ver abajo)

## Ordenamiento y limitación de resultados

### ORDER BY

- Ordena el resultado por una o más columnas. Por defecto **ascendente** (`ASC`); `DESC` para descendente
- Va **al final** de la consulta (después de `WHERE`)

```sql
-- C15. Empleados y sus proyectos, ordenados por departamento,
-- y dentro de cada departamento por apellido y nombre
SELECT   NombreDpto, Apellido1, Nombre, NombreProyecto
FROM     DEPARTAMENTO, EMPLEADO, TRABAJA_EN, PROYECTO
WHERE    NúmeroDpto = Dno AND Dni = DniEmpleado AND NumProy = NumProyecto
ORDER BY NombreDpto DESC, Apellido1 ASC, Nombre ASC;
```

- Se puede ordenar por un **alias** o una **expresión**: `ORDER BY Sueldo * 1.1 DESC`
- Sin `ORDER BY`, el orden de las filas **no está garantizado**

> **Nota:** ¿Dónde quedan los `NULL`? En **PostgreSQL** y **Oracle** van **al final** en `ASC`; en **SQL Server** y **SQLite** van **al principio**. PostgreSQL, Oracle y SQLite (≥ 3.30) aceptan `NULLS FIRST` / `NULLS LAST`; SQL Server no.

### LIMIT y OFFSET

- Limitan **cuántas** filas devuelve la consulta y **desde cuál** empezar (paginación). No están en SQL-99; cada motor tiene su sintaxis
- Siempre deben ir con `ORDER BY`; si no, "los 3 primeros" son 3 filas cualesquiera

```sql
-- Los 3 empleados con mayor sueldo (PostgreSQL, SQLite)
SELECT   Nombre, Apellido1, Sueldo
FROM     EMPLEADO
ORDER BY Sueldo DESC
LIMIT 3;

-- Página 2 de 3 en 3: salta 3 filas y toma las siguientes 3
SELECT   Nombre, Apellido1, Sueldo
FROM     EMPLEADO
ORDER BY Sueldo DESC
LIMIT 3 OFFSET 3;
```

- El estándar SQL:2008 define `OFFSET ... FETCH`:

```sql
SELECT   Nombre, Apellido1, Sueldo
FROM     EMPLEADO
ORDER BY Sueldo DESC
OFFSET 3 ROWS FETCH NEXT 3 ROWS ONLY;
```

| Motor | Primeras *n* filas | Paginación |
| --- | --- | --- |
| PostgreSQL | `LIMIT n` o `FETCH FIRST n ROWS ONLY` | `LIMIT n OFFSET m` u `OFFSET m ROWS FETCH NEXT n ROWS ONLY` |
| SQLite | `LIMIT n` | `LIMIT n OFFSET m` |
| SQL Server | `SELECT TOP n ...` | `OFFSET m ROWS FETCH NEXT n ROWS ONLY` (requiere `ORDER BY`) |
| Oracle (≥ 12c) | `FETCH FIRST n ROWS ONLY` | `OFFSET m ROWS FETCH NEXT n ROWS ONLY` |

## Operadores aritméticos y funciones

### Aritmética y renombrado

- `+`, `-`, `*`, `/` sobre columnas numéricas; el resultado se renombra con `AS`

```sql
-- C13. Sueldo aumentado un 10% de quienes trabajan en 'ProductoX'
SELECT Nombre, Apellido1, 1.1 * Sueldo AS SueldoAumentado
FROM   EMPLEADO, TRABAJA_EN, PROYECTO
WHERE  Dni = DniEmpleado AND NumProy = NumProyecto
  AND  NombreProyecto = 'ProductoX';
```

> **Nota:** la división entre **enteros** trunca en **SQL Server**, **PostgreSQL** y **SQLite** (`7 / 2 = 3`); en **Oracle** da `3.5`. Para forzar decimales: `7 * 1.0 / 2`.

### Funciones de cadena

| Operación | Estándar | Diferencias |
| --- | --- | --- |
| Concatenar | `a \|\| b` | **SQL Server**: `a + b` o `CONCAT(a, b)` |
| Longitud | `CHAR_LENGTH(s)` | `LENGTH(s)` en PostgreSQL, Oracle, SQLite; `LEN(s)` en SQL Server |
| Mayúsculas / minúsculas | `UPPER(s)`, `LOWER(s)` | Iguales en los cuatro |
| Subcadena | `SUBSTRING(s FROM i FOR n)` | `SUBSTRING(s, i, n)` en SQL Server y PostgreSQL; `SUBSTR(s, i, n)` en Oracle, SQLite y PostgreSQL |
| Quitar espacios | `TRIM(s)` | Igual en los cuatro (SQL Server ≥ 2017) |
| Reemplazar | — | `REPLACE(s, buscar, reemplazo)` en los cuatro |

- Las posiciones empiezan en **1**, no en 0

```sql
-- Nombre completo en mayúsculas e iniciales
SELECT UPPER(Nombre || ' ' || Apellido1) AS NombreCompleto,
       SUBSTR(Nombre, 1, 1) || SUBSTR(Apellido1, 1, 1) AS Iniciales
FROM   EMPLEADO;

-- Búsqueda sin importar mayúsculas (funciona en cualquier motor)
SELECT * FROM EMPLEADO WHERE LOWER(Apellido1) LIKE 'p%';
```

### Funciones numéricas

| Función | Resultado |
| --- | --- |
| `ABS(x)` | Valor absoluto |
| `ROUND(x, d)` | Redondea a `d` decimales |
| `CEIL(x)` / `FLOOR(x)` | Entero superior / inferior (SQL Server: `CEILING`) |
| `MOD(a, b)` | Residuo (SQL Server y SQLite: `a % b`) |
| `POWER(x, y)`, `SQRT(x)` | Potencia, raíz cuadrada |

```sql
-- Sueldo mensual redondeado a 2 decimales
SELECT Nombre, Apellido1, ROUND(Sueldo / 12, 2) AS SueldoMensual
FROM   EMPLEADO;
```

> **Nota:** en **SQLite**, `CEIL`, `FLOOR`, `POWER`, `SQRT` y `MOD` solo existen desde la versión 3.35 (y si se compiló con funciones matemáticas).

### Funciones de fecha

- SQL permite **sumar o restar intervalos** a una fecha, y la **diferencia** de dos fechas es un intervalo
- La fecha actual en el estándar es `CURRENT_DATE`; para extraer partes, `EXTRACT(YEAR FROM fecha)`

| Operación | PostgreSQL | Oracle | SQL Server | SQLite |
| --- | --- | --- | --- | --- |
| Fecha actual | `CURRENT_DATE` | `CURRENT_DATE` / `SYSDATE` | `CAST(GETDATE() AS DATE)` | `DATE('now')` |
| Año | `EXTRACT(YEAR FROM f)` | `EXTRACT(YEAR FROM f)` | `YEAR(f)` | `STRFTIME('%Y', f)` |
| Sumar 30 días | `f + INTERVAL '30 days'` | `f + 30` | `DATEADD(day, 30, f)` | `DATE(f, '+30 days')` |
| Días entre fechas | `f2 - f1` | `f2 - f1` | `DATEDIFF(day, f1, f2)` | `JULIANDAY(f2) - JULIANDAY(f1)` |

```sql
-- Empleados nacidos en la década de 1950 (PostgreSQL / Oracle)
SELECT Nombre, Apellido1, FechaNac
FROM   EMPLEADO
WHERE  EXTRACT(YEAR FROM FechaNac) BETWEEN 1950 AND 1959;

-- Alternativa que funciona en los cuatro motores
SELECT Nombre, Apellido1, FechaNac
FROM   EMPLEADO
WHERE  FechaNac BETWEEN '1950-01-01' AND '1959-12-31';
```

> **Nota:** **SQLite** no tiene tipo `DATE`: guarda las fechas como texto `'AAAA-MM-DD'`. Por eso comparar con `BETWEEN` funciona, pero solo si todas las fechas siguen ese formato. En **Oracle** el literal debe escribirse `DATE '1950-01-01'`.

## Valores NULL y lógica de tres valores

- `NULL` representa la **ausencia** de valor. Puede significar:
  1. **Desconocido**: existe pero no se conoce (fecha de nacimiento olvidada)
  2. **No disponible**: existe pero no se quiere mostrar (teléfono privado)
  3. **No aplicable**: el atributo no tiene sentido para esa fila (título universitario de alguien sin carrera)
- SQL **no distingue** entre estos significados; cada `NULL` se considera distinto de cualquier otro
- Cualquier comparación con `NULL` da **`UNKNOWN`** (desconocido), no `TRUE` ni `FALSE` → SQL usa **lógica de tres valores**

| AND | TRUE | FALSE | UNKNOWN |
| --- | --- | --- | --- |
| **TRUE** | TRUE | FALSE | UNKNOWN |
| **FALSE** | FALSE | FALSE | FALSE |
| **UNKNOWN** | UNKNOWN | FALSE | UNKNOWN |

| OR | TRUE | FALSE | UNKNOWN |
| --- | --- | --- | --- |
| **TRUE** | TRUE | TRUE | TRUE |
| **FALSE** | TRUE | FALSE | UNKNOWN |
| **UNKNOWN** | TRUE | UNKNOWN | UNKNOWN |

| NOT | |
| --- | --- |
| **TRUE** | FALSE |
| **FALSE** | TRUE |
| **UNKNOWN** | UNKNOWN |

- `WHERE` solo devuelve las filas donde la condición es **`TRUE`**; las `FALSE` y `UNKNOWN` se descartan
- Por eso **nunca** se compara con `= NULL`; se usa `IS NULL` / `IS NOT NULL`

```sql
-- C18. Empleados sin supervisor
SELECT Nombre, Apellido1
FROM   EMPLEADO
WHERE  SuperDni IS NULL;

-- ERROR lógico: devuelve 0 filas siempre (SuperDni = NULL es UNKNOWN)
SELECT Nombre, Apellido1 FROM EMPLEADO WHERE SuperDni = NULL;
```

- `COALESCE(a, b, ...)` devuelve el **primer valor no nulo**; útil para mostrar un valor por defecto

```sql
SELECT Nombre, COALESCE(Dirección, 'Sin dirección') AS Dirección
FROM   EMPLEADO;
```

> **Nota:** en **Oracle** la cadena vacía `''` **es** `NULL`: `WHERE Apellido2 = ''` nunca devuelve filas; hay que usar `IS NULL`. En los otros tres motores `''` y `NULL` son distintos.

## Operador IN

- `v IN (lista)` es verdadero si `v` es **igual a algún** elemento de la lista. Equivale a varios `OR`

```sql
-- C17. Empleados que trabajan en los proyectos 1, 2 o 3
SELECT DISTINCT DniEmpleado
FROM   TRABAJA_EN
WHERE  NumProy IN (1, 2, 3);

-- Equivale a
WHERE  NumProy = 1 OR NumProy = 2 OR NumProy = 3;
```

- La lista también puede ser una **consulta anidada** (subconsulta) que devuelva una columna:

```sql
-- Proyectos en los que trabaja algún empleado de apellido 'Pérez'
SELECT DISTINCT NumProy
FROM   TRABAJA_EN
WHERE  DniEmpleado IN (SELECT Dni
                       FROM   EMPLEADO
                       WHERE  Apellido1 = 'Pérez');
```

- Cuidado con `NOT IN` y `NULL`: si la lista contiene un `NULL`, `v NOT IN (...)` nunca es `TRUE` y la consulta no devuelve filas

```sql
-- Devuelve 0 filas si algún empleado tiene SuperDni NULL
SELECT * FROM EMPLEADO
WHERE  Dni NOT IN (SELECT SuperDni FROM EMPLEADO);

-- Correcto: excluir los NULL de la subconsulta
SELECT * FROM EMPLEADO
WHERE  Dni NOT IN (SELECT SuperDni FROM EMPLEADO WHERE SuperDni IS NOT NULL);
```

## Expresiones CASE

- `CASE` es el **if/else** de SQL: devuelve un valor según condiciones. Se puede usar en `SELECT`, `WHERE`, `ORDER BY` y en `UPDATE`
- Las condiciones se evalúan **en orden**; gana la primera verdadera. Si ninguna se cumple y no hay `ELSE`, el resultado es `NULL`

**CASE buscado** (cada rama con su condición):

```sql
SELECT Nombre, Apellido1, Sueldo,
       CASE
         WHEN Sueldo >= 40000 THEN 'Alto'
         WHEN Sueldo >= 30000 THEN 'Medio'
         ELSE 'Bajo'
       END AS Rango
FROM   EMPLEADO;
```

**CASE simple** (compara una expresión con valores):

```sql
SELECT Nombre, Apellido1,
       CASE Sexo
         WHEN 'H' THEN 'Hombre'
         WHEN 'M' THEN 'Mujer'
         ELSE 'No indicado'
       END AS Sexo
FROM   EMPLEADO;
```

- Combinado con `NULL`:

```sql
SELECT Nombre, Apellido1,
       CASE WHEN SuperDni IS NULL THEN 'Director general' ELSE 'Empleado' END AS Cargo
FROM   EMPLEADO;
```

## Modificar datos: INSERT, UPDATE, DELETE

### INSERT

- Agrega **filas** a una tabla. Los valores van en el **mismo orden** que las columnas del `CREATE TABLE`

```sql
-- U1. Fila completa
INSERT INTO EMPLEADO
VALUES ('Ricardo', 'Roca', 'Flores', '653298653', '1962-12-30',
        'Los Jarales, 47', 'H', 37000, '653298653', 4);
```

- Es mejor **nombrar las columnas**: las omitidas toman su `DEFAULT` o `NULL`. Las `NOT NULL` sin `DEFAULT` son obligatorias

```sql
-- U1A. Solo algunas columnas
INSERT INTO EMPLEADO (Nombre, Apellido1, Dno, Dni)
VALUES ('Ricardo', 'Roca', 4, '653298653');

-- Varias filas en una sola sentencia
INSERT INTO TRABAJA_EN (DniEmpleado, NumProy, Horas)
VALUES ('653298653', 1, 10.0),
       ('653298653', 2, 15.5);
```

- El DBMS **rechaza** el `INSERT` si viola una restricción:

```sql
-- U2. Rechazado si no existe el departamento 2 (integridad referencial)
INSERT INTO EMPLEADO (Nombre, Apellido1, Dni, Dno)
VALUES ('Casimiro', 'García', '980760540', 2);

-- U2A. Rechazado: falta Dni, que es NOT NULL
INSERT INTO EMPLEADO (Nombre, Apellido1, Dno)
VALUES ('Casimiro', 'García', 5);
```

- **INSERT ... SELECT**: carga en una tabla el resultado de una consulta

```sql
-- U3A + U3B. Tabla resumen por departamento
CREATE TABLE INFO_DEPTS (
  NombreDeDpto   VARCHAR(15),
  NumDeEmpleados INTEGER,
  TotalSueldos   INTEGER
);

INSERT INTO INFO_DEPTS (NombreDeDpto, NumDeEmpleados, TotalSueldos)
SELECT   NombreDpto, COUNT(*), SUM(Sueldo)
FROM     DEPARTAMENTO JOIN EMPLEADO ON NúmeroDpto = Dno
GROUP BY NombreDpto;
```

- `INFO_DEPTS` es una **copia**: si luego cambia `EMPLEADO`, queda desactualizada (para eso existen las **vistas**)

> **Nota:**
>
> - **Oracle** no acepta varias filas en un solo `VALUES` (antes de 23c): se repite el `INSERT` o se usa `INSERT ALL ... SELECT * FROM DUAL`
> - Las fechas como `'1962-12-30'` se convierten solas en PostgreSQL, SQL Server y SQLite; en **Oracle** se escribe `DATE '1962-12-30'`
> - **SQLite** no verifica claves foráneas a menos que se active `PRAGMA foreign_keys = ON;`

### UPDATE

- Modifica columnas de las filas que cumplen el `WHERE`. `SET` indica las columnas y sus nuevos valores

```sql
-- U5. Cambiar ubicación y departamento del proyecto 10
UPDATE PROYECTO
SET    UbicaciónProyecto = 'Valencia', NumDptoProyecto = 5
WHERE  NumProyecto = 10;

-- U6. Subir 10% a los empleados de 'Investigación'
UPDATE EMPLEADO
SET    Sueldo = Sueldo * 1.1
WHERE  Dno IN (SELECT NúmeroDpto
               FROM   DEPARTAMENTO
               WHERE  NombreDpto = 'Investigación');
```

- En `Sueldo = Sueldo * 1.1`, el `Sueldo` de la derecha es el valor **anterior** y el de la izquierda el **nuevo**
- Se puede asignar `NULL` o `DEFAULT`. Un `UPDATE` modifica **una sola tabla**
- Si se cambia una clave primaria, el cambio se propaga a las claves foráneas solo si se definió `ON UPDATE CASCADE`

```sql
-- UPDATE con CASE: aumento diferenciado por departamento
UPDATE EMPLEADO
SET    Sueldo = CASE
                  WHEN Dno = 5 THEN Sueldo * 1.10
                  WHEN Dno = 4 THEN Sueldo * 1.05
                  ELSE Sueldo
                END;
```

> **Cuidado:** un `UPDATE` **sin `WHERE`** modifica **todas** las filas de la tabla.

### DELETE

- Elimina las filas que cumplen el `WHERE`; puede borrar ninguna, una o varias

```sql
-- U4A. Ninguna fila (no hay nadie con ese apellido)
DELETE FROM EMPLEADO WHERE Apellido1 = 'Cabrera';

-- U4B. Una fila
DELETE FROM EMPLEADO WHERE Dni = '123456789';

-- U4C. Todos los empleados de 'Investigación'
DELETE FROM EMPLEADO
WHERE  Dno IN (SELECT NúmeroDpto
               FROM   DEPARTAMENTO
               WHERE  NombreDpto = 'Investigación');

-- U4D. TODAS las filas: la tabla queda vacía, pero sigue existiendo
DELETE FROM EMPLEADO;
```

- `DELETE` borra **datos**; `DROP TABLE` borra la **tabla** (estructura y datos)
- El borrado puede propagarse a otras tablas si se definió `ON DELETE CASCADE`; si hay una clave foránea sin acción, el DBMS **rechaza** el borrado

> **Cuidado:** igual que `UPDATE`, un `DELETE` **sin `WHERE`** borra toda la tabla. Buena práctica: ejecutar primero un `SELECT` con el mismo `WHERE` para ver qué filas se afectarán.

## Orden de las cláusulas

```sql
SELECT   [DISTINCT] columnas, expresiones, CASE ...
FROM     tablas
WHERE    condiciones (AND, OR, NOT, LIKE, IN, BETWEEN, IS NULL)
ORDER BY columnas [ASC | DESC]
LIMIT    n OFFSET m;    -- o OFFSET m ROWS FETCH NEXT n ROWS ONLY
```

- Conceptualmente se evalúa en este orden: `FROM` → `WHERE` → `SELECT` → `ORDER BY` → `LIMIT`. Por eso un alias del `SELECT` se puede usar en `ORDER BY` pero **no** en `WHERE`

## Resumen de comandos DML

| Comando | Uso |
| --- | --- |
| `SELECT ... FROM ... WHERE` | Consultar filas que cumplen una condición |
| `AND`, `OR`, `NOT`, `BETWEEN` | Combinar y negar condiciones |
| `LIKE` (`%`, `_`) | Buscar por patrón de texto |
| `IN (...)` | Pertenencia a una lista o subconsulta |
| `IS NULL` / `IS NOT NULL` | Comprobar ausencia de valor |
| `CASE WHEN ... THEN ... END` | Valor condicional |
| `ORDER BY ... ASC/DESC` | Ordenar el resultado |
| `LIMIT` / `OFFSET` / `FETCH` | Limitar y paginar el resultado |
| `INSERT INTO ... VALUES` / `SELECT` | Agregar filas |
| `UPDATE ... SET ... WHERE` | Modificar filas |
| `DELETE FROM ... WHERE` | Eliminar filas |

[⬅️ Volver a Unidad II](./index.md)
