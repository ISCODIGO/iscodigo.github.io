---
layout: post
title: "2: Tipos, Operadores y Expresiones"
parent: "Unidad I: Introducción y Lógica de Programación"
nav_order: 4
---

Este bloque es el "taller" donde definimos nuestras herramientas de trabajo. En C, no basta con dar instrucciones; debemos ser precisos sobre qué datos usamos y cómo los manipulamos.

### 1. Nombres de variables (Identificadores)
Para nombrar variables, C sigue reglas estrictas que todo programador debe memorizar (Capítulo 3, Sección 3.6):
*   **Reglas de oro:** Deben comenzar con una letra o un subrayado (`_`). No pueden contener espacios ni caracteres especiales como `@` o `&`.
*   **Sensibilidad a mayúsculas:** C es *case-sensitive*. Esto significa que `minum`, `MiNum` y `MINUM` son tres variables totalmente distintas.
*   **Longitud:** Aunque pueden ser largos, muchos compiladores solo consideran significativos los primeros 31 o 32 caracteres.
*   **Ejemplos:**
    *   ✅ *Válidos:* `fecha_nacimiento`, `_valor`, `notaFinal2`.
    *   ❌ *Inválidos:* `1erParcial` (empieza con número), `valor total` (tiene espacio).

### 2. Tipos de datos y tamaños


Tipos comunes en un sistema moderno de 64 bits:

| Tipo | Tamaño | Mínimo | Máximo |
|------|--------|--------|--------|
| `char` | 1 byte | -128 | 127 |
| `unsigned char` | 1 byte | 0 | 255 |
| `short` | 2 bytes | -32 768 | 32 767 |
| `unsigned short` | 2 bytes | 0 | 65 535 |
| `int` | 4 bytes | -2 147 483 648 | 2 147 483 647 |
| `unsigned int` | 4 bytes | 0 | 4 294 967 295 |
| `long` | 8 bytes* | -9 223 372 036 854 775 808 | 9 223 372 036 854 775 807 |
| `unsigned long` | 8 bytes* | 0 | 18 446 744 073 709 551 615 |
| `long long` | 8 bytes | -9 223 372 036 854 775 808 | 9 223 372 036 854 775 807 |
| `float` | 4 bytes | ±1.2 × 10⁻³⁸ | ±3.4 × 10³⁸ (~6-7 dígitos de precisión) |
| `double` | 8 bytes | ±2.2 × 10⁻³⁰⁸ | ±1.8 × 10³⁰⁸ (~15-16 dígitos de precisión) |
| `long double` | 16 bytes** | ±3.4 × 10⁻⁴⁹³² | ±1.2 × 10⁴⁹³² (~18-19 dígitos de precisión) |

> En Windows, `long` ocupa 4 bytes (mismo rango que `int`). \*\* `long double` depende de la plataforma: en Linux x86-64 usa 80 bits útiles (almacenados en 16 bytes); en Windows (MSVC) y macOS con Apple Silicon es igual a `double` (8 bytes). En `float`, `double` y `long double`, el mínimo es el menor valor positivo normalizado. Los límites exactos de tu sistema están en `<limits.h>` (`INT_MAX`, `INT_MIN`, …) y `<float.h>` (`FLT_MAX`, `DBL_MAX`, …).


**¿Cómo saber cuánto ocupa un dato en MI computadora?**
Usamos el operador **`sizeof`**. Si escribes `sizeof(int)`, el programa te dirá cuántos bytes reserva tu sistema para un entero (Capítulo 4, Sección 4.10).

### 3. Constantes: Valores que no cambian
Existen dos formas principales de definir valores fijos en C (Capítulo 3, Sección 3.9):
1.  **#define (Macros):** Se definen antes del `main`. No ocupan espacio de memoria real, el compilador simplemente busca y reemplaza el nombre por el valor. 
    *   *Ejemplo:* `#define PI 3.141592`
2.  **const:** Se declaran como una variable normal pero con la palabra reservada `const`. Tienen tipo de dato y terminan en punto y coma.
    *   *Ejemplo:* `const int DIAS_SEMANA = 7;`

### 4. Operadores: El motor de los cálculos
C ofrece una rica colección de operadores para transformar datos:

*   **Aritméticos (Capítulo 4, Sección 4.3):** Además de `+`, `-`, `*` y `/`, tenemos el operador **módulo `%`**, que devuelve el resto de una división entera.
    *   *Ejemplo:* `15 % 12` da como resultado `3`.
*   **Incremento y Decremento (Capítulo 4, Sección 4.4):** Los operadores `++` y `--` suman o restan 1. ¡Cuidado con su posición!
    *   `++n` (Prefijo): Primero incrementa, luego entrega el valor.
    *   `n++` (Posfijo): Primero entrega el valor actual, luego incrementa.
*   **Relacionales y Lógicos (Capítulo 4, Secciones 4.5 y 4.6):** Se usan para comparar. En C, **0 es Falso y cualquier otro número es Verdadero**.
    *   **&& (AND):** Verdadero solo si ambos son ciertos.
    *   **\|\| (OR):** Verdadero si al menos uno es cierto.
    *   **! (NOT):** Invierte el valor (lo que es cierto lo hace falso).

### 5. Conversión de tipos (Cast)
A veces mezclamos peras con manzanas. C puede convertir tipos automáticamente (conversión implícita), pero si queremos forzarlo, usamos el **moldeo o cast** (Capítulo 4, Sección 4.11):
*   *Ejemplo:* Si tienes `float x = 3.9;` y quieres convertirlo a entero, escribes `(int)x`. El resultado será `3` (se pierden los decimales).

### 6. Evaluación de Precedencia
Al igual que en matemáticas, no todas las operaciones se hacen a la vez. Los paréntesis `()` tienen la máxima prioridad, seguidos por la multiplicación y división, y finalmente suma y resta (Capítulo 4, Sección 4.12 y Tabla 4.13). Conocer esto evita errores lógicos donde el resultado no es el esperado por falta de paréntesis.

[⬅️ Volver al índice de la unidad](./index.md)