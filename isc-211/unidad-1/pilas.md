---
layout: post
title: "Pilas (Stacks)"
parent: "Unidad I: Introducción a Estructuras de Datos, Modelado y Algoritmos Básicos"
grand_parent: "ISC-211 Estructuras de Datos"
nav_order: 8
---

Resumen basado en Goodrich, Tamassia y Goldwasser, *Data Structures and Algorithms in Java* (6.ª ed.): sección 6.1 (Pilas).

## ¿Qué es una pila?

Una **pila** (*stack*) es una colección de objetos que se insertan y eliminan según el principio **LIFO** (*last-in, first-out*): el último en entrar es el primero en salir. Se puede insertar en cualquier momento, pero solo se puede acceder o eliminar el elemento insertado más recientemente, que está en el **tope** (*top*) de la pila.

El nombre viene de una pila de platos en un dispensador de cafetería: se **apila** (*push*) un plato encima y se **desapila** (*pop*) el de arriba.

Ejemplos de uso:

- **Navegador web**: guarda las direcciones visitadas en una pila; el botón "atrás" desapila la última.
- **Editor de texto**: el mecanismo de "deshacer" guarda los cambios recientes en una pila.

## El ADT Pila

Operaciones de actualización:

| Método | Descripción |
|---|---|
| `push(e)` | agrega `e` en el tope de la pila |
| `pop()` | elimina y devuelve el elemento del tope (o `null` si está vacía) |

Operaciones de consulta:

| Método | Descripción |
|---|---|
| `top()` | devuelve el elemento del tope **sin eliminarlo** (o `null` si está vacía) |
| `size()` | devuelve la cantidad de elementos |
| `isEmpty()` | `true` si la pila está vacía |

Ejemplo del libro sobre una pila de enteros inicialmente vacía (el tope es el último elemento de la derecha):

| Operación | Devuelve | Contenido |
|---|---|---|
| `push(5)` | – | (5) |
| `push(3)` | – | (5, 3) |
| `size()` | 2 | (5, 3) |
| `pop()` | 3 | (5) |
| `isEmpty()` | false | (5) |
| `pop()` | 5 | () |
| `isEmpty()` | true | () |
| `pop()` | null | () |
| `push(7)` | – | (7) |
| `push(9)` | – | (7, 9) |
| `top()` | 9 | (7, 9) |
| `push(4)` | – | (7, 9, 4) |
| `size()` | 3 | (7, 9, 4) |
| `pop()` | 4 | (7, 9) |
| `push(6)` | – | (7, 9, 6) |
| `push(8)` | – | (7, 9, 6, 8) |
| `pop()` | 8 | (7, 9, 6) |

### Interfaz en Java

La API del ADT se define como una interfaz genérica, de modo que la pila puede guardar elementos de cualquier tipo por referencia (`Stack<Integer>`, `Stack<String>`, etc.):

```java
public interface Stack<E> {
    int size();         // número de elementos
    boolean isEmpty();  // ¿está vacía?
    void push(E e);     // inserta en el tope
    E top();            // devuelve el tope sin eliminarlo (null si está vacía)
    E pop();            // elimina y devuelve el tope (null si está vacía)
}
```

### La clase `java.util.Stack`

Java incluye desde su primera versión la clase `java.util.Stack`, pero se mantiene solo por razones históricas y su documentación recomienda **no usarla**; en su lugar se usa una cola doble (*deque*, sección 6.3 del libro). Sus diferencias con el ADT del libro:

| ADT del libro | `java.util.Stack` |
|---|---|
| `size()` | `size()` |
| `isEmpty()` | `empty()` |
| `push(e)` | `push(e)` |
| `pop()` | `pop()` |
| `top()` | `peek()` |

Además, `pop` y `peek` de `java.util.Stack` lanzan `EmptyStackException` si la pila está vacía, en lugar de devolver `null`.

## Implementación con arreglo

Los elementos se guardan en un arreglo `data` de capacidad fija `N`. La base de la pila está en `data[0]` y el tope en `data[t]`, donde `t` es el índice del tope. La pila vacía tiene `t = -1`, así que el tamaño siempre es `t + 1`.

```
data:  [A, B, C, D, E, _, _, _]
        0           t       N-1
```

```java
public class ArrayStack<E> implements Stack<E> {
    public static final int CAPACITY = 1000; // capacidad por defecto
    private E[] data;                        // arreglo genérico de almacenamiento
    private int t = -1;                      // índice del tope

    public ArrayStack() { this(CAPACITY); }
    public ArrayStack(int capacity) {
        data = (E[]) new Object[capacity];
    }

    public int size() { return t + 1; }
    public boolean isEmpty() { return t == -1; }

    public void push(E e) throws IllegalStateException {
        if (size() == data.length) throw new IllegalStateException("La pila está llena");
        data[++t] = e;          // incrementa t antes de guardar
    }

    public E top() {
        if (isEmpty()) return null;
        return data[t];
    }

    public E pop() {
        if (isEmpty()) return null;
        E answer = data[t];
        data[t] = null;         // ayuda al recolector de basura
        t--;
        return answer;
    }
}
```

### Análisis

| Método | Tiempo |
|---|---|
| `size` | O(1) |
| `isEmpty` | O(1) |
| `top` | O(1) |
| `push` | O(1) |
| `pop` | O(1) |

El espacio es **O(N)**, donde `N` es la capacidad del arreglo, sin importar cuántos elementos `n ≤ N` haya realmente.

**Desventaja:** la capacidad es fija. Si se reserva de más se desperdicia memoria, y si la pila se llena, `push` lanza `IllegalStateException`. Esto se resuelve con una lista enlazada (abajo) o con un arreglo dinámico (ver [Arreglos e Iteradores](./arreglos-e-iteradores.md)).

### ¿Por qué `data[t] = null` en `pop`?

No es necesario para que la pila funcione, pero si la celda siguiera apuntando al elemento eliminado, el **recolector de basura** de Java no podría liberar ese objeto aunque ya nadie más lo use (ver [Referencias a Objetos y Listas](./referencias-y-listas.md)).

### Ejemplo de uso

```java
Stack<Integer> S = new ArrayStack<>();  // contenido: ()
S.push(5);                              // (5)
S.push(3);                              // (5, 3)
System.out.println(S.size());           // (5, 3)     imprime 2
System.out.println(S.pop());            // (5)        imprime 3
System.out.println(S.isEmpty());        // (5)        imprime false
System.out.println(S.pop());            // ()         imprime 5
System.out.println(S.pop());            // ()         imprime null
S.push(7);                              // (7)
S.push(9);                              // (7, 9)
System.out.println(S.top());            // (7, 9)     imprime 9
```

## Implementación con lista enlazada

Una lista simplemente enlazada (sección 3.2 del libro) no tiene límite de capacidad y usa memoria proporcional a los elementos que contiene. Como en esa lista solo se puede insertar y eliminar en tiempo constante **al inicio**, el tope de la pila se coloca al frente de la lista.

Se usa el **patrón adaptador** (*adapter*): una clase nueva que guarda una instancia de una clase existente como campo oculto e implementa sus métodos usando los de esa instancia.

| Método de la pila | Método de `SinglyLinkedList` |
|---|---|
| `size()` | `list.size()` |
| `isEmpty()` | `list.isEmpty()` |
| `push(e)` | `list.addFirst(e)` |
| `pop()` | `list.removeFirst()` |
| `top()` | `list.first()` |

```java
public class LinkedStack<E> implements Stack<E> {
    private SinglyLinkedList<E> list = new SinglyLinkedList<>();
    public LinkedStack() { }
    public int size() { return list.size(); }
    public boolean isEmpty() { return list.isEmpty(); }
    public void push(E element) { list.addFirst(element); }
    public E top() { return list.first(); }
    public E pop() { return list.removeFirst(); }
}
```

Todos los métodos son **O(1)**.

## Aplicaciones

### Invertir un arreglo

Por el principio LIFO, si se apilan 1, 2 y 3, se desapilan en orden 3, 2, 1. Basta con apilar todos los elementos del arreglo y luego desapilarlos sobrescribiendo el arreglo desde el inicio:

```java
public static <E> void reverse(E[] a) {
    Stack<E> buffer = new ArrayStack<>(a.length);
    for (int i = 0; i < a.length; i++)
        buffer.push(a[i]);
    for (int i = 0; i < a.length; i++)
        a[i] = buffer.pop();
}
```

```
a = [4, 8, 15, 16, 23, 42]   →   a = [42, 23, 16, 15, 8, 4]
```

### Verificar paréntesis balanceados

En una expresión, cada símbolo de apertura `(`, `{`, `[` debe cerrarse con su símbolo correspondiente `)`, `}`, `]`, en el orden correcto.

| Expresión | ¿Correcta? |
|---|---|
| `()(()){([()])}` | Sí |
| `((()(()){([()])}))` | Sí |
| `)(()){([()])}` | No |
| `({[])}` | No |
| `(` | No |

**Algoritmo:** se recorre la expresión de izquierda a derecha.

1. Si es un símbolo de apertura, se apila.
2. Si es de cierre, se desapila (si la pila está vacía, es incorrecta) y se verifica que ambos formen pareja.
3. Al terminar, la expresión es correcta solo si la pila quedó vacía.

```java
public static boolean isMatched(String expression) {
    final String opening = "({[";   // símbolos de apertura
    final String closing = ")}]";   // cierres correspondientes
    Stack<Character> buffer = new LinkedStack<>();
    for (char c : expression.toCharArray()) {
        if (opening.indexOf(c) != -1)          // apertura
            buffer.push(c);
        else if (closing.indexOf(c) != -1) {   // cierre
            if (buffer.isEmpty())
                return false;                  // no hay con qué emparejar
            if (closing.indexOf(c) != opening.indexOf(buffer.pop()))
                return false;                  // no forman pareja
        }
    }
    return buffer.isEmpty();                   // ¿se cerraron todos?
}
```

Con una expresión de longitud `n` se hacen como máximo `n` llamadas a `push` y `n` a `pop`, así que el algoritmo es **O(n)**.

### Verificar etiquetas HTML

La misma idea sirve para validar que en un documento HTML o XML cada etiqueta de apertura `<nombre>` tenga su cierre `</nombre>`: las etiquetas de apertura se apilan y, al encontrar una de cierre, se desapila y se compara.

```java
public static boolean isHTMLMatched(String html) {
    Stack<String> buffer = new LinkedStack<>();
    int j = html.indexOf('<');                    // primer '<'
    while (j != -1) {
        int k = html.indexOf('>', j + 1);         // siguiente '>'
        if (k == -1)
            return false;                         // etiqueta inválida
        String tag = html.substring(j + 1, k);    // quita < >
        if (!tag.startsWith("/"))                 // etiqueta de apertura
            buffer.push(tag);
        else {                                    // etiqueta de cierre
            if (buffer.isEmpty())
                return false;
            if (!tag.substring(1).equals(buffer.pop()))
                return false;                     // no coinciden
        }
        j = html.indexOf('<', k + 1);             // siguiente '<'
    }
    return buffer.isEmpty();
}
```

[⬅️ Volver a la Unidad I](./index.md)
