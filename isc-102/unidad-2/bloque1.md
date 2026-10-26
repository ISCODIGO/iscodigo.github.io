---
layout: post
title: "1. Funciones y Estructura de un Programa"
parent: "Unidad II: Funciones, Arreglos, Punteros y Memoria "
nav_order: 1
---

Una **función** es un grupo de sentencias diseñadas para realizar una tarea específica. La programación estructurada se basa en dividir un problema grande en módulos pequeños y manejables (Capítulo 7, Sección 7.1).

### 1. Elementos Básicos y Retorno de Valores
Toda función consta de una **cabecera** y un **cuerpo**. La cabecera define el tipo de retorno, el nombre y la lista de parámetros (Capítulo 7, Sección 7.2).

*   **Retorno de valores:** Se utiliza la sentencia `return` para enviar un resultado de vuelta a la función llamadora. Si la función no devuelve nada, se marca como `void` (Capítulo 7, Sección 7.2).

**Ejemplo de Función en C:**

<div style="margin: 25px 0; border: 2px solid #BB86FC; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
    <iframe 
        src="{{ site.baseurl }}/compilerc.html?file=https://raw.githubusercontent.com/ISCODIGO/iscodigo.github.io/main/isc-102/unidad-2/code/ejemplo1-1.c" 
        width="100%" 
        height="600px" 
        frameborder="0">
    </iframe>
</div>

### 2. Reglas de Ámbito (Alcance) y Clases de Almacenamiento
El ámbito o alcance es la zona del programa en la que una variable es visible para las funciones. Según su posición y modificadores, una variable puede tener un ámbito de programa, de archivo fuente, de función o de bloque.

#### Variables Externas (Globales)
Se declaran fuera de cualquier función, normalmente al principio del archivo fuente. Son visibles para cualquier función del resto del programa. Si se desea usar una variable definida en otro archivo fuente, se utiliza la palabra reservada `extern`.

**Ejemplo de Ámbito de Programa (Capítulo 7, Sección 7.6):**

<div style="margin: 25px 0; border: 2px solid #BB86FC; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
    <iframe 
        src="{{ site.baseurl }}/compilerc.html?file=https://raw.githubusercontent.com/ISCODIGO/iscodigo.github.io/main/isc-102/unidad-2/code/ejemplo2-1.c" 
        width="100%" 
        height="600px" 
        frameborder="0">
    </iframe>
</div>

#### Variables Estáticas (`static`)
A diferencia de las variables automáticas, las estáticas no se borran al terminar la función; retienen su valor entre llamadas sucesivas y se inicializan solo una vez.

**Ejemplo de Acumulación (Capítulo 7, Sección 7.7):**
```c
float ResultadosTotales(float valor) {
    static float suma = 0; // Retiene su valor entre llamadas [10]
    suma = suma + valor;
    return suma;
}
```

#### Variables de Registro (`register`)
Es una sugerencia al compilador para que intente almacenar la variable en un registro de la CPU en lugar de la memoria RAM, buscando un acceso ultrarrápido. Solo puede aplicarse a variables locales.

**Ejemplo en un Bucle (Capítulo 7, Sección 7.7):**
```c
void proceso_rapido() {
    // Aplicación típica como variable de control de un bucle [8, 11]
    register int indice; 
    for (indice = 0; indice < 1000; indice++) {
        // Operaciones repetitivas
    }
}
```

#### Estructura de Bloques
Un bloque está delimitado por llaves `{ }`. Una variable declarada dentro de un bloque es invisible fuera de él.

**Ejemplo de Ámbito de Bloque (Capítulo 7, Sección 7.6):**
```c
void funcion_con_bloques(int j) {
    if (j > 3) {
        int i; // i solo es visible dentro de este bloque if [12, 13]
        for (i = 0; i < 10; i++) {
            printf("%d", i);
        }
    } 
    // Aquí i ya no es visible [13]
}
```

#### Archivos de Cabecera
Los archivos de cabecera (.h) contienen código fuente C, como prototipos de funciones o definiciones de macros, que se insertan en otros archivos mediante la directiva `#include`. El preprocesador mezcla el contenido del archivo antes de la compilación.

**Ejemplo de Inclusión (Capítulo 3, Sección 3.1):**
```c
// Uso de biblioteca estándar [15, 17]
#include <stdio.h> 

// Uso de cabecera personalizada del usuario [15, 18]
#include "mis_definiciones.h" 

int main() {
    printf("Uso de funciones definidas en cabeceras\n");
    return 0;
}
```

**Resumen de Visibilidad (Basado en Figura 7.5):**
![Resumen de visibilidad de variables](./visibilidad.png)

### 3. Recursividad
Una función es **recursiva** si se invoca a sí misma. Es vital incluir un **caso base** para evitar que las llamadas sean infinitas y agoten la memoria (Capítulo 7, Sección 7.14).

**Flujo de llamadas recursivas (Esquema conceptual):**

![Llamadas recursivas de fact(3)](./recursividad.png)

En el caso del factorial de un número ($n!$), la definición recursiva establece que el factorial de 0 o 1 es 1 (**caso base**), y para cualquier otro número es $n \times (n-1)!$.

**Ejemplo de Factorial en C (Recursivo):**

<div style="margin: 25px 0; border: 2px solid #BB86FC; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
    <iframe 
        src="{{ site.baseurl }}/compilerc.html?file=https://raw.githubusercontent.com/ISCODIGO/iscodigo.github.io/main/isc-102/unidad-2/code/ejemplo3-1.c" 
        width="100%" 
        height="600px" 
        frameborder="0">
    </iframe>
</div>


**Comportamiento del flujo recursivo:**
Cuando ejecutamos `factorial(5)`, el programa realiza una serie de llamadas descendentes hasta alcanzar el caso base y luego "rebota" devolviendo los resultados hacia arriba.

![Fases descendente y ascendente de factorial(5)](./factorial-fases.png)

*   **Condición de terminación:** Es vital para evitar una recursión infinita que agotaría la pila (*stack*) de la computadora.
*   **Eficiencia:** Aunque la recursividad es más natural para ciertos problemas, consume más tiempo y memoria que una solución iterativa debido a la sobrecarga de múltiples llamadas.



### 4. El Preprocesador de C
Antes de la compilación real, el preprocesador actúa como un "editor inteligente". Sus directivas más comunes son `#include` (insertar archivos) y `#define` (sustitución de macros) (Capítulo 3, Sección 3.1).

El preprocesador es una fase previa a la compilación real que prepara el código fuente antes de ser analizado sintácticamente.

#### A. Directiva `#include` (Inserción de archivos)
Indica al compilador que inserte el contenido íntegro de un archivo de cabecera en esa posición.

*   `#include <nombre.h>`: Busca el archivo en el directorio estándar del sistema.
*   `#include "nombre.h"`: Busca el archivo primero en el directorio actual del proyecto.

**Ejemplo:**
```c
#include <stdio.h>     // Biblioteca estándar
#include "mis_mates.h" // Cabecera propia
```

**Ejemplo completo con archivos separados:**
Un proyecto típico separa la *declaración* (`.h`) de la *implementación* (`.c`):

```text
proyecto/
├── mis_mates.h   ← prototipos (qué funciones existen)
├── mis_mates.c   ← implementación (cómo funcionan)
└── main.c        ← programa que las usa
```

📄 **`mis_mates.h`**
```c
#ifndef MIS_MATES_H
#define MIS_MATES_H

int sumar(int a, int b);
int cuadrado(int x);

#endif
```

📄 **`mis_mates.c`**
```c
#include "mis_mates.h"

int sumar(int a, int b) {
    return a + b;
}

int cuadrado(int x) {
    return x * x;
}
```

📄 **`main.c`**
```c
#include <stdio.h>
#include "mis_mates.h"   // el preprocesador pega aquí los prototipos

int main() {
    printf("3 + 4 = %d\n", sumar(3, 4));    // 7
    printf("5^2   = %d\n", cuadrado(5));    // 25
    return 0;
}
```

**Compilación** (se compilan los `.c`, nunca el `.h`):
```bash
gcc main.c mis_mates.c -o programa
./programa
```

Después del preprocesador, `main.c` queda como si los prototipos se hubieran escrito a mano en su lugar; así el compilador conoce `sumar` y `cuadrado` antes de usarlas, y el enlazador (*linker*) las une con su código de `mis_mates.c`.

#### B. Directiva `#define` y el concepto de "Replace"
Se utiliza para crear macros o constantes simbólicas. No ocupa espacio en memoria RAM; el preprocesador realiza una **sustitución de texto pura** (Capítulo 3, Sección 3.9).

**Ejemplo de Sustitución:**
```c
#define PI 3.141592 
int main() {
    float radio = 5.0;
    float area = PI * (radio * radio); // El compilador verá el valor directamente
    return 0;
}
```

**Macros con parámetros (parecidas a funciones):**
`#define` también acepta argumentos. Parece una función, pero el preprocesador solo reemplaza texto: no hay llamada, ni tipos, ni evaluación previa de los argumentos.

```c
#define CUADRADO_MAL(x) x * x
#define CUADRADO(x)     ((x) * (x))
#define MAX(a, b)       ((a) > (b) ? (a) : (b))

int main() {
    int n = 3;
    printf("%d\n", CUADRADO_MAL(n + 1)); // n + 1 * n + 1  -> 7  (¡incorrecto!)
    printf("%d\n", CUADRADO(n + 1));     // ((n + 1) * (n + 1)) -> 16
    printf("%d\n", MAX(4, 9));           // ((4) > (9) ? (4) : (9)) -> 9
    return 0;
}
```

*   **Regla:** envolver cada parámetro y la expresión completa entre paréntesis.
*   **Cuidado con efectos secundarios:** `CUADRADO(n++)` se expande a `((n++) * (n++))`, que incrementa `n` dos veces (comportamiento indefinido). Una función normal no tiene este problema.

**Macros de varias líneas:**
Una macro termina al final de la línea. Para continuarla en la siguiente se coloca `\` al final de cada línea (sin espacios después). Si la macro contiene varias instrucciones, se envuelve en `do { ... } while (0)` para que se comporte como **una sola** instrucción.

```c
#include <stdio.h>

#define INTERCAMBIAR(a, b) \
    do {                   \
        int tmp = (a);     \
        (a) = (b);         \
        (b) = tmp;         \
    } while (0)

int main() {
    int x = 1, y = 2;
    if (x < y)
        INTERCAMBIAR(x, y);   // el ';' final cierra el do-while
    else
        printf("Ya están en orden\n");
    printf("x = %d, y = %d\n", x, y); // x = 2, y = 1
    return 0;
}
```

*   **¿Por qué `do { } while (0)`?** Si solo se usaran llaves `{ ... }`, el `;` después de `INTERCAMBIAR(x, y)` quedaría como una instrucción vacía y el `else` perdería su `if`: error de compilación. El `do-while (0)` se ejecuta exactamente una vez y sí necesita ese `;`.
*   **`tmp` es local al bloque:** no choca con otras variables del programa (salvo que alguien llame `INTERCAMBIAR(tmp, y)`).

#### C. El "if" del Preprocesador (Procesamiento Condicional)
Permite decidir qué partes del código se compilan y cuáles se ignoran. Es vital para evitar que un archivo se incluya más de una vez mediante **guardas de cabecera** (Capítulo 19, Sección 19.3).


**Ejemplo de Guardas de Cabecera:**
```c
#ifndef MI_CABECERA_H
#define MI_CABECERA_H

// Definiciones...

#endif 
```

`#ifndef` significa "*if not defined*": el bloque hasta `#endif` solo se procesa si el nombre todavía **no** ha sido definido con `#define`.

**¿Qué problema resuelve?** Supongamos esta cabecera sin guardas:

```c
// punto.h
struct Punto { int x, y; };
```

```c
// main.c
#include "punto.h"
#include "geometria.h"   // geometria.h también hace #include "punto.h"
```

Como `#include` copia el texto, `struct Punto` aparece **dos veces** en `main.c` y el compilador marca error: *redefinition of 'struct Punto'*.

**¿Cómo funciona la guarda?**
1.  Primera inclusión: `PUNTO_H` no existe → se entra al bloque, se define `PUNTO_H` y se copian las definiciones.
2.  Segunda inclusión: `PUNTO_H` ya existe → el preprocesador salta todo hasta `#endif`. El archivo queda vacío.

```c
// punto.h
#ifndef PUNTO_H
#define PUNTO_H

struct Punto { int x, y; };

#endif
```

*   **Convención:** el nombre de la guarda es el del archivo en mayúsculas, con `_` en lugar de `.` (`punto.h` → `PUNTO_H`). Debe ser único en todo el proyecto.
*   **Evitar** nombres que comienzan con `_` + mayúscula (como `_PUNTO_H`): están reservados para el compilador y la biblioteca estándar.
*   **Alternativa:** muchos compiladores aceptan `#pragma once` al inicio del archivo, que hace lo mismo en una línea, pero no forma parte del estándar de C.

**Ejemplo de If para activar depuración:**
```c
#define DEBUG 1

#if DEBUG
    printf("Modo depuración activado\n");
#else
    printf("Modo producción\n");
#endif
```

**Ejemplo de If para activar caclulos condicionales:**
<div style="margin: 25px 0; border: 2px solid #BB86FC; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
    <iframe 
        src="{{ site.baseurl }}/compilerc.html?file=https://raw.githubusercontent.com/ISCODIGO/iscodigo.github.io/main/isc-102/unidad-2/code/ejemplo4-1.c" 
        width="100%" 
        height="600px" 
        frameborder="0">
    </iframe>
</div>

**Resumen de Ventajas:**
*   **Velocidad:** Las macros son rápidas porque evitan la sobrecarga de una llamada a función.
*   **Eficiencia:** El procesamiento condicional evita errores de duplicidad en proyectos grandes.

[⬅️ Volver al índice de la unidad](./index.md)