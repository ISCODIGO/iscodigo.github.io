---
layout: default
title: "Unidad I: Introducción a SO y Control de Procesos"
parent: "ISC-333 Sistemas Operativos I"
nav_order: 1
has_children: true
has_mermaid: true
---

# 📘 Unidad I: Unidad I: Introducción a SO y Control de Procesos

**[1. Introduccion ](./introSO.md)**
Una introducción a los sistemas operativos, su historia, evolución y su papel fundamental en la informática moderna.

**[2. Procesos](./procesos.md)**
Definición, estados, descripción y control de procesos. Basado en el Capítulo 2 de *Modern Operating Systems* (Tanenbaum & Bos) y el Capítulo 3 de *Operating Systems: Internals and Design Principles* (Stallings).

**[3. Hilos (Threads)](./hilos.md)**
Conceptos fundamentales de hilos, diferencias con procesos, uso de `pthreads`, memoria compartida y condiciones de carrera, basado en los temas del laboratorio de threads.

**[4. Lab: Procesos en Linux con GCC](./lab-procesos-linux.md)**
Laboratorio práctico en GNU/Linux con GCC: identificación de procesos (PID, PPID, UID), `fork()`, jerarquías, estados y zombies con `wait()`, `execv()`, y `pipe()`. Incluye herramientas Linux: `/proc`, `strace` y `pstree`.

**[5. Lab: Procesos en Minix3 con Clang](./lab-procesos-minix3.md)**
Laboratorio práctico en Minix 3.3 con Clang: identificación de procesos (PID, PPID, UID), creación con `fork()`, jerarquías, estados y zombies con `wait()`, reemplazo de imagen con `execv()`, y comunicación entre procesos con `pipe()`.
