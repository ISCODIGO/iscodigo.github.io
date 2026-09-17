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
4. **Compartición de datos y procesamiento de transacciones multiusuario**: requiere **control de concurrencia** para que accesos simultáneos no produzcan resultados incorrectos. Una **transacción** debe cumplir propiedades como **aislamiento** y **atomicidad** (se explican en profundidad en la Parte 5 del libro).

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

- **Control de la redundancia** (evita duplicación de esfuerzo, desperdicio de espacio e inconsistencias; permite redundancia *controlada* cuando conviene al rendimiento).
- **Restricción del acceso no autorizado** (seguridad y subsistema de autorización).
- **Almacenamiento persistente para objetos de programa** (relevante en BD orientadas a objetos, resuelve el *problema de incompatibilidad de impedancia*).
- **Estructuras de almacenamiento eficientes** (índices, módulo de buffer, optimización de consultas).
- **Copias de seguridad y recuperación** ante fallos.
- **Varias interfaces de usuario** (lenguajes de consulta, GUI, formularios, interfaces web).
- **Representación de relaciones complejas** entre datos.
- **Restricciones de integridad** (tipos de datos, relaciones entre archivos, unicidad; en la práctica, "reglas de negocio").
- **Inferencia y acciones mediante reglas** (bases de datos deductivas, *triggers*, procedimientos almacenados, bases de datos activas).
- Beneficios adicionales: estándares, menor tiempo de desarrollo de aplicaciones, flexibilidad, información siempre actualizada, economías de escala.

## Breve historia de las aplicaciones de bases de datos

1. **Sistemas jerárquicos y de red** (mainframes, 1960s-1980s): mezclaban la organización lógica con el almacenamiento físico, poco flexibles y con interfaces solo de lenguaje de programación.
2. **Bases de datos relacionales**: separan almacenamiento físico de representación conceptual; introducen lenguajes de consulta de alto nivel. Lentas al inicio, se volvieron predominantes tras mejoras en indexación y optimización.
3. **Bases de datos orientadas a objetos (OODB)**: surgen con los lenguajes de programación orientados a objetos (encapsulación, herencia, identidad de objeto); uso limitado por complejidad y falta de estándares, quedan para nichos (ingeniería, multimedia, manufactura).
4. **Intercambio de datos en la Web / e-commerce**: XML como estándar de intercambio.
5. **Capacidades extendidas** para aplicaciones científicas, imágenes, video, minería de datos, aplicaciones espaciales y series temporales, impulsando bases de datos *back-end* para sistemas ERP y CRM.
6. **Bases de datos vs. recuperación de información (IR)**: datos estructurados (BD) frente a texto libre indexado por palabras clave (IR); la Web obliga a combinar ambas técnicas.

## Cuándo NO usar un DBMS

El uso de un DBMS implica sobrecostes (inversión inicial alta, generalidad innecesaria, costes de seguridad/concurrencia/recuperación). Puede ser preferible el procesamiento de archivos tradicional cuando:

- La aplicación es sencilla, bien definida y no va a cambiar.
- Hay requisitos estrictos de tiempo real que el sobrecoste del DBMS no permite cumplir.
- No existe acceso multiusuario a los datos.

Ejemplos típicos: software CAD propietario, sistemas de conmutación telefónica, algunas implementaciones GIS con esquemas propios.


[⬅️ Volver a Unidad I](./index.md)
