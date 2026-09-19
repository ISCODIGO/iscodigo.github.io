---
layout: default
title: "Ejercicios: Clases y Objetos en Java"
parent: "Unidad I: Introducción a Estructuras de Datos, Modelado y Algoritmos Básicos"
grand_parent: "ISC-211 Estructuras de Datos"
nav_order: 2
---

# Ejercicios de Repaso: Clases y Objetos en Java

Ejercicios para verificar el dominio de clases y objetos en Java como base para el diseño de ADTs. No se incluyen soluciones.

## 1. Conceptos básicos

1. Explica con tus palabras la diferencia entre una **clase** y un **objeto**, usando un ejemplo distinto al visto en clase.
2. ¿Qué diferencia hay entre una **variable de instancia** y una **variable local** dentro de un método?
3. ¿Para qué sirve la palabra reservada `this` en Java? Da un ejemplo donde sea necesaria (no opcional).
4. ¿Qué hace un **constructor**? ¿Qué pasa si una clase no define ningún constructor?
5. ¿Qué es la **sobrecarga de constructores** (constructor overloading)? Explica un caso donde sea útil.

## 2. Encapsulamiento

6. ¿Qué significa declarar un atributo como `private`? ¿Por qué no se recomienda declarar atributos como `public`?
7. ¿Qué son los métodos **getter** y **setter** y qué relación tienen con el encapsulamiento?
8. Da un ejemplo de un `setter` que valide un dato antes de asignarlo (por ejemplo, que no permita una edad negativa).

## 3. Diseño de clases

9. Diseña (en pseudocódigo o Java) una clase `Punto` con atributos `x`, `y` (enteros), un constructor, getters/setters y un método `distancia(Punto otro)` que calcule la distancia euclidiana entre dos puntos.
10. Diseña una clase `CuentaBancaria` con atributos `saldo` y `titular`. Debe incluir métodos `depositar(monto)` y `retirar(monto)`, este último debe rechazar el retiro si el monto excede el saldo disponible.
11. A partir del ADT Fracción visto en clase, escribe la clase `Fraccion` en Java: atributos `num` y `den`, constructor que valide `den != 0` y llame a un método `simplificar()`, y los métodos `sumar(Fraccion otra)` e `imprimir()`.
12. A partir del ADT Arreglo visto en clase, escribe la clase `ArregloEnteros` en Java: atributos `datos` (arreglo de tamaño fijo), `tam` y `MAX`, con métodos `insertar(int valor)`, `borrar()` e `imprimir()`.

## 4. Objetos y memoria

13. ¿Qué diferencia hay entre comparar dos objetos con `==` y comparar su contenido con `.equals()`? Ilustra con un ejemplo de dos objetos `Fraccion` que representan el mismo valor.
14. Si tienes `Punto a = new Punto(1, 2);` y luego `Punto b = a;`, ¿qué ocurre si modificas un atributo de `b`? Explica por qué.

## 5. Relación con ADTs

15. Completa la siguiente tabla relacionando los conceptos de ADT con su equivalente en Java:

    | Concepto ADT | Equivalente en Java |
    |---|---|
    | ADT | ? |
    | Atributos | ? |
    | Operaciones | ? |
    | Instancia del ADT | ? |
    | Inicializador | ? |

16. Explica por qué encapsular los atributos como `private` en una clase Java es indispensable para que esa clase cumpla realmente con la definición de ADT vista en clase.

[⬅️ Volver a Unidad I](./index.md)
