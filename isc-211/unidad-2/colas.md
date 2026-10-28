---
layout: post
title: "Colas (Queues) y Deques"
parent: "Unidad II: Recursión, Listas, Genéricos, Pilas y Colas"
grand_parent: "ISC-211 Estructuras de Datos"
nav_order: 5
---

Resumen basado en el libro de texto (de la Cueva et al., *Estructura de datos y algoritmos fundamentales*): secciones 8.3 (Cola) y 8.4 (Deque). El libro presenta el código en C++; aquí se muestra en Java, reutilizando las clases de [Listas Enlazadas](./listas-enlazadas.md).

## ¿Qué es una cola?

Una **cola** o **fila** (*queue*) es una estructura de datos lineal en la que los elementos **entran por un lado** y **salen por el lado contrario**. Es una estructura **FIFO** (*first-in, first-out*): el primero en entrar es el primero en salir.

Ejemplo: la fila para pagar en un supermercado; los primeros clientes en llegar son los primeros en ser atendidos.

- **Frente** (*front*): el siguiente elemento que saldría de la cola.
- **Posterior** (*rear*): el último elemento que entró a la cola.

```
 sale ←  [ 5 | 3 | 8 | 1 ]  ← entra
          ↑           ↑
        frente     posterior
```

Comparación con la [pila](./pilas.md):

| | Pila | Cola |
|---|---|---|
| Principio | LIFO | FIFO |
| Inserta por | el tope | el posterior |
| Elimina por | el tope (mismo lado) | el frente (lado contrario) |

## El ADT Cola

Acciones principales:

| Método | Descripción |
|---|---|
| `enqueue(dato)` | inserta el dato en el posterior de la cola |
| `dequeue()` | saca el dato que está en el frente |

Acciones auxiliares comunes:

| Método | Descripción |
|---|---|
| `getFrente()` | devuelve el elemento del frente **sin eliminarlo** |
| `colaVacia()` | `true` si la cola está vacía |
| `colaLlena()` | `true` si la cola está llena (solo cuando es de tamaño fijo) |

El libro define el ADT así:

```
Cola(T)
  frente, posterior
  espacioCola: arreglo o lista ligada que guarda los datos de tipo T
  Constructor: frente y posterior en nulo (cola vacía)
  enqueue(dato), dequeue(), getFrente(), colaVacia()
```

Ejemplo sobre una cola de enteros inicialmente vacía (el frente está a la izquierda):

| Operación | Devuelve | Contenido |
|---|---|---|
| `enqueue(5)` | – | (5) |
| `enqueue(3)` | – | (5, 3) |
| `enqueue(8)` | – | (5, 3, 8) |
| `getFrente()` | 5 | (5, 3, 8) |
| `dequeue()` | 5 | (3, 8) |
| `enqueue(1)` | – | (3, 8, 1) |
| `dequeue()` | 3 | (8, 1) |
| `colaVacia()` | false | (8, 1) |

### Interfaz en Java

```java
public interface Queue<E> {
    boolean colaVacia();    // ¿está vacía?
    void enqueue(E dato);   // inserta en el posterior
    E getFrente();          // devuelve el frente sin eliminarlo (null si está vacía)
    E dequeue();            // elimina y devuelve el frente (null si está vacía)
}
```

## Implementación con arreglo

Igual que la pila, la cola puede guardar sus datos (`espacioCola`) en un arreglo de tamaño fijo `MAX`, por lo que hay que verificar que no esté llena antes de insertar.

### El problema del arreglo lineal

Cada `enqueue` mueve `posterior` una casilla a la derecha y cada `dequeue` mueve `frente` también a la derecha. Las casillas de la izquierda quedan sin usar:

```
a) inicial          [A, B, C, D, E, _, _, _]   frente=0, posterior=4
b) enqueue(F)       [A, B, C, D, E, F, _, _]   frente=0, posterior=5
c) dequeue() → A    [_, B, C, D, E, F, _, _]   frente=1, posterior=5
d) dequeue() → B    [_, _, C, D, E, F, _, _]   frente=2, posterior=5
```

Si se sigue así, `posterior` llega al final del arreglo e indica que **no hay espacio**, aunque en realidad sí lo hay a la izquierda.

### Cola circular

La solución es usar el arreglo **como si fuera circular**: el siguiente de la última casilla es la primera. Se logra con el **módulo** del índice sobre el tamaño del arreglo:

```java
siguiente = (indice + 1) % MAX;
```

```
        posterior
            ↓
   [ G | H | _ | _ | C | D | E | F ]
                     ↑
                   frente
```

Con solo `frente` y `posterior` es difícil distinguir si la cola está **llena** o **vacía** (en ambos casos los índices pueden coincidir). El libro sugiere agregar información extra, como el **número de elementos**:

```java
public class ArrayQueue<E> implements Queue<E> {
    private E[] data;        // espacioCola
    private int frente = 0;  // índice del frente
    private int n = 0;       // número de elementos

    public ArrayQueue(int max) {
        data = (E[]) new Object[max];
    }

    public boolean colaVacia() { return n == 0; }
    public boolean colaLlena() { return n == data.length; }

    public void enqueue(E dato) throws IllegalStateException {
        if (colaLlena()) throw new IllegalStateException("La cola está llena");
        int posterior = (frente + n) % data.length;  // casilla libre siguiente
        data[posterior] = dato;
        n++;
    }

    public E getFrente() {
        if (colaVacia()) return null;
        return data[frente];
    }

    public E dequeue() {
        if (colaVacia()) return null;
        E answer = data[frente];
        data[frente] = null;                    // ayuda al recolector de basura
        frente = (frente + 1) % data.length;    // avanza circularmente
        n--;
        return answer;
    }
}
```

Todas las operaciones son **O(1)**, pero la capacidad sigue siendo fija. Por eso el libro concluye que la implementación con lista ligada "parece ser una mejor opción".

## Implementación con lista ligada

Se reutiliza la clase lista y cada operación de la cola es una **envoltura** (*wrap*) de una operación de la lista:

| Cola | Lista |
|---|---|
| `enqueue(dato)` | insertar al **final** (`addLast`) |
| `dequeue()` | eliminar del **inicio** (`removeFirst`) |
| `getFrente()` | obtener el primero (`first`) |
| `colaVacia()` | lista vacía (`isEmpty`) |

```java
public class LinkedQueue<E> implements Queue<E> {
    private SinglyLinkedList<E> list = new SinglyLinkedList<>();
    public boolean colaVacia() { return list.isEmpty(); }
    public void enqueue(E dato) { list.addLast(dato); }
    public E getFrente() { return list.first(); }
    public E dequeue() { return list.removeFirst(); }
}
```

Como `SinglyLinkedList` guarda una referencia a la cola de la lista (`tail`), insertar al final también es **O(1)**. No hay límite de capacidad, así que no se necesita `colaLlena()`.

> ¿Por qué no insertar al inicio y eliminar del final? En una lista simplemente enlazada, eliminar el último nodo es **O(n)**, porque hay que recorrerla para encontrar al penúltimo.

## Deque

Una **deque** (*double-ended queue*, "cola doblemente terminada") generaliza la cola: se puede **insertar y eliminar por cualquiera de sus dos extremos**. Es muy versátil: con ella se implementan fácilmente pilas y colas.

La forma más sencilla de implementarla es con una [lista doblemente enlazada](./listas-enlazadas.md) que tenga una referencia al primer nodo (**frente**) y otra al último (**posterior**). Cada nodo tiene una referencia a su previo (`prev`) y a su siguiente (`next`).

```
 null ← [A] ⇄ [B] ⇄ [C] ⇄ [D] → null
         ↑                 ↑
       frente          posterior
```

### Operaciones

| Método | Descripción | Tiempo |
|---|---|---|
| `insertarFrente(dato)` | inserta al frente | O(1) |
| `insertarPosterior(dato)` | inserta en el posterior | O(1) |
| `eliminarFrente()` | elimina del frente | O(1) |
| `eliminarPosterior()` | elimina del posterior | O(1) |
| `getFrente()` | valor del frente | O(1) |
| `getPosterior()` | valor del posterior | O(1) |
| `dequeVacia()` | ¿está vacía? | O(1) |

Insertar en el posterior es **O(1)** gracias a la referencia `posterior`; en una lista doblemente enlazada sin esa referencia habría que recorrerla toda (**O(n)**).

### Insertar al frente

Dos casos:

- **Deque vacía:** se crea el nodo y `frente` y `posterior` apuntan a él.
- **Deque no vacía:**
  1. Se crea el nodo nuevo.
  2. El `next` del nodo nuevo apunta a `frente`.
  3. El `prev` de `frente` apunta al nodo nuevo.
  4. `frente` apunta al nodo nuevo.

`insertarPosterior` es igual, cambiando `frente` por `posterior` y `next` por `prev`.

### Eliminar del frente

Tres casos (el libro devuelve un booleano que indica si se pudo eliminar):

- **Deque vacía:** devuelve `false`.
- **Un solo elemento:** `frente` y `posterior` se hacen `null`; devuelve `true`.
- **Más de un elemento:**
  1. `frente` avanza a su `next`.
  2. El `prev` del nuevo `frente` se hace `null` (ya no tiene previo).
  3. Devuelve `true`.

`eliminarPosterior` es igual, cambiando `frente` por `posterior` y `next` por `prev`.

### Implementación en Java

```java
public class Deque<E> {
    private static class Node<E> {
        E info;
        Node<E> prev, next;
        Node(E info) { this.info = info; }
    }

    private Node<E> frente = null;
    private Node<E> posterior = null;

    public boolean dequeVacia() { return frente == null; }

    // Los getters no validan: quien los usa debe verificar antes que no esté vacía.
    public E getFrente() { return frente.info; }
    public E getPosterior() { return posterior.info; }

    public void insertarFrente(E dato) {
        Node<E> nuevo = new Node<>(dato);
        if (dequeVacia()) {
            frente = posterior = nuevo;
        } else {
            nuevo.next = frente;
            frente.prev = nuevo;
            frente = nuevo;
        }
    }

    public void insertarPosterior(E dato) {
        Node<E> nuevo = new Node<>(dato);
        if (dequeVacia()) {
            frente = posterior = nuevo;
        } else {
            nuevo.prev = posterior;
            posterior.next = nuevo;
            posterior = nuevo;
        }
    }

    public boolean eliminarFrente() {
        if (dequeVacia()) return false;
        if (frente == posterior) {          // un solo elemento
            frente = posterior = null;
        } else {
            frente = frente.next;
            frente.prev = null;
        }
        return true;
    }

    public boolean eliminarPosterior() {
        if (dequeVacia()) return false;
        if (frente == posterior) {          // un solo elemento
            frente = posterior = null;
        } else {
            posterior = posterior.prev;
            posterior.next = null;
        }
        return true;
    }
}
```

### Pilas y colas con una deque

Con una deque, los métodos de la pila y de la cola se vuelven **envolturas**:

| Pila (entra y sale por el frente) | Deque |
|---|---|
| `push(dato)` | `insertarFrente(dato)` |
| `pop()` | `eliminarFrente()` |
| `getTop()` | `getFrente()` |
| `pilaVacia()` | `dequeVacia()` |

| Cola (entra por el posterior, sale por el frente) | Deque |
|---|---|
| `enqueue(dato)` | `insertarPosterior(dato)` |
| `dequeue()` | `eliminarFrente()` |
| `getFrente()` | `getFrente()` |
| `colaVacia()` | `dequeVacia()` |

También funciona con los lados invertidos (pila por el posterior; cola entrando por el frente y saliendo por el posterior): el resultado es el mismo.

### En la biblioteca de Java

Java ya incluye estas estructuras en `java.util`. La interfaz `Deque` (implementada por `ArrayDeque` y `LinkedList`) sirve como pila, cola o deque, y es la que la documentación recomienda en lugar de `java.util.Stack`:

| Deque del libro | `java.util.Deque` |
|---|---|
| `insertarFrente(e)` | `addFirst(e)` / `push(e)` |
| `insertarPosterior(e)` | `addLast(e)` / `offer(e)` |
| `eliminarFrente()` | `pollFirst()` / `poll()` / `pop()` |
| `eliminarPosterior()` | `pollLast()` |
| `getFrente()` | `peekFirst()` / `peek()` |
| `getPosterior()` | `peekLast()` |
| `dequeVacia()` | `isEmpty()` |

```java
Deque<Integer> cola = new ArrayDeque<>();
cola.offer(5);                    // (5)
cola.offer(3);                    // (5, 3)
System.out.println(cola.poll());  // (3)       imprime 5

Deque<Integer> pila = new ArrayDeque<>();
pila.push(5);                     // (5)
pila.push(3);                     // (3, 5)    el tope a la izquierda
System.out.println(pila.pop());   // (5)       imprime 3
```

## Ejercicios (del libro)

1. Escriba la pila que resulta en cada paso al hacer, partiendo de una pila de enteros vacía: `push(9)`, `push(2)`, `pop()`, `push(4)`, `push(7)`, `pop()`, `pop()`.
2. Para el ejercicio 1, ¿qué devuelve `getTop()` si se invoca después de a) `push(4)`; b) el último `pop()`?
3. Escriba la cola que resulta en cada paso, partiendo de una cola de enteros vacía: `enqueue(0)`, `enqueue(5)`, `enqueue(2)`, `dequeue()`, `dequeue()`, `enqueue(0)`, `enqueue(7)`.
4. Para el ejercicio 3, ¿qué devuelven `getFrente()` y `getPosterior()` después de a) el segundo `enqueue(0)`; b) el primer `dequeue()`; c) `enqueue(7)`?

Programación:

1. Implemente una pila utilizando una deque.
2. Implemente una cola utilizando una deque.
3. Implemente una pila con nodos enlazados, sin usar la clase lista.
4. Use `java.util.ArrayDeque` para comprobar sus respuestas a los ejercicios 1 a 4.

[⬅️ Volver a la Unidad II](./index.md)
