---
layout: post
title: "Referencias a Objetos y Listas"
parent: "Unidad I: Introducción a Estructuras de Datos, Modelado y Algoritmos Básicos"
grand_parent: "ISC-211 Estructuras de Datos"
nav_order: 6
---

Resumen basado en Goodrich, Tamassia y Goldwasser, *Data Structures and Algorithms in Java* (6.ª ed.): secciones 1.2–1.3 (Clases, objetos y arreglos), 3.5–3.6 (Equivalencia y clonación), 7.1 (El ADT Lista) y 7.5 (Java Collections Framework).

## Referencias a objetos

En Java las clases son **tipos por referencia**. Una variable de un tipo clase no guarda el objeto en sí: guarda su **dirección en memoria** (una referencia), o el valor especial `null` si no apunta a ningún objeto.

```java
Counter c;              // declara la variable, pero NO crea ningún objeto (c es null)
c = new Counter();      // new crea el objeto y devuelve su referencia
```

Al ejecutar `new` ocurren tres cosas:

1. Se reserva memoria para el objeto y sus variables de instancia toman valores por defecto (`null` para referencias, `0` para números, `false` para `boolean`).
2. Se llama al constructor con los parámetros indicados.
3. `new` devuelve la referencia (dirección) al objeto creado.

El libro compara una referencia con un **control remoto**: la variable no es el televisor, solo el control que lo maneja. Una referencia `null` es un portacontrol vacío, y usar el operador punto sobre ella lanza `NullPointerException`.

### Alias

Varias variables pueden referirse al **mismo objeto**. Si se modifica el objeto a través de una, el cambio se ve desde todas.

```java
Counter d = new Counter(5);
Counter e = d;     // NO crea otro Counter: e y d son alias del mismo objeto
e.increment(2);    // d.getCount() ahora también devuelve 7
```

### Comparar referencias

| Expresión | Significado |
|---|---|
| `a == b` | `true` si `a` y `b` apuntan al **mismo objeto** (o ambos son `null`) |
| `a.equals(b)` | `true` si los objetos se consideran **equivalentes** según su clase |

### Los arreglos también son referencias

Un arreglo es un objeto, y su variable es una referencia. Por eso:

- Un arreglo de un tipo por referencia (p. ej. `String[]`) creado con `new` tiene todas sus celdas en `null`; cada celda guarda una **referencia** a un objeto, no el objeto.
- Asignar un arreglo a otra variable **no lo copia**, solo crea un alias:

```java
int[] data = {2, 3, 5, 7, 11};
int[] backup = data;          // ¡cuidado! no es una copia, es el mismo arreglo
int[] copia = data.clone();   // arreglo nuevo e independiente
```

- Para comparar arreglos, `a == b` y `a.equals(b)` solo dicen si son el mismo arreglo. Para comparar el contenido se usa `Arrays.equals(a, b)` (o `Arrays.deepEquals(a, b)` en arreglos bidimensionales).

### Copia superficial y copia profunda

Si el arreglo guarda objetos, `clone()` hace una **copia superficial** (*shallow copy*): el arreglo es nuevo, pero sus celdas apuntan a los **mismos objetos** que el original. Para una **copia profunda** (*deep copy*) hay que clonar cada elemento:

```java
Person[] guests = contacts.clone();   // copia superficial: mismos objetos Person

Person[] guests2 = new Person[contacts.length];
for (int k = 0; k < contacts.length; k++)
    guests2[k] = (Person) contacts[k].clone();  // copia profunda (Person debe ser Cloneable)
```

## El ADT Lista

Una **lista** es una secuencia lineal de elementos donde se puede insertar, consultar o eliminar en **cualquier posición** usando un índice. El índice de un elemento es la cantidad de elementos que tiene antes, así que va de `0` a `n - 1`. Java la define en la interfaz `java.util.List`; el libro usa esta versión simplificada:

```java
public interface List<E> {
    int size();                                       // número de elementos
    boolean isEmpty();                                // ¿está vacía?
    E get(int i) throws IndexOutOfBoundsException;    // devuelve el elemento en i
    E set(int i, E e) throws IndexOutOfBoundsException; // reemplaza el elemento en i y devuelve el anterior
    void add(int i, E e) throws IndexOutOfBoundsException; // inserta e en i, recorre los siguientes
    E remove(int i) throws IndexOutOfBoundsException; // elimina y devuelve el elemento en i
}
```

- En `get`, `set` y `remove` el índice válido es `[0, size() - 1]`.
- En `add` el índice válido es `[0, size()]`: si `i == size()`, el elemento queda al final.
- El índice de un elemento puede cambiar cuando se agregan o eliminan otros antes de él.

Ejemplo del libro sobre una lista de caracteres inicialmente vacía:

| Operación | Devuelve | Contenido |
|---|---|---|
| `add(0, A)` | – | (A) |
| `add(0, B)` | – | (B, A) |
| `get(1)` | A | (B, A) |
| `set(2, C)` | error | (B, A) |
| `add(2, C)` | – | (B, A, C) |
| `add(4, D)` | error | (B, A, C) |
| `remove(1)` | A | (B, C) |
| `add(1, D)` | – | (B, D, C) |
| `add(1, E)` | – | (B, E, D, C) |
| `get(4)` | error | (B, E, D, C) |
| `add(4, F)` | – | (B, E, D, C, F) |
| `set(2, G)` | D | (B, E, G, C, F) |
| `get(2)` | G | (B, E, G, C, F) |

La implementación más directa es un **arreglo**, donde `A[i]` guarda (una referencia a) el elemento con índice `i`. Así, `get` y `set` son O(1), mientras que `add` y `remove` deben desplazar elementos (O(n)), como se ve en [Arreglos e Iteradores](./arreglos-e-iteradores.md). Si se quiere que la lista no tenga capacidad fija, se usa un arreglo dinámico.

## Listas en el *Java Collections Framework*

Java ofrece la interfaz `java.util.List` con dos implementaciones principales:

| Operación | `ArrayList` (arreglo dinámico) | `LinkedList` (lista enlazada) |
|---|---|---|
| `size()`, `isEmpty()` | O(1) | O(1) |
| `get(i)`, `set(i, e)` | O(1) | O(min(i, n - i)) |
| `add(e)` (al final) | O(1) | O(1) |
| `add(0, e)` (al inicio) | O(n) | O(1) |
| `add(i, e)` | O(n) | O(n) |
| `remove(i)` | O(n) | O(min(i, n - i)) |

Ambas son `Iterable`, así que pueden recorrerse con *for-each*.

### `ListIterator`

El método `listIterator()` de una lista devuelve un `ListIterator`, un iterador que puede avanzar y **retroceder** y modificar la lista en la posición actual. Funciona como el **cursor** de un editor de texto: está antes del primer elemento, entre dos elementos o después del último.

| Método | Descripción |
|---|---|
| `hasNext()` / `next()` | hay / devuelve el elemento que sigue al cursor |
| `hasPrevious()` / `previous()` | hay / devuelve el elemento anterior al cursor |
| `nextIndex()` / `previousIndex()` | índice del elemento siguiente / anterior |
| `add(e)` | inserta `e` en la posición del cursor |
| `set(e)` | reemplaza el último elemento devuelto por `next` o `previous` |
| `remove()` | elimina el último elemento devuelto por `next` o `previous` |

Los iteradores de estas listas son **fail-fast**: si la lista se modifica por fuera de un iterador (con sus propios métodos o con otro iterador), ese iterador queda invalidado y al usarlo lanza `ConcurrentModificationException`.

[⬅️ Volver a la Unidad I](./index.md)
