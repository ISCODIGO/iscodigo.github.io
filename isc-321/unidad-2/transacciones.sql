-- Pruebas de transacciones en SQLite con un esquema bancario (ISC-321, Unidad II)
-- Parte del ejemplo de la presentación: transferir 50 de la cuenta A (1000) a la B (2000).
--
-- Cómo ejecutarlo en DBeaver:
--   1. Crear una conexión SQLite a un archivo nuevo, por ejemplo banco.db
--   2. Dejar la conexión en modo Auto-commit (botón de la barra del editor). En modo
--      manual, el driver abre la transacción por su cuenta y BEGIN da error
--   3. Ejecutar todo el script con Alt+X. Cada SELECT abre una pestaña de resultados
--      con el número de prueba y una columna Resultado que debe decir OK
--
-- Varias pruebas fallan a propósito (están marcadas con "Se espera error"). DBeaver
-- pregunta qué hacer en cada error: elegir la opción de ignorar y seguir.
-- Si el script se detiene a la mitad, ejecutar ROLLBACK antes de volver a lanzarlo.
--
-- Las pruebas 13 a 16 necesitan dos conexiones: están en transacciones-concurrencia.sql

PRAGMA foreign_keys = ON;   -- En SQLite están desactivadas por defecto, y es por conexión

-- Reiniciar para poder ejecutarlo varias veces
DROP VIEW  IF EXISTS ESTADO;
DROP TABLE IF EXISTS MOVIMIENTO;
DROP TABLE IF EXISTS CUENTA;
DROP TABLE IF EXISTS CLIENTE;


-- =====================================================================
-- DDL
-- =====================================================================
CREATE TABLE CLIENTE (
  IdCliente INT         NOT NULL,
  Nombre    VARCHAR(40) NOT NULL,
  PRIMARY KEY (IdCliente)
);

CREATE TABLE CUENTA (
  NumCuenta CHAR(1)       NOT NULL,
  IdCliente INT           NOT NULL,
  Tipo      VARCHAR(10)   NOT NULL CHECK (Tipo IN ('Ahorro', 'Cheques')),
  Saldo     DECIMAL(12,2) NOT NULL CHECK (Saldo >= 0),   -- Regla de negocio: sin sobregiros
  PRIMARY KEY (NumCuenta),
  -- Diferida: se comprueba al hacer COMMIT, no en cada sentencia (prueba 12)
  FOREIGN KEY (IdCliente) REFERENCES CLIENTE(IdCliente) DEFERRABLE INITIALLY DEFERRED
);

-- Historial de la cuenta: un cargo es negativo y un abono, positivo
CREATE TABLE MOVIMIENTO (
  IdMovimiento INTEGER PRIMARY KEY,
  NumCuenta    CHAR(1)       NOT NULL,
  Monto        DECIMAL(12,2) NOT NULL CHECK (Monto <> 0),
  Concepto     VARCHAR(40)   NOT NULL,
  Fecha        TEXT          NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (NumCuenta) REFERENCES CUENTA(NumCuenta)
);

-- Una sola fila con el estado del banco. El total solo debe cambiar con dinero que entra o sale.
CREATE VIEW ESTADO AS
SELECT MAX(CASE WHEN NumCuenta = 'A' THEN Saldo END) AS A,
       MAX(CASE WHEN NumCuenta = 'B' THEN Saldo END) AS B,
       MAX(CASE WHEN NumCuenta = 'C' THEN Saldo END) AS C,
       MAX(CASE WHEN NumCuenta = 'D' THEN Saldo END) AS D,
       SUM(Saldo)                                    AS Total,
       (SELECT COUNT(*) FROM MOVIMIENTO)             AS Movs
FROM   CUENTA;


-- =====================================================================
-- DML inicial, dentro de una transacción
-- =====================================================================
BEGIN TRANSACTION;

INSERT INTO CLIENTE VALUES
  (1, 'Ana Mejía'),
  (2, 'Carlos Zelaya'),
  (3, 'Lucía Funes');

INSERT INTO CUENTA VALUES
  ('A', 1, 'Ahorro',  1000),
  ('B', 2, 'Ahorro',  2000),
  ('C', 3, 'Ahorro',   500),
  ('D', 3, 'Cheques', 1500);

INSERT INTO MOVIMIENTO (NumCuenta, Monto, Concepto) VALUES
  ('A', 1000, 'Depósito de apertura'),
  ('B', 2000, 'Depósito de apertura'),
  ('C',  500, 'Depósito de apertura'),
  ('D', 1500, 'Depósito de apertura');

COMMIT;

-- Carga inicial
SELECT 'Carga inicial' AS Prueba, *, iif(A = 1000 AND B = 2000 AND Total = 5000 AND Movs = 4, 'OK', 'FALLO') AS Resultado FROM ESTADO;


-- =====================================================================
-- 1. COMMIT: la transferencia completa queda permanente
-- =====================================================================
-- 1. COMMIT: transferir 50 de A a B
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo - 50 WHERE NumCuenta = 'A';
UPDATE CUENTA SET Saldo = Saldo + 50 WHERE NumCuenta = 'B';
INSERT INTO MOVIMIENTO (NumCuenta, Monto, Concepto) VALUES
  ('A', -50, 'Transferencia a B'),
  ('B',  50, 'Transferencia de A');
COMMIT;
SELECT '1. COMMIT' AS Prueba, *, iif(A = 950 AND B = 2050 AND Total = 5000 AND Movs = 6, 'OK', 'FALLO') AS Resultado FROM ESTADO;


-- =====================================================================
-- 2. Lo confirmado no se deshace: se compensa con otra transacción,
--    y el historial conserva tanto la transferencia como su reverso
-- =====================================================================
-- 2. Transacción compensadora: revertir la transferencia
-- Se espera error: no hay transacción activa
ROLLBACK;
SELECT '2. Transacción compensadora' AS Prueba, *, iif(A = 950, 'OK', 'FALLO') AS Resultado FROM ESTADO;

BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo + 50 WHERE NumCuenta = 'A';
UPDATE CUENTA SET Saldo = Saldo - 50 WHERE NumCuenta = 'B';
INSERT INTO MOVIMIENTO (NumCuenta, Monto, Concepto) VALUES
  ('A',  50, 'Reverso de transferencia'),
  ('B', -50, 'Reverso de transferencia');
COMMIT;
SELECT '2. Transacción compensadora' AS Prueba, *, iif(A = 1000 AND B = 2000 AND Movs = 8, 'OK', 'FALLO') AS Resultado FROM ESTADO;


-- =====================================================================
-- 3. ROLLBACK: la red de seguridad ante un UPDATE sin WHERE
-- =====================================================================
-- 3. ROLLBACK: UPDATE sin WHERE
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = 0;
SELECT '3. ROLLBACK' AS Prueba, *, iif(Total = 0, 'OK', 'FALLO') AS Resultado FROM ESTADO;
ROLLBACK;
SELECT '3. ROLLBACK' AS Prueba, *, iif(Total = 5000, 'OK', 'FALLO') AS Resultado FROM ESTADO;


-- =====================================================================
-- 4. Autocommit: sin BEGIN, cada sentencia se confirma sola.
--    Si falla algo antes del abono, A queda en 950 y se perdieron 50.
-- =====================================================================
-- 4. Autocommit: cargo sin transacción
UPDATE CUENTA SET Saldo = Saldo - 50 WHERE NumCuenta = 'A';
-- Se espera error: no hay transacción activa, el cargo ya no se puede deshacer
ROLLBACK;
SELECT '4. Autocommit' AS Prueba, *, iif(A = 950 AND B = 2000 AND Total = 4950, 'OK', 'FALLO') AS Resultado FROM ESTADO;

-- Corregirlo a mano para seguir con las pruebas
UPDATE CUENTA SET Saldo = Saldo + 50 WHERE NumCuenta = 'A';


-- =====================================================================
-- 5. Una sentencia es atómica: no quedan filas a medias
-- =====================================================================
-- 5. Atomicidad de una sentencia: comisión de 600 a todas las cuentas
-- Se espera error: CHECK constraint failed, porque C solo tiene 500
UPDATE CUENTA SET Saldo = Saldo - 600;
SELECT '5. Atomicidad de una sentencia' AS Prueba, *, iif(A = 1000 AND C = 500 AND Total = 5000, 'OK', 'FALLO') AS Resultado FROM ESTADO;


-- =====================================================================
-- 6. Un error no anula la transacción: COMMIT guarda lo que funcionó.
--    Aquí falla el cargo y se aplica el abono: aparecen 600 de la nada.
-- =====================================================================
-- 6. Error ignorado y COMMIT: transferir 600 de C a D sin fondos
BEGIN TRANSACTION;
-- Se espera error: CHECK constraint failed
UPDATE CUENTA SET Saldo = Saldo - 600 WHERE NumCuenta = 'C';
UPDATE CUENTA SET Saldo = Saldo + 600 WHERE NumCuenta = 'D';
COMMIT;
SELECT '6. Error ignorado y COMMIT' AS Prueba, *, iif(C = 500 AND D = 2100 AND Total = 5600, 'OK', 'FALLO') AS Resultado FROM ESTADO;

-- Corregirlo a mano para seguir con las pruebas
UPDATE CUENTA SET Saldo = Saldo - 600 WHERE NumCuenta = 'D';


-- =====================================================================
-- 7. La misma operación, decidiendo ROLLBACK tras el error
-- =====================================================================
-- 7. Error y ROLLBACK: el total no cambia
BEGIN TRANSACTION;
-- Se espera error: CHECK constraint failed
UPDATE CUENTA SET Saldo = Saldo - 600 WHERE NumCuenta = 'C';
ROLLBACK;
SELECT '7. Error y ROLLBACK' AS Prueba, *, iif(C = 500 AND D = 1500 AND Total = 5000, 'OK', 'FALLO') AS Resultado FROM ESTADO;


-- =====================================================================
-- 8. OR ROLLBACK (propio de SQLite): el error anula toda la transacción
-- =====================================================================
-- 8. UPDATE OR ROLLBACK: se abona primero y el cargo falla
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo + 600 WHERE NumCuenta = 'D';
-- Se esperan dos errores: CHECK constraint failed, y COMMIT sin transacción activa
UPDATE OR ROLLBACK CUENTA SET Saldo = Saldo - 600 WHERE NumCuenta = 'C';
COMMIT;
SELECT '8. UPDATE OR ROLLBACK' AS Prueba, *, iif(C = 500 AND D = 1500 AND Total = 5000, 'OK', 'FALLO') AS Resultado FROM ESTADO;


-- =====================================================================
-- 9. Consistencia: es tarea del programador.
--    Abonar a una cuenta inexistente no es un error: el UPDATE afecta 0 filas.
--    Con COMMIT se habrían perdido 50, así que el programa debe comprobarlo.
-- =====================================================================
-- 9. Abono a una cuenta que no existe: 0 filas y ningún error
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo - 50 WHERE NumCuenta = 'A';
UPDATE CUENTA SET Saldo = Saldo + 50 WHERE NumCuenta = 'Z';
SELECT '9. Abono a una cuenta que no existe' AS Prueba, changes() AS FilasAbonadas, iif(changes() = 0, 'OK', 'FALLO') AS Resultado;
ROLLBACK;
SELECT '9. Abono a una cuenta que no existe' AS Prueba, *, iif(A = 1000 AND Total = 5000, 'OK', 'FALLO') AS Resultado FROM ESTADO;


-- =====================================================================
-- 10. SAVEPOINT: deshacer solo una parte
-- =====================================================================
-- 10. SAVEPOINT: abono a la cuenta equivocada, y se corrige sin repetir el cargo
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo - 50 WHERE NumCuenta = 'A';
SAVEPOINT tras_el_cargo;
UPDATE CUENTA SET Saldo = Saldo + 50 WHERE NumCuenta = 'B';
SELECT '10. SAVEPOINT' AS Prueba, *, iif(A = 950 AND B = 2050, 'OK', 'FALLO') AS Resultado FROM ESTADO;
ROLLBACK TO tras_el_cargo;
UPDATE CUENTA SET Saldo = Saldo + 50 WHERE NumCuenta = 'D';
COMMIT;
SELECT '10. SAVEPOINT' AS Prueba, *, iif(A = 950 AND B = 2000 AND D = 1550 AND Total = 5000, 'OK', 'FALLO') AS Resultado FROM ESTADO;

-- Dejar los saldos como estaban
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo + 50 WHERE NumCuenta = 'A';
UPDATE CUENTA SET Saldo = Saldo - 50 WHERE NumCuenta = 'D';
COMMIT;


-- =====================================================================
-- 11. En SQLite el DDL también se puede deshacer
-- =====================================================================
-- 11. ROLLBACK de un CREATE TABLE
BEGIN TRANSACTION;
CREATE TABLE AUDITORIA (Id INTEGER PRIMARY KEY, Detalle TEXT);
SELECT '11. ROLLBACK de un CREATE TABLE' AS Prueba, COUNT(*) AS Tablas, iif(COUNT(*) = 1, 'OK', 'FALLO') AS Resultado
FROM   sqlite_master WHERE name = 'AUDITORIA';
ROLLBACK;
SELECT '11. ROLLBACK de un CREATE TABLE' AS Prueba, COUNT(*) AS Tablas, iif(COUNT(*) = 0, 'OK', 'FALLO') AS Resultado
FROM   sqlite_master WHERE name = 'AUDITORIA';


-- =====================================================================
-- 12. Una restricción diferida se comprueba en el COMMIT
-- =====================================================================
-- 12. COMMIT rechazado: la cuenta queda a nombre de un cliente inexistente
BEGIN TRANSACTION;
UPDATE CUENTA SET IdCliente = 999 WHERE NumCuenta = 'A';
-- Se espera error: FOREIGN KEY constraint failed. La transacción sigue abierta
COMMIT;
SELECT '12. COMMIT rechazado' AS Prueba, IdCliente, iif(IdCliente = 999, 'OK', 'FALLO') AS Resultado FROM CUENTA WHERE NumCuenta = 'A';
ROLLBACK;
SELECT '12. COMMIT rechazado' AS Prueba, IdCliente, iif(IdCliente = 1, 'OK', 'FALLO') AS Resultado FROM CUENTA WHERE NumCuenta = 'A';
