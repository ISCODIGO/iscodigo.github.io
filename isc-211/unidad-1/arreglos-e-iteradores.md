---
layout: post
title: "Arreglos e Iteradores"
parent: "Unidad I: Introducción a Estructuras de Datos, Modelado y Algoritmos Básicos"
grand_parent: "ISC-211 Estructuras de Datos"
nav_order: 5
---

Resumen basado en Goodrich, Tamassia y Goldwasser, *Data Structures and Algorithms in Java* (6.ª ed.): secciones 3.1 (Usando arreglos), 7.2 (Arreglos dinámicos) y 7.4 (Iteradores).

## Arreglos

Un **arreglo** es una estructura de datos concreta que guarda una secuencia de elementos del mismo tipo en celdas contiguas de memoria, a las que se accede mediante un **índice entero** que va de `0` a `n - 1`.

- El acceso a cualquier celda `A[i]` es **O(1)**.
- La **capacidad** (`A.length`) se fija al crearlo y no puede cambiar.
- Acceder fuera del rango lanza `ArrayIndexOutOfBoundsException`.

```java
int[] numeros = new int[10];          // 10 celdas inicializadas en 0
String[] dias = {"Lun", "Mar", "Mié"}; // inicialización literal
```

Es importante distinguir entre la **capacidad** del arreglo y el **número de elementos** realmente guardados. Por eso, las clases que usan arreglos suelen llevar un contador aparte (por ejemplo, `size`).

## Ejemplo: lista de compras

Una lista de compras guardada en un arreglo de tamaño fijo, con un contador `size` que indica cuántos productos hay.

```java
public class ListaCompras {
    private String[] items = new String[10]; // capacidad: 10
    private int size = 0;                    // productos guardados
}
```

### Insertar en una posición

Para insertar en el índice `i`, primero se **desplazan hacia la derecha** los elementos desde `i` hasta el final, y luego se coloca el nuevo en el hueco.

```
Insertar "Pan" en el índice 1:

antes:     [Leche, Huevos, Café, _, _]
desplazar: [Leche, _, Huevos, Café, _]
después:   [Leche, Pan, Huevos, Café, _]
```

```java
public void add(int i, String item) {
    if (size == items.length)
        throw new IllegalStateException("La lista está llena");
    for (int j = size; j > i; j--)
        items[j] = items[j - 1];  // desplazar a la derecha
    items[i] = item;
    size++;
}
```

### Eliminar de una posición

Para eliminar el índice `i`, se **desplazan hacia la izquierda** los elementos que están después de `i`, y la última celda se deja en `null`.

```
Eliminar el índice 1 ("Pan"):

antes:   [Leche, Pan, Huevos, Café, _]
después: [Leche, Huevos, Café, _, _]
```

```java
public String remove(int i) {
    if (i < 0 || i >= size)
        throw new IndexOutOfBoundsException("Índice inválido: " + i);
    String eliminado = items[i];
    for (int j = i; j < size - 1; j++)
        items[j] = items[j + 1];  // desplazar a la izquierda
    items[size - 1] = null;
    size--;
    return eliminado;
}
```

Ambas operaciones son **O(n)** en el peor caso (insertar o eliminar en el índice 0 obliga a mover todos los elementos). Agregar al final no desplaza nada, por eso es **O(1)**.

## Métodos útiles de `java.util.Arrays`

| Método | Descripción |
|---|---|
| `equals(A, B)` | `true` si ambos tienen los mismos elementos en el mismo orden |
| `fill(A, x)` | guarda `x` en todas las celdas |
| `copyOf(A, n)` | nuevo arreglo de tamaño `n` con los primeros elementos de `A` |
| `copyOfRange(A, s, t)` | nuevo arreglo con `A[s..t-1]` |
| `toString(A)` | representación como texto, p. ej. `[4, 5, 2]` |
| `sort(A)` | ordena de forma no decreciente |
| `binarySearch(A, x)` | busca `x` en un arreglo **ordenado** |

Para números pseudoaleatorios se usa `java.util.Random` (`nextInt(n)`, `nextDouble()`, `setSeed(s)`).

## Arreglos bidimensionales

En Java un arreglo bidimensional es un **arreglo de arreglos**: cada celda de un arreglo contiene otro arreglo. El primer índice suele ser la fila y el segundo la columna.

```java
int[][] data = new int[8][10]; // 8 filas, 10 columnas
data[3][5] = 100;
int filas = data.length;       // 8
int columnas = data[4].length; // 10
```

El libro lo ejemplifica con un tablero de **Gato (Tic-Tac-Toe)**: una matriz 3×3 de enteros donde `0` es vacío, `1` es X y `-1` es O. Un jugador gana si una fila, columna o diagonal suma `3` (X) o `-3` (O).

## Arreglos dinámicos

La capacidad fija del arreglo es su principal limitación. Un **arreglo dinámico** (como `java.util.ArrayList`) la resuelve así: cuando el arreglo se llena,

1. Se crea un arreglo nuevo `B` con mayor capacidad (normalmente el **doble**).
2. Se copian los elementos: `B[k] = A[k]`.
3. Se reemplaza `A` por `B`.
4. Se inserta el nuevo elemento.

```java
protected void resize(int capacity) {
    E[] temp = (E[]) new Object[capacity];
    for (int k = 0; k < size; k++)
        temp[k] = data[k];
    data = temp;
}
```

Copiar cuesta O(n), pero al **duplicar** la capacidad esto ocurre pocas veces. Con **análisis amortizado** se demuestra que una serie de `n` inserciones al final toma O(n) en total, es decir, **O(1) amortizado** por inserción. Si en lugar de duplicar se aumenta en una cantidad fija, el costo total sube a O(n²).

## Iteradores

Un **iterador** es un patrón de diseño que abstrae el proceso de recorrer una secuencia de elementos, uno a la vez, sin importar cómo están guardados. Java lo define con la interfaz `java.util.Iterator<E>`:

| Método | Descripción |
|---|---|
| `hasNext()` | `true` si quedan elementos por recorrer |
| `next()` | devuelve el siguiente elemento; lanza `NoSuchElementException` si no hay más |
| `remove()` | (opcional) elimina el último elemento devuelto por `next()`; si no se soporta lanza `UnsupportedOperationException` |

```java
Iterator<String> iter = lista.iterator();
while (iter.hasNext()) {
    String valor = iter.next();
    System.out.println(valor);
}
```

### La interfaz `Iterable` y el ciclo *for-each*

Un iterador solo sirve para **una pasada**: no se puede reiniciar. Por eso, las colecciones implementan la interfaz `Iterable<E>`, cuyo único método `iterator()` devuelve un **iterador nuevo** cada vez que se llama, lo que permite recorrer la colección varias veces (incluso de forma simultánea).

Cualquier objeto `Iterable` puede usarse en el ciclo *for-each*:

```java
for (String s : lista) {
    System.out.println(s);
}
```

que es una forma abreviada de:

```java
Iterator<String> iter = lista.iterator();
while (iter.hasNext()) {
    String s = iter.next();
    System.out.println(s);
}
```

Dentro de un *for-each* **no** se puede llamar a `remove()`. Para eliminar elementos mientras se recorre hay que usar el iterador de forma explícita:

```java
Iterator<Double> walk = data.iterator();
while (walk.hasNext())
    if (walk.next() < 0.0)
        walk.remove();  // elimina los negativos
```

### Estilos de implementación

| Estilo | Funcionamiento | Costo al crear | ¿Le afectan los cambios a la colección? |
|---|---|---|---|
| **Snapshot** | copia los elementos al crearse | O(n) tiempo y espacio | No |
| **Lazy** (perezoso) | recorre la estructura original a medida que se llama `next()` | O(1) | Sí |

Muchos iteradores de Java son *lazy* con comportamiento **fail-fast**: si la colección se modifica por fuera del iterador, lanzan `ConcurrentModificationException`.

### Ejemplo: iterador para un `ArrayList`

El iterador se implementa como una **clase interna** (no estática), así puede acceder a los campos privados de la lista (`data`, `size`). Guarda el índice `j` del siguiente elemento a devolver.

```java
public class ArrayList<E> implements Iterable<E> {
    private E[] data;
    private int size = 0;
    // ... resto de la implementación ...

    private class ArrayIterator implements Iterator<E> {
        private int j = 0;                 // índice del siguiente elemento
        private boolean removable = false; // ¿se puede llamar a remove()?

        public boolean hasNext() { return j < size; }

        public E next() throws NoSuchElementException {
            if (j == size) throw new NoSuchElementException("No hay más elementos");
            removable = true;
            return data[j++];
        }

        public void remove() throws IllegalStateException {
            if (!removable) throw new IllegalStateException("Nada que eliminar");
            ArrayList.this.remove(j - 1); // el último devuelto
            j--;                          // el siguiente se desplazó a la izquierda
            removable = false;
        }
    }

    public Iterator<E> iterator() {
        return new ArrayIterator();
    }
}
```

## Resumen

| Operación | Arreglo | Arreglo dinámico |
|---|---|---|
| Acceso `A[i]` | O(1) | O(1) |
| Insertar/eliminar al final | O(1) (si hay espacio) | O(1) amortizado |
| Insertar/eliminar en posición `i` | O(n) | O(n) |
| Capacidad | fija | crece automáticamente |

[⬅️ Volver a la Unidad I](./index.md)
