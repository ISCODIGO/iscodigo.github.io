-- Pruebas de concurrencia en SQLite (ISC-321, Unidad II)
-- Usa las tablas de transacciones.sql: ejecutar ese script primero.
--
-- Cómo ejecutarlo en DBeaver:
--   1. Abrir este archivo y copiarlo en una segunda pestaña (SQL Editor > New SQL Script).
--      La primera pestaña hace de T1 y la segunda de T2. Cada pestaña debe tener su propia
--      conexión: es la opción "Open separate connection for each editor" de DBeaver.
--      Si en la prueba 13 Resultado dice FALLO, las dos pestañas comparten conexión
--   2. Dejar ambas en modo Auto-commit
--   3. Seguir el orden de los pasos: ejecutar cada bloque, con Ctrl+Enter por sentencia,
--      en la pestaña que indica su etiqueta [T1] o [T2]
--
-- "database is locked" es el resultado esperado donde se indica. En la prueba 14 puede
-- tardar unos segundos en aparecer, porque el driver espera antes de rendirse.


-- =====================================================================
-- Preparación
-- =====================================================================
-- [T1]
PRAGMA journal_mode = WAL;   -- Permite leer mientras otra conexión escribe; cada lectura ve una foto fija
PRAGMA foreign_keys = ON;

-- [T2]
PRAGMA foreign_keys = ON;


-- =====================================================================
-- 13. Sin lectura sucia ni suma incorrecta: a mitad de la transferencia de T1,
--     T2 ve A = 1000 y el total completo, no A + B = 2950
-- =====================================================================
-- [T1]
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo - 50 WHERE NumCuenta = 'A';

-- [T2]
SELECT '13' AS Prueba, *, iif(A = 1000 AND Total = 5000, 'OK', 'FALLO') AS Resultado FROM ESTADO;

-- [T1]
ROLLBACK;


-- =====================================================================
-- 14. Un solo escritor a la vez
-- =====================================================================
-- [T1]
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo - 50 WHERE NumCuenta = 'A';

-- [T2] Se espera error: database is locked
UPDATE CUENTA SET Saldo = Saldo + 50 WHERE NumCuenta = 'C';

-- [T1]
ROLLBACK;
SELECT '14' AS Prueba, *, iif(A = 1000 AND C = 500, 'OK', 'FALLO') AS Resultado FROM ESTADO;


-- =====================================================================
-- 15. Sin lectura irrepetible ni fantasmas: T1 retira 100 mientras T2 revisa A
-- =====================================================================
-- [T2]
BEGIN TRANSACTION;
SELECT '15 antes' AS Prueba, (SELECT Saldo FROM CUENTA WHERE NumCuenta = 'A') AS SaldoA, COUNT(*) AS MovsA,
       iif((SELECT Saldo FROM CUENTA WHERE NumCuenta = 'A') = 1000 AND COUNT(*) = 3, 'OK', 'FALLO') AS Resultado
FROM   MOVIMIENTO WHERE NumCuenta = 'A';

-- [T1] Cambia el saldo, inserta un movimiento de A y confirma
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo - 100 WHERE NumCuenta = 'A';
INSERT INTO MOVIMIENTO (NumCuenta, Monto, Concepto) VALUES ('A', -100, 'Retiro en cajero');
COMMIT;

-- [T2] Repite la consulta dentro de su transacción: no cambia
SELECT '15 durante' AS Prueba, (SELECT Saldo FROM CUENTA WHERE NumCuenta = 'A') AS SaldoA, COUNT(*) AS MovsA,
       iif((SELECT Saldo FROM CUENTA WHERE NumCuenta = 'A') = 1000 AND COUNT(*) = 3, 'OK', 'FALLO') AS Resultado
FROM   MOVIMIENTO WHERE NumCuenta = 'A';
COMMIT;

-- [T2] Una vez terminada, ya ve lo confirmado
SELECT '15 después' AS Prueba, (SELECT Saldo FROM CUENTA WHERE NumCuenta = 'A') AS SaldoA, COUNT(*) AS MovsA,
       iif((SELECT Saldo FROM CUENTA WHERE NumCuenta = 'A') = 900 AND COUNT(*) = 4, 'OK', 'FALLO') AS Resultado
FROM   MOVIMIENTO WHERE NumCuenta = 'A';

-- [T1] Dejar los datos como estaban
BEGIN TRANSACTION;
UPDATE CUENTA SET Saldo = Saldo + 100 WHERE NumCuenta = 'A';
DELETE FROM MOVIMIENTO WHERE Concepto = 'Retiro en cajero';
COMMIT;


-- =====================================================================
-- 16. Sin actualización perdida: sobre A = 1000, un cargo de 50 y un abono de 40
--     deben dejar 990. Si T2 escribiera con su valor viejo, quedaría en 1040.
-- =====================================================================
-- [T2]
BEGIN TRANSACTION;
SELECT '16' AS Prueba, A AS LeidoPorT2 FROM ESTADO;

-- [T1]
UPDATE CUENTA SET Saldo = Saldo - 50 WHERE NumCuenta = 'A';

-- [T2] Se espera error: database is locked, porque la foto de T2 ya no es la actual
UPDATE CUENTA SET Saldo = Saldo + 40 WHERE NumCuenta = 'A';

-- [T2] Reintenta desde el principio: con el valor actual, se aplican ambos cambios
ROLLBACK;
UPDATE CUENTA SET Saldo = Saldo + 40 WHERE NumCuenta = 'A';
SELECT '16 reintento' AS Prueba, *, iif(A = 990, 'OK', 'FALLO') AS Resultado FROM ESTADO;

-- [T1] Dejar el saldo como estaba
UPDATE CUENTA SET Saldo = 1000 WHERE NumCuenta = 'A';


-- =====================================================================
-- Estado final: los saldos de la carga inicial
-- =====================================================================
-- [T1]
SELECT 'Final' AS Prueba, *, iif(A = 1000 AND B = 2000 AND C = 500 AND D = 1500 AND Total = 5000 AND Movs = 8, 'OK', 'FALLO') AS Resultado FROM ESTADO;
