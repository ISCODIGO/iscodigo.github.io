---
layout: post
title: "BST y AVL según Goodrich"
parent: "Unidad III: Árboles"
grand_parent: "ISC-211 Estructuras de Datos"
nav_order: 2
mermaid: true
---

Resumen de Goodrich, Tamassia y Goldwasser, *Data Structures and Algorithms in Java* (6.ª ed.), secciones 11.1 a 11.3. Se asume lo visto en [Árboles](./arboles.md). Para practicar, usa las pestañas **BST** y **AVL** de las [animaciones](./animaciones.html).

Colores de los diagramas: **azul** = camino de búsqueda, **amarillo** = lo que cambia, **rojo** = eliminado o desbalanceado.

## Árbol binario de búsqueda (BST)

Goodrich usa el BST para implementar un **mapa ordenado**: pares (clave, valor) sin claves repetidas, con `get(k)`, `put(k, v)` (si k existe, reemplaza el valor) y `remove(k)`. Al iterarlo, las claves salen **en orden**, y permite consultas como `floorEntry(k)` (mayor clave ≤ k) o `subMap(k1, k2)`.

### Definición

En cada nodo con clave k:

- las claves del subárbol **izquierdo** son **menores** que k;
- las del subárbol **derecho** son **mayores** que k.

Goodrich usa hojas **centinela** vacías (en código, `null`): una búsqueda fallida siempre termina en una, y ahí es donde se insertaría la clave. En los diagramas no se dibujan.

Figura 11.1, insertando **44, 17, 8, 32, 28, 21, 29, 88, 65, 54, 82, 76, 80, 97, 93**:

```mermaid
flowchart TD
    n1(("44"))
    n2(("17"))
    n3(("8"))
    n2 --- n3
    n4(("32"))
    n5(("28"))
    n6(("21"))
    n5 --- n6
    n7(("29"))
    n5 --- n7
    n4 --- n5
    n8[ ]:::vacio
    n4 ~~~ n8
    n2 --- n4
    n1 --- n2
    n9(("88"))
    n10(("65"))
    n11(("54"))
    n10 --- n11
    n12(("82"))
    n13(("76"))
    n14[ ]:::vacio
    n13 ~~~ n14
    n15(("80"))
    n13 --- n15
    n12 --- n13
    n16[ ]:::vacio
    n12 ~~~ n16
    n10 --- n12
    n9 --- n10
    n17(("97"))
    n18(("93"))
    n17 --- n18
    n19[ ]:::vacio
    n17 ~~~ n19
    n9 --- n17
    n1 --- n9
    classDef vacio fill:none,stroke:none,color:none
```

El recorrido **inorden** da las claves ordenadas: 8 17 21 28 29 32 44 54 65 76 80 82 88 93 97.

### Búsqueda

Se compara k con la clave del nodo: si es menor se baja a la izquierda, si es mayor a la derecha, si es igual se encontró. Llegar a una hoja vacía significa que **no está**.

```
Algoritmo TreeSearch(p, k):
    si p es externo:   devolver p                        {fallida}
    si k == key(p):    devolver p                        {exitosa}
    si k < key(p):     devolver TreeSearch(left(p), k)
    si no:             devolver TreeSearch(right(p), k)
```

Buscar **68** (figura 11.2):

```mermaid
flowchart TD
    k["Buscar k = 68"]:::clave
    a(("44")):::camino
    k ==> a
    a17(("17")):::otro
    a --- a17
    b(("88")):::camino
    a ==> b
    c(("65")):::camino
    b ==> c
    b97(("97")):::otro
    b --- b97
    c54(("54")):::otro
    c --- c54
    d(("82")):::camino
    c ==> d
    e(("76")):::camino
    d ==> e
    dv[ ]:::vacio
    d ~~~ dv
    f["hoja vacía:<br/>68 no está"]:::mal
    e ==> f
    e80(("80")):::otro
    e --- e80
    classDef clave fill:#fff3cd,stroke:#e0a800,color:#5c4400,font-weight:bold
    classDef vacio fill:none,stroke:none,color:none
    classDef camino fill:#d6eaff,stroke:#1e6fd9,color:#0b3d91,font-weight:bold
    classDef otro fill:#eeeeee,stroke:#999999,color:#444444
    classDef mal fill:#f8d7da,stroke:#dc3545,color:#842029,font-weight:bold
```

| Nodo | Comparación | Sigue por |
|------|-------------|-----------|
| 44 | 68 > 44 | derecha |
| 88 | 68 < 88 | izquierda |
| 65 | 68 > 65 | derecha |
| 82 | 68 < 82 | izquierda |
| 76 | 68 < 76 | izquierda → hoja vacía: **68 no está** |

Se visita un nodo por nivel: la búsqueda es **O(h)**, con h la altura.

### Inserción

`put(k, v)` busca k. Si la encuentra, reemplaza el valor; si no, guarda (k, v) en la hoja donde terminó la búsqueda, que es justo donde una búsqueda futura la esperaría.

Insertar **68** (figura 11.4): queda como hijo izquierdo de 76.

```mermaid
flowchart TD
    n1(("44"))
    n2(("17"))
    n3(("8"))
    n2 --- n3
    n4(("32"))
    n5(("28"))
    n6(("21"))
    n5 --- n6
    n7(("29"))
    n5 --- n7
    n4 --- n5
    n8[ ]:::vacio
    n4 ~~~ n8
    n2 --- n4
    n1 --- n2
    n9(("88"))
    n10(("65"))
    n11(("54"))
    n10 --- n11
    n12(("82"))
    n13(("76"))
    n14(("68")):::nuevo
    n13 --- n14
    n15(("80"))
    n13 --- n15
    n12 --- n13
    n16[ ]:::vacio
    n12 ~~~ n16
    n10 --- n12
    n9 --- n10
    n17(("97"))
    n18(("93"))
    n17 --- n18
    n19[ ]:::vacio
    n17 ~~~ n19
    n9 --- n17
    n1 --- n9
    classDef vacio fill:none,stroke:none,color:none
    classDef nuevo fill:#fff3cd,stroke:#e0a800,color:#5c4400,font-weight:bold
```

### Eliminación

Se busca k en el nodo p. Hay dos casos:

1. **p tiene a lo más un hijo.** Se quita p y su hijo (si tiene) **sube** a su lugar.
2. **p tiene dos hijos.** Se busca su **predecesor** r, el nodo **más a la derecha del subárbol izquierdo** (la mayor clave menor que la de p). Se copia r en p y se elimina r, que no tiene hijo derecho, así que es el caso 1.

#### Caso 1: eliminar 32

32 solo tiene hijo izquierdo (28): **28 sube** con su subárbol.

Antes:

```mermaid
flowchart TD
    a(("17"))
    b(("8"))
    a --- b
    c(("32")):::borrar
    a --- c
    d(("28")):::sube
    c --- d
    cv[ ]:::vacio
    c ~~~ cv
    e(("21"))
    d --- e
    f(("29"))
    d --- f
    classDef vacio fill:none,stroke:none,color:none
    classDef borrar fill:#f8d7da,stroke:#dc3545,color:#842029,font-weight:bold
    classDef sube fill:#fff3cd,stroke:#e0a800,color:#5c4400,font-weight:bold
    classDef pred fill:#d6eaff,stroke:#1e6fd9,color:#0b3d91,font-weight:bold
```

Después:

```mermaid
flowchart TD
    a(("17"))
    b(("8"))
    a --- b
    d(("28")):::sube
    a --- d
    e(("21"))
    d --- e
    f(("29"))
    d --- f
    classDef vacio fill:none,stroke:none,color:none
    classDef borrar fill:#f8d7da,stroke:#dc3545,color:#842029,font-weight:bold
    classDef sube fill:#fff3cd,stroke:#e0a800,color:#5c4400,font-weight:bold
    classDef pred fill:#d6eaff,stroke:#1e6fd9,color:#0b3d91,font-weight:bold
```

Si p es hoja, simplemente desaparece (por ejemplo, eliminar 93).

#### Caso 2: eliminar 88

Predecesor de 88: una vez a la izquierda (65) y luego a la derecha mientras se pueda → **82**. Se copia 82 en el lugar de 88 y se elimina el 82 original: su hijo 76 sube.

Antes:

```mermaid
flowchart TD
    a(("88")):::borrar
    b(("65"))
    a --- b
    c(("97"))
    a --- c
    d(("54"))
    b --- d
    e(("82")):::pred
    b --- e
    f(("76")):::sube
    e --- f
    ev[ ]:::vacio
    e ~~~ ev
    g(("68"))
    f --- g
    h(("80"))
    f --- h
    i(("93"))
    c --- i
    cv[ ]:::vacio
    c ~~~ cv
    classDef vacio fill:none,stroke:none,color:none
    classDef borrar fill:#f8d7da,stroke:#dc3545,color:#842029,font-weight:bold
    classDef sube fill:#fff3cd,stroke:#e0a800,color:#5c4400,font-weight:bold
    classDef pred fill:#d6eaff,stroke:#1e6fd9,color:#0b3d91,font-weight:bold
```

Después:

```mermaid
flowchart TD
    a(("82")):::pred
    b(("65"))
    a --- b
    c(("97"))
    a --- c
    d(("54"))
    b --- d
    f(("76")):::sube
    b --- f
    g(("68"))
    f --- g
    h(("80"))
    f --- h
    i(("93"))
    c --- i
    cv[ ]:::vacio
    c ~~~ cv
    classDef vacio fill:none,stroke:none,color:none
    classDef borrar fill:#f8d7da,stroke:#dc3545,color:#842029,font-weight:bold
    classDef sube fill:#fff3cd,stroke:#e0a800,color:#5c4400,font-weight:bold
    classDef pred fill:#d6eaff,stroke:#1e6fd9,color:#0b3d91,font-weight:bold
```

También es **O(h)**.

### Costo

Todo depende de la altura:

- **Mejor caso**: h ≈ log n, operaciones O(log n).
- **Peor caso**: h = n − 1, el árbol es una lista y todo cuesta O(n). Pasa al insertar claves **en orden** (figura 11.7):

```mermaid
flowchart TD
    n1(("10"))
    n2[ ]:::vacio
    n1 ~~~ n2
    n3(("20"))
    n4[ ]:::vacio
    n3 ~~~ n4
    n5(("30"))
    n6[ ]:::vacio
    n5 ~~~ n6
    n7(("40"))
    n5 --- n7
    n3 --- n5
    n1 --- n3
    classDef vacio fill:none,stroke:none,color:none
```

- **Promedio** (claves en orden aleatorio): altura O(log n).

Para garantizar O(log n) siempre, se usa un árbol balanceado como el AVL.

## Árboles AVL

### Definición

Un **AVL** (Adel'son-Vel'skii y Landis, 1962) es un BST que **se balancea solo**: en cada nodo, las alturas de sus dos hijos difieren **a lo más en 1**.

**Altura de un nodo**: aristas del camino más largo hacia abajo. Una hoja tiene h = 0 y un hijo que no existe cuenta como h = −1.

**Factor de equilibrio:**

> **FE = h(hijo derecho) − h(hijo izquierdo)**

Un nodo está balanceado si FE es −1, 0 o +1. Basta **un** nodo con FE = ±2 para que el árbol deje de ser AVL. Tras cada inserción o eliminación se revisa el camino a la raíz y se repara con una [rotación](#rotaciones).

| | BST común | AVL |
|---|---|---|
| Balance | no se controla | todo nodo con FE ∈ {−1, 0, +1} |
| Altura en el peor caso | n − 1 | ≤ 2 log n + 1 (en la práctica ≈ 1.44 log n) |
| Buscar, insertar, eliminar | O(n) en el peor caso | O(log n) siempre |
| Costo extra | ninguno | guardar la altura en cada nodo y rotar |

**Ejemplo de AVL** (figura 11.10):

```mermaid
flowchart TD
    n1(("44<br/>h=3<br/>FE=+1"))
    n2(("17<br/>h=1<br/>FE=+1"))
    n3[ ]:::vacio
    n2 ~~~ n3
    n4(("32<br/>h=0<br/>FE=0"))
    n2 --- n4
    n1 --- n2
    n5(("78<br/>h=2<br/>FE=−1"))
    n6(("50<br/>h=1<br/>FE=0"))
    n7(("48<br/>h=0<br/>FE=0"))
    n6 --- n7
    n8(("62<br/>h=0<br/>FE=0"))
    n6 --- n8
    n5 --- n6
    n9(("88<br/>h=0<br/>FE=0"))
    n5 --- n9
    n1 --- n5
    classDef vacio fill:none,stroke:none,color:none
```

Por ejemplo, 17: FE = 0 − (−1) = +1; 78: FE = 0 − 1 = −1; 44: FE = 2 − 1 = +1. Todos entre −1 y +1.

**No es AVL**: si se quita el 32, la raíz 44 tiene hijos de altura 0 y 2, FE = **+2**.

```mermaid
flowchart TD
    n1(("44<br/>h=3<br/>FE=+2")):::mal
    n2(("17<br/>h=0<br/>FE=0"))
    n1 --- n2
    n5(("78<br/>h=2<br/>FE=−1"))
    n6(("50<br/>h=1<br/>FE=0"))
    n7(("48<br/>h=0<br/>FE=0"))
    n6 --- n7
    n8(("62<br/>h=0<br/>FE=0"))
    n6 --- n8
    n5 --- n6
    n9(("88<br/>h=0<br/>FE=0"))
    n5 --- n9
    n1 --- n5
    classDef mal fill:#f8d7da,stroke:#dc3545,color:#842029,font-weight:bold
```

> **Si lees el libro:** Goodrich cuenta las hojas centinela como altura 0, así que sus alturas son 1 mayores que aquí. Los FE salen iguales.

### La altura es O(log n)

Sea n(h) el **mínimo** de nodos de un AVL de altura h. n(0) = 1, n(1) = 2 y, para h ≥ 2, la raíz más dos subárboles mínimos de alturas h − 1 y h − 2:

**n(h) = 1 + n(h − 1) + n(h − 2)**

Parecida a [Fibonacci](../unidad-2/recursion.md): crece exponencialmente. Como n(h − 1) > n(h − 2), se tiene n(h) > 2·n(h − 2) > … > 2<sup>⌊h/2⌋</sup>, y sacando logaritmos, **h ≤ 2 log n + 1**.

### Rotaciones

Un nodo desbalanceado **z** se arregla con su hijo **y** y su nieto **x** en el camino. La regla (Goodrich la llama **`restructure(x)`**):

> Ordenar x, y, z por clave (a < b < c). **El del medio (b) sube**, a queda a su izquierda y c a su derecha.

Los subárboles que colgaban se reacomodan en el mismo orden, así que sigue siendo BST. Es **O(1)**.

Con 10, 20 y 30 hay cuatro formas, y todas terminan igual (rojo = z, amarillo = el que sube):

<table>
<thead><tr><th>Forma de z → y → x</th><th>Antes</th><th>Después</th><th>Rotación</th></tr></thead>
<tbody>
<tr><td>izquierda-izquierda<br/><small>30 → 20 → 10</small></td><td><svg width="130" height="122" viewBox="0 0 130 122" role="img"><line x1="98" y1="22" x2="68" y2="62" stroke="#34495e" stroke-width="2"/><line x1="68" y1="62" x2="38" y2="102" stroke="#34495e" stroke-width="2"/><circle cx="98" cy="22" r="15" fill="#f8d7da" stroke="#dc3545" stroke-width="2"/><text x="98" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#842029">30</text><text x="122" y="26" text-anchor="middle" font-size="12" font-style="italic" fill="#666">z</text><circle cx="68" cy="62" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="68" y="67" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">20</text><text x="44" y="66" text-anchor="middle" font-size="12" font-style="italic" fill="#666">y</text><circle cx="38" cy="102" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="38" y="107" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">10</text><text x="14" y="106" text-anchor="middle" font-size="12" font-style="italic" fill="#666">x</text></svg></td><td><svg width="130" height="102" viewBox="0 0 130 102" role="img"><line x1="67" y1="22" x2="37" y2="82" stroke="#34495e" stroke-width="2"/><line x1="67" y1="22" x2="97" y2="82" stroke="#34495e" stroke-width="2"/><circle cx="67" cy="22" r="15" fill="#fff3cd" stroke="#e0a800" stroke-width="2"/><text x="67" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#5c4400">20</text><text x="91" y="26" text-anchor="middle" font-size="12" font-style="italic" fill="#666">y</text><circle cx="37" cy="82" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="37" y="87" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">10</text><text x="13" y="86" text-anchor="middle" font-size="12" font-style="italic" fill="#666">x</text><circle cx="97" cy="82" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="97" y="87" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">30</text><text x="121" y="86" text-anchor="middle" font-size="12" font-style="italic" fill="#666">z</text></svg></td><td><b>simple</b>: 20 (y) sube una vez</td></tr>
<tr><td>derecha-derecha<br/><small>10 → 20 → 30</small></td><td><svg width="130" height="122" viewBox="0 0 130 122" role="img"><line x1="40" y1="22" x2="70" y2="62" stroke="#34495e" stroke-width="2"/><line x1="70" y1="62" x2="100" y2="102" stroke="#34495e" stroke-width="2"/><circle cx="40" cy="22" r="15" fill="#f8d7da" stroke="#dc3545" stroke-width="2"/><text x="40" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#842029">10</text><text x="64" y="26" text-anchor="middle" font-size="12" font-style="italic" fill="#666">z</text><circle cx="70" cy="62" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="70" y="67" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">20</text><text x="94" y="66" text-anchor="middle" font-size="12" font-style="italic" fill="#666">y</text><circle cx="100" cy="102" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="100" y="107" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">30</text><text x="124" y="106" text-anchor="middle" font-size="12" font-style="italic" fill="#666">x</text></svg></td><td><svg width="130" height="102" viewBox="0 0 130 102" role="img"><line x1="67" y1="22" x2="37" y2="82" stroke="#34495e" stroke-width="2"/><line x1="67" y1="22" x2="97" y2="82" stroke="#34495e" stroke-width="2"/><circle cx="67" cy="22" r="15" fill="#fff3cd" stroke="#e0a800" stroke-width="2"/><text x="67" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#5c4400">20</text><text x="91" y="26" text-anchor="middle" font-size="12" font-style="italic" fill="#666">y</text><circle cx="37" cy="82" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="37" y="87" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">10</text><text x="13" y="86" text-anchor="middle" font-size="12" font-style="italic" fill="#666">z</text><circle cx="97" cy="82" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="97" y="87" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">30</text><text x="121" y="86" text-anchor="middle" font-size="12" font-style="italic" fill="#666">x</text></svg></td><td><b>simple</b>: 20 (y) sube una vez</td></tr>
<tr><td>izquierda-derecha<br/><small>30 → 10 → 20</small></td><td><svg width="130" height="122" viewBox="0 0 130 122" role="img"><line x1="85" y1="22" x2="45" y2="62" stroke="#34495e" stroke-width="2"/><line x1="45" y1="62" x2="75" y2="102" stroke="#34495e" stroke-width="2"/><circle cx="85" cy="22" r="15" fill="#f8d7da" stroke="#dc3545" stroke-width="2"/><text x="85" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#842029">30</text><text x="109" y="26" text-anchor="middle" font-size="12" font-style="italic" fill="#666">z</text><circle cx="45" cy="62" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="45" y="67" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">10</text><text x="21" y="66" text-anchor="middle" font-size="12" font-style="italic" fill="#666">y</text><circle cx="75" cy="102" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="75" y="107" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">20</text><text x="99" y="106" text-anchor="middle" font-size="12" font-style="italic" fill="#666">x</text></svg></td><td><svg width="130" height="102" viewBox="0 0 130 102" role="img"><line x1="67" y1="22" x2="37" y2="82" stroke="#34495e" stroke-width="2"/><line x1="67" y1="22" x2="97" y2="82" stroke="#34495e" stroke-width="2"/><circle cx="67" cy="22" r="15" fill="#fff3cd" stroke="#e0a800" stroke-width="2"/><text x="67" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#5c4400">20</text><text x="91" y="26" text-anchor="middle" font-size="12" font-style="italic" fill="#666">x</text><circle cx="37" cy="82" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="37" y="87" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">10</text><text x="13" y="86" text-anchor="middle" font-size="12" font-style="italic" fill="#666">y</text><circle cx="97" cy="82" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="97" y="87" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">30</text><text x="121" y="86" text-anchor="middle" font-size="12" font-style="italic" fill="#666">z</text></svg></td><td><b>doble</b>: 20 (x) sube dos veces</td></tr>
<tr><td>derecha-izquierda<br/><small>10 → 30 → 20</small></td><td><svg width="130" height="122" viewBox="0 0 130 122" role="img"><line x1="35" y1="22" x2="75" y2="62" stroke="#34495e" stroke-width="2"/><line x1="75" y1="62" x2="45" y2="102" stroke="#34495e" stroke-width="2"/><circle cx="35" cy="22" r="15" fill="#f8d7da" stroke="#dc3545" stroke-width="2"/><text x="35" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#842029">10</text><text x="59" y="26" text-anchor="middle" font-size="12" font-style="italic" fill="#666">z</text><circle cx="75" cy="62" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="75" y="67" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">30</text><text x="99" y="66" text-anchor="middle" font-size="12" font-style="italic" fill="#666">y</text><circle cx="45" cy="102" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="45" y="107" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">20</text><text x="21" y="106" text-anchor="middle" font-size="12" font-style="italic" fill="#666">x</text></svg></td><td><svg width="130" height="102" viewBox="0 0 130 102" role="img"><line x1="67" y1="22" x2="37" y2="82" stroke="#34495e" stroke-width="2"/><line x1="67" y1="22" x2="97" y2="82" stroke="#34495e" stroke-width="2"/><circle cx="67" cy="22" r="15" fill="#fff3cd" stroke="#e0a800" stroke-width="2"/><text x="67" y="27" text-anchor="middle" font-size="13" font-weight="bold" fill="#5c4400">20</text><text x="91" y="26" text-anchor="middle" font-size="12" font-style="italic" fill="#666">x</text><circle cx="37" cy="82" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="37" y="87" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">10</text><text x="13" y="86" text-anchor="middle" font-size="12" font-style="italic" fill="#666">z</text><circle cx="97" cy="82" r="15" fill="#ffffff" stroke="#34495e" stroke-width="2"/><text x="97" y="87" text-anchor="middle" font-size="13" font-weight="bold" fill="#222222">30</text><text x="121" y="86" text-anchor="middle" font-size="12" font-style="italic" fill="#666">y</text></svg></td><td><b>doble</b>: 20 (x) sube dos veces</td></tr>
</tbody>
</table>

Si el camino va **en línea recta**, basta una rotación **simple**; si hace **zigzag**, hace falta una **doble**.

### Inserción

Se inserta como en un BST y se sube desde el nuevo nodo:

1. **z** = primer nodo desbalanceado.
2. **y** = hijo de z con mayor altura; **x** = hijo de y con mayor altura.
3. `restructure(x)`.

El subárbol recupera la altura que tenía antes de insertar, así que **una sola rotación basta**.

Insertar **54** (figura 11.11): 78 y 44 quedan con FE = ±2.

```mermaid
flowchart TD
    n1(("44<br/>h=4<br/>FE=+2")):::mal
    n2(("17<br/>h=1<br/>FE=+1"))
    n3[ ]:::vacio
    n2 ~~~ n3
    n4(("32<br/>h=0<br/>FE=0"))
    n2 --- n4
    n1 --- n2
    n5(("z = 78<br/>h=3<br/>FE=−2")):::mal
    n6(("y = 50<br/>h=2<br/>FE=+1"))
    n7(("48<br/>h=0<br/>FE=0"))
    n6 --- n7
    n8(("x = 62<br/>h=1<br/>FE=−1"))
    n9(("54<br/>h=0<br/>FE=0")):::nuevo
    n8 --- n9
    n10[ ]:::vacio
    n8 ~~~ n10
    n6 --- n8
    n5 --- n6
    n11(("88<br/>h=0<br/>FE=0"))
    n5 --- n11
    n1 --- n5
    classDef vacio fill:none,stroke:none,color:none
    classDef mal fill:#f8d7da,stroke:#dc3545,color:#842029,font-weight:bold
    classDef nuevo fill:#fff3cd,stroke:#e0a800,color:#5c4400,font-weight:bold
```

z = 78, y = 50, x = 62. El camino es izquierda-derecha (zigzag): **doble**, y 62 sube:

```mermaid
flowchart TD
    n1(("44<br/>h=3<br/>FE=+1"))
    n2(("17<br/>h=1<br/>FE=+1"))
    n3[ ]:::vacio
    n2 ~~~ n3
    n4(("32<br/>h=0<br/>FE=0"))
    n2 --- n4
    n1 --- n2
    n5(("62<br/>h=2<br/>FE=0")):::nuevo
    n6(("50<br/>h=1<br/>FE=0")):::nuevo
    n7(("48<br/>h=0<br/>FE=0"))
    n6 --- n7
    n8(("54<br/>h=0<br/>FE=0"))
    n6 --- n8
    n5 --- n6
    n9(("78<br/>h=1<br/>FE=+1")):::nuevo
    n10[ ]:::vacio
    n9 ~~~ n10
    n11(("88<br/>h=0<br/>FE=0"))
    n9 --- n11
    n5 --- n9
    n1 --- n5
    classDef vacio fill:none,stroke:none,color:none
    classDef nuevo fill:#fff3cd,stroke:#e0a800,color:#5c4400,font-weight:bold
```

### Eliminación

Se elimina como en un BST y se sube desde el lugar del nodo quitado, con la misma elección de z, y, x. Dos diferencias:

- Si los hijos de y **empatan** en altura, x es el del **mismo lado** que y, para que la rotación sea simple y siempre funcione.
- La rotación puede **bajar en 1** la altura del subárbol, así que hay que **seguir subiendo** hasta la raíz: hasta O(log n) rotaciones.

Eliminar **32** (figura 11.13): z = 44 con FE = +2.

```mermaid
flowchart TD
    n1(("z = 44<br/>h=3<br/>FE=+2")):::mal
    n2(("17<br/>h=0<br/>FE=0"))
    n1 --- n2
    n3(("y = 62<br/>h=2<br/>FE=0"))
    n4(("50<br/>h=1<br/>FE=0"))
    n5(("48<br/>h=0<br/>FE=0"))
    n4 --- n5
    n6(("54<br/>h=0<br/>FE=0"))
    n4 --- n6
    n3 --- n4
    n7(("x = 78<br/>h=1<br/>FE=+1"))
    n8[ ]:::vacio
    n7 ~~~ n8
    n9(("88<br/>h=0<br/>FE=0"))
    n7 --- n9
    n3 --- n7
    n1 --- n3
    classDef vacio fill:none,stroke:none,color:none
    classDef mal fill:#f8d7da,stroke:#dc3545,color:#842029,font-weight:bold
```

y = 62. Sus hijos empatan (altura 1) y y es hijo derecho, así que x = 78. Camino derecha-derecha: **simple**, y 62 sube:

```mermaid
flowchart TD
    n1(("62<br/>h=3<br/>FE=−1")):::nuevo
    n2(("44<br/>h=2<br/>FE=+1")):::nuevo
    n3(("17<br/>h=0<br/>FE=0"))
    n2 --- n3
    n4(("50<br/>h=1<br/>FE=0"))
    n5(("48<br/>h=0<br/>FE=0"))
    n4 --- n5
    n6(("54<br/>h=0<br/>FE=0"))
    n4 --- n6
    n2 --- n4
    n1 --- n2
    n7(("78<br/>h=1<br/>FE=+1"))
    n8[ ]:::vacio
    n7 ~~~ n8
    n9(("88<br/>h=0<br/>FE=0"))
    n7 --- n9
    n1 --- n7
    classDef vacio fill:none,stroke:none,color:none
    classDef nuevo fill:#fff3cd,stroke:#e0a800,color:#5c4400,font-weight:bold
```

### Costo

Cada operación baja buscando y sube recalculando alturas, con O(1) por nivel (tabla 11.2):

| Método | BST | AVL |
|---|---|---|
| `size`, `isEmpty` | O(1) | O(1) |
| `get`, `put`, `remove` | O(h), O(n) en el peor caso | **O(log n)** |
| `firstEntry`, `floorEntry`, `higherEntry`… | O(h) | O(log n) |
| `subMap` (s entradas) | O(s + h) | O(s + log n) |
| `entrySet`, `keySet`, `values` | O(n) | O(n) |

[⬅️ Volver al índice de la unidad](./index.md)
