# task-management Specification

## Purpose
Qué puede hacer alguien con sus tareas: escribirlas, agruparlas y darlas por hechas.

## Requirements

### Requirement: Una tarea se puede dar por hecha

La aplicación DEBE permitir marcar una tarea como hecha, y NO DEBE perder la fecha en la
que se marcó.

#### Scenario: Marcar una tarea pendiente

- **WHEN** alguien marca como hecha una tarea que estaba pendiente
- **THEN** la tarea queda hecha y guarda la fecha en la que se marcó

#### Scenario: Desmarcar una tarea

- **WHEN** alguien quita la marca de una tarea que estaba hecha
- **THEN** la tarea vuelve a estar pendiente y NO DEBE conservar la fecha anterior

### Requirement: Las tareas se agrupan

Una tarea DEBE pertenecer a un grupo, y el grupo DEBE decir cuántas de sus tareas están
hechas sin que haya que contarlas a mano.

#### Scenario: Contar lo hecho de un grupo

- **WHEN** se mira un grupo con cuatro tareas de las que dos están hechas
- **THEN** el grupo dice que hay cuatro y que dos están hechas
