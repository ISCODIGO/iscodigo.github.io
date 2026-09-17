---
layout: default
title: "Introducción a las Bases de Datos Relacionales y conceptos básicos"
parent: "Unidad I: Introducción a las Bases de Datos Relacionales y conceptos básicos"
grand_parent: "ISC-321 Fundamentos de Bases de Datos"
nav_order: 1
---

# Introducción a las Bases de Datos Relacionales y conceptos básicos

## Introducción

Una **base de datos** es una colección de datos relacionados con un significado implícito. Tiene tres propiedades:

- Representa algún aspecto del mundo real (el **minimundo** o universo de discurso).
- Es una colección lógicamente coherente, no un surtido aleatorio de datos.
- Se diseña, construye y llena con un propósito específico, para un grupo de usuarios determinado.

Un **DBMS** (*Database Management System*) es el software de propósito general que permite **definir**, **construir**, **manipular** y **compartir** una base de datos:

| Función | Qué implica |
|---|---|
| Definir | Especificar tipos de datos, estructuras y restricciones (se guarda como **metadatos** en el catálogo) |
| Construir | Almacenar los datos en el medio controlado por el DBMS |
| Manipular | Consultar, actualizar y generar informes |
| Compartir | Permitir acceso simultáneo de varios usuarios y programas |

**Base de datos + software DBMS = sistema de bases de datos.**

## Características de la metodología de bases de datos

Frente al procesamiento tradicional de archivos (cada aplicación define sus propios archivos, con redundancia e inconsistencia), un DBMS aporta:

1. **Naturaleza autodescriptiva**: el catálogo (metadatos) describe la estructura de la base de datos, así el mismo software DBMS sirve para cualquier aplicación.
2. **Aislamiento entre programas y datos (independencia programa-datos)**: cambiar la estructura de un archivo no obliga a modificar los programas, porque la estructura vive en el catálogo, no en el código. En sistemas orientados a objetos existe también **independencia programa-operación**, mediante la separación de interfaz e implementación. Ambas dan lugar a la **abstracción de datos** (el modelo de datos oculta los detalles de almacenamiento).
3. **Soporte de varias vistas**: distintos usuarios pueden tener distintas perspectivas (subconjuntos o datos derivados) de la misma base de datos.
4. **Compartición de datos y procesamiento de transacciones multiusuario**: requiere **control de concurrencia** para que accesos simultáneos no produzcan resultados incorrectos. Una **transacción** debe cumplir propiedades como **aislamiento** y **atomicidad**

## Actores de la escena

Personas que usan la base de datos a diario:

- **DBA (administrador de la base de datos)**: responsable del acceso autorizado, coordinación de uso, recursos y seguridad.
- **Diseñadores de bases de datos**: identifican datos y estructuras antes de implementar la base de datos; integran las vistas de los distintos grupos de usuarios.
- **Usuarios finales**, clasificados en:
  - **Casuales**: consultas ocasionales con lenguaje de consulta sofisticado.
  - **Principiantes/paramétricos**: usan transacciones enlatadas predefinidas (cajeros, agentes de viajes, etc.).
  - **Sofisticados**: ingenieros/analistas que conocen a fondo el DBMS.
  - **Independientes**: mantienen bases de datos personales con software confeccionado (menús/GUI).
- **Analistas de sistemas y programadores de aplicaciones**: levantan requisitos e implementan las transacciones enlatadas.


## Ventajas de utilizar un DBMS

- **Control de la redundancia** (evita duplicación de esfuerzo, desperdicio de espacio e inconsistencias; permite redundancia *controlada* cuando conviene al rendimiento). En el procesamiento de archivos, al no haber control central, es fácil que la misma información (p. ej., dirección y teléfono de un cliente) quede duplicada en archivos distintos y que las copias diverjan (**inconsistencia de los datos**) cuando se actualiza una sin actualizar la otra.
- **Facilita el acceso a los datos** frente a los entornos de procesamiento de archivos, donde una consulta no prevista por los diseñadores originales (p. ej., "clientes de un código postal dado" o "con saldo ≥ 10.000 €") no tiene programa que la resuelva, obligando a extraer todo manualmente o a pedir un programa nuevo.
- **Restricción del acceso no autorizado** (seguridad y subsistema de autorización), necesaria porque no todos los usuarios deben ver todos los datos (p. ej., nóminas no debería acceder a las cuentas de clientes); en archivos, al añadirse los programas de forma *ad hoc*, es difícil hacer cumplir esas restricciones.
- **Almacenamiento persistente para objetos de programa** (relevante en BD orientadas a objetos, resuelve el *problema de incompatibilidad de impedancia*).
- **Estructuras de almacenamiento eficientes** (índices, módulo de buffer, optimización de consultas), que superan el **aislamiento de datos** propio de archivos dispersos en formatos distintos, difíciles de recorrer con nuevos programas.
- **Copias de seguridad y recuperación** ante fallos, garantizando la **atomicidad**: una operación como transferir 50 € de la cuenta A a la B debe ocurrir por completo o no ocurrir, evitando el estado inconsistente que deja un fallo a mitad de camino en el procesamiento de archivos convencional.
- **Varias interfaces de usuario** (lenguajes de consulta, GUI, formularios, interfaces web).
- **Representación de relaciones complejas** entre datos.
- **Restricciones de integridad** (tipos de datos, relaciones entre archivos, unicidad; en la práctica, "reglas de negocio"); en archivos, cada restricción se codifica por separado en cada programa, así que añadirla o cambiarla obliga a modificar todos los programas afectados.
- **Control de concurrencia**, que evita las anomalías del acceso concurrente sin control: por ejemplo, una cuenta con 500 € que recibe dos retiros simultáneos (50 € y 100 €) puede quedar en 450 € o 400 € en vez de los 350 € correctos si los programas leen el saldo antes de que el otro escriba.
- **Inferencia y acciones mediante reglas** (bases de datos deductivas, *triggers*, procedimientos almacenados, bases de datos activas).
- Beneficios adicionales: estándares, menor tiempo de desarrollo de aplicaciones, flexibilidad, información siempre actualizada, economías de escala.

## Breve historia de las aplicaciones de bases de datos

El procesamiento de datos impulsa el crecimiento de las computadoras desde sus primeros días: la automatización de tareas de procesamiento de datos precede a las computadoras comerciales (tarjetas perforadas de Herman Hollerith para el censo de EE. UU.). Las técnicas de almacenamiento y procesamiento evolucionaron así a lo largo de las décadas:

- **1950 - 1960**: cintas magnéticas para el almacenamiento. Las tareas de procesamiento (p. ej., nóminas) se automatizaron con datos en cintas, que solo se podían leer secuencialmente y eran mucho más lentas que la memoria principal; los programas debían procesar los datos en un orden determinado.
- **Finales de 1960 a 1970**: el uso generalizado de discos duros cambió el procesamiento de datos, al permitir **acceso directo** (unas decenas de milisegundos) y liberar los datos de la tiranía de la secuencialidad. Surgen los **sistemas jerárquicos y de red** (mainframes; listas y árboles en disco), que mezclaban la organización lógica con el almacenamiento físico, poco flexibles y con interfaces solo de lenguaje de programación. El artículo de Codd (1970) define el **modelo relacional** y las formas no procedimentales de consulta, ocultando los detalles de implementación al programador.
- **1980**: pese a lo académicamente interesante del modelo relacional, inicialmente no se usó en la práctica por su rendimiento frente a las BD de red y jerárquicas. El proyecto **System R** de IBM Research resolvió esto y dio lugar al primer producto relacional (SQL/DS); surgen DB2, Oracle, Ingres y Rdb. A inicios de los ochenta, las **bases de datos relacionales** (que separan almacenamiento físico de representación conceptual e introducen lenguajes de consulta de alto nivel) ya eran competitivas en rendimiento y, por su simplicidad frente al esfuerzo de programación de bajo nivel de las BD de red/jerárquicas, terminan reemplazándolas. También arranca la investigación en BD paralelas, distribuidas y **orientadas a objetos (OODB)** —surgidas con los lenguajes de programación orientados a objetos (encapsulación, herencia, identidad de objeto), de uso limitado por su complejidad y falta de estándares, y relegadas a nichos como ingeniería, multimedia y manufactura.
- **Inicios de 1990**: SQL se diseña para aplicaciones de ayuda a la toma de decisiones (intensivas en consultas), complementando el procesamiento de transacciones (intensivo en actualizaciones) que dominaba los ochenta. Crecen las herramientas de análisis de grandes volúmenes de datos y los productos paralelos; los distintos fabricantes añaden soporte relacional-orientado a objetos.
- **Finales de 1990**: el crecimiento explosivo de la Web obliga a las BD a soportar tasas de transacciones muy altas y disponibilidad 24 × 7; crece el **intercambio de datos en la Web / e-commerce**, con XML como estándar de intercambio.
- **2000**: emergen XML y su lenguaje de consultas XQuery como nueva tecnología de bases de datos, junto con el crecimiento de las técnicas de **informática autónoma / administración automática** para minimizar el esfuerzo de administración. Se extienden las **capacidades** hacia aplicaciones científicas, imágenes, video, minería de datos, aplicaciones espaciales y series temporales, impulsando bases de datos *back-end* para sistemas ERP y CRM. Surge también el contraste entre **bases de datos y recuperación de información (IR)**: datos estructurados (BD) frente a texto libre indexado por palabras clave (IR); la Web obliga a combinar ambas técnicas.

## Cuándo NO usar un DBMS

El uso de un DBMS implica sobrecostes (inversión inicial alta, generalidad innecesaria, costes de seguridad/concurrencia/recuperación). Puede ser preferible el procesamiento de archivos tradicional cuando:

- La aplicación es sencilla, bien definida y no va a cambiar.
- Hay requisitos estrictos de tiempo real que el sobrecoste del DBMS no permite cumplir.
- No existe acceso multiusuario a los datos.

Ejemplos típicos: software CAD propietario, sistemas de conmutación telefónica, algunas implementaciones GIS con esquemas propios.


[⬅️ Volver a Unidad I](./index.md)
