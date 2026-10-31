---
layout: post
title: "Recursión"
parent: "Unidad II: Recursión, Listas, Genéricos, Pilas y Colas"
grand_parent: "ISC-211 Estructuras de Datos"
nav_order: 6
---

## Introducción

Resumen del capítulo 2 del libro de texto: qué es un algoritmo recursivo, sus componentes, la recursión infinita y la comparación entre iteración y recursión.

## Recursividad

Un algoritmo es **recursivo** cuando un método se llama a sí mismo (directa o indirectamente), definiéndose en términos de una versión más simple de sí mismo. Suele aplicar el principio de **divide y vencerás**.

Ejemplo clásico: el factorial de un número natural `n`, definido como `n! = n * (n-1)!`, con caso base `0! = 1`.

### Consideraciones para emplear la recursión

- Debe existir al menos un **caso base**, que se resuelve directamente sin más recursión.
- Cada llamada recursiva debe **progresar** hacia el caso base.
- Cada llamada recursiva mantiene sus **variables locales independientes** de las demás llamadas en espera en la pila (stack): al terminar una llamada, el control regresa a la llamada anterior, que conserva sus propios valores.

### Sucesión de Fibonacci

`1, 1, 2, 3, 5, 8, 13, 21, 34, 55, …` — a partir del tercer término, cada uno es la suma de los dos anteriores. Tiene dos casos base (los dos primeros términos = 1) y es fácil de expresar recursivamente, pero es un ejemplo de solución "elegante" que resulta ineficiente: calcular Fibonacci(4) requiere 9 llamadas, Fibonacci(5) requiere 15, y el crecimiento es tan explosivo que calcular términos grandes con este algoritmo tardaría años en una computadora actual. Lección: una solución recursiva simple no siempre es la más eficiente (el **análisis de algoritmos** permite detectarlo), pero una pequeña modificación (evitar recalcular subproblemas) resuelve el problema.

La versión directa sigue la definición al pie de la letra:

```java
public static long fibonacci(int n) {
    if (n <= 1) return n;                          // casos base: F(0) = 0, F(1) = 1
    return fibonacci(n - 1) + fibonacci(n - 2);    // dos llamadas recursivas
}
```

El problema es que repite trabajo: `fibonacci(5)` calcula `fibonacci(3)` dos veces, `fibonacci(2)` tres veces, y así sucesivamente. Cada llamada genera dos más, por lo que el número de llamadas crece de forma **exponencial**.

### Mejora: memoización

La **memoización** consiste en guardar el resultado de cada subproblema la primera vez que se calcula y reutilizarlo en las siguientes. Basta con un arreglo `memo` donde `memo[k]` almacena `F(k)` (un 0 indica que aún no se ha calculado):

```java
public static long fibonacciMemo(int n) {
    return fibonacciMemo(n, new long[n + 1]);
}

private static long fibonacciMemo(int n, long[] memo) {
    if (n <= 1) return n;
    if (memo[n] != 0) return memo[n];              // ya calculado: se reutiliza
    memo[n] = fibonacciMemo(n - 1, memo) + fibonacciMemo(n - 2, memo);
    return memo[n];
}
```

El algoritmo sigue siendo recursivo y tiene los mismos casos base. La diferencia es que cada `F(k)` se calcula **una sola vez**, así que el número de llamadas pasa a ser lineal (2n − 1):

| n | F(n) | Llamadas (directa) | Llamadas (memoización) |
|---|---|---|---|
| 5 | 5 | 15 | 9 |
| 10 | 55 | 177 | 19 |
| 30 | 832,040 | 2,692,537 | 59 |
| 40 | 102,334,155 | 331,160,281 | 79 |

La versión directa con `n = 40` ya es notablemente lenta y con `n = 90` no terminaría en un tiempo razonable; la versión con memoización calcula `F(90)` en 179 llamadas. El costo de la mejora es memoria adicional: el arreglo de `n + 1` posiciones.

### Recursión infinita

Ocurre cuando falta el caso base o las llamadas no progresan hacia él, agotando la pila del programa (**stack overflow**) y terminando el programa de forma anormal. Ejemplos: un `factorial` sin caso base, o invocarlo con un valor negativo (nunca llega a 0).

## Iteración vs. recursión

Todo algoritmo recursivo puede escribirse también de forma iterativa (no existe lo contrario). La recursión paga un costo adicional por cada llamada en espera en la pila, por lo que:

- Si existe una solución iterativa simple y natural, se prefiere sobre la recursiva (p. ej., sumar los números de 1 a n: una versión recursiva dejaría n llamadas pendientes en la pila, con riesgo de desbordarla).
- La recursión conviene cuando la naturaleza del problema es recursiva y las estructuras adicionales necesarias para "iterarlo" no compensan la sobrecarga de la pila.

[⬅️ Volver a la Unidad II](./index.md)
