---
layout: post
title: "Tipos Genéricos"
parent: "Unidad I: Introducción a Estructuras de Datos, Modelado y Algoritmos Básicos"
grand_parent: "ISC-211 Estructuras de Datos"
nav_order: 7
---

Resumen basado en Goodrich, Tamassia y Goldwasser, *Data Structures and Algorithms in Java* (6.ª ed.): sección 2.5.2 (Genéricos).

En las secciones anteriores ya aparecieron tipos como `ArrayList<E>`, `List<E>` e `Iterator<E>`. Aquí se explica qué significa esa `<E>` antes de usarla para construir la pila.

## ¿Por qué tipos genéricos?

Una estructura de datos debe poder guardar elementos de **cualquier tipo**: una pila de enteros, una lista de cadenas, una cola de clientes. No tiene sentido escribir `IntStack`, `StringStack` y `ClienteStack` con el mismo código.

Antes de Java 5 la solución era usar `Object`, ya que toda clase hereda de él:

```java
public class ObjectPair {
    private Object first;
    private Object second;

    public ObjectPair(Object a, Object b) { first = a; second = b; }
    public Object getFirst() { return first; }
    public Object getSecond() { return second; }
}
```

Esto funciona, pero tiene dos problemas:

```java
ObjectPair bid = new ObjectPair("ORCL", 32.07);
String stock = (String) bid.getFirst();   // cast obligatorio
Integer x = (Integer) bid.getSecond();    // compila, pero falla en ejecución:
                                          // ClassCastException (es un Double)
```

1. Hay que hacer **cast** cada vez que se lee un elemento.
2. Los errores de tipo **no se detectan al compilar**, sino al ejecutar.

## Clases genéricas

Un **tipo genérico** es una clase o interfaz con uno o más **parámetros de tipo** entre `< >`. El parámetro (por convención una letra mayúscula: `T`, `E`, `K`, `V`) se usa dentro de la clase como si fuera un tipo cualquiera:

```java
public class Pair<A, B> {
    private A first;
    private B second;

    public Pair(A a, B b) { first = a; second = b; }
    public A getFirst() { return first; }
    public B getSecond() { return second; }
}
```

Al crear un objeto se indica el **tipo real** de cada parámetro:

```java
Pair<String, Double> bid = new Pair<>("ORCL", 32.07);
String stock = bid.getFirst();      // sin cast
double price = bid.getSecond();     // sin cast (unboxing automático)
Integer x = bid.getSecond();        // ERROR de compilación
```

El operador `<>` (*diamante*) le pide al compilador que deduzca los tipos a partir de la declaración.

| Convención | Significado |
|---|---|
| `E` | Elemento de una colección (`List<E>`, `Stack<E>`) |
| `T` | Tipo cualquiera |
| `K`, `V` | Llave y valor (`Map<K, V>`) |

## Interfaces genéricas

Las interfaces también pueden ser genéricas. Así se define el ADT Pila del curso:

```java
public interface Stack<E> {
    int size();
    boolean isEmpty();
    void push(E e);
    E top();
    E pop();
}
```

Y una clase que la implementa conserva el parámetro:

```java
public class ArrayStack<E> implements Stack<E> { ... }
```

## Métodos genéricos

Un método puede declarar su propio parámetro de tipo, colocándolo **antes del tipo de retorno**, aunque la clase no sea genérica:

```java
public static <T> void reverse(T[] data) {
    int low = 0, high = data.length - 1;
    while (low < high) {
        T temp = data[low];
        data[low++] = data[high];
        data[high--] = temp;
    }
}
```

```java
String[] nombres = {"Ana", "Luis", "Eva"};
Integer[] numeros = {1, 2, 3};
reverse(nombres);   // T = String
reverse(numeros);   // T = Integer
```

## Restricciones

### Solo tipos referencia

Los parámetros de tipo no aceptan tipos primitivos. Se usan las clases envolventes (*wrapper*) y Java convierte automáticamente (*autoboxing* / *unboxing*):

```java
Stack<int> s;         // ERROR
Stack<Integer> s;     // correcto
s.push(5);            // autoboxing: int → Integer
int x = s.pop();      // unboxing: Integer → int
```

| Primitivo | Envolvente |
|---|---|
| `int` | `Integer` |
| `double` | `Double` |
| `char` | `Character` |
| `boolean` | `Boolean` |

### No se puede crear un arreglo genérico

Java borra los parámetros de tipo al compilar (*type erasure*): en tiempo de ejecución `E` no existe, así que no se puede escribir `new E[n]`. La solución usada en las implementaciones del curso es crear un arreglo de `Object` y hacer cast:

```java
public ArrayStack(int capacity) {
    data = (E[]) new Object[capacity];   // el compilador emite una advertencia
}
```

El cast es seguro porque el arreglo es **privado** y la clase solo guarda en él elementos de tipo `E`.

## Tipos acotados

A veces el algoritmo necesita que el tipo tenga cierta capacidad, por ejemplo poder compararse. Se restringe el parámetro con `extends`:

```java
public static <T extends Comparable<T>> T max(T[] data) {
    T best = data[0];
    for (T x : data)
        if (x.compareTo(best) > 0)
            best = x;
    return best;
}
```

`max` acepta `Integer[]` o `String[]` (ambos implementan `Comparable`), pero no un arreglo de una clase que no se pueda comparar. Esto se usará en ordenamiento, árboles binarios de búsqueda y colas de prioridad.

## Resumen

- Los genéricos permiten escribir **una sola estructura** para cualquier tipo de elemento.
- Eliminan los casts y detectan errores de tipo **al compilar**.
- Se aplican a clases, interfaces y métodos.
- Solo aceptan tipos referencia; los primitivos se envuelven automáticamente.
- No se puede hacer `new E[n]`; se usa `(E[]) new Object[n]`.
- `<T extends Comparable<T>>` restringe el tipo a los que se pueden comparar.

[⬅️ Volver a la Unidad I](./index.md)
