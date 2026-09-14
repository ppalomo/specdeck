## MODIFIED Requirements

### Requirement: Una tarea se puede dar por hecha

La aplicación DEBE permitir marcar una tarea como hecha, y NO DEBE perder la fecha en la
que se marcó. Dar una tarea por hecha DEBE cancelar su recordatorio si todavía no ha
avisado.

#### Scenario: Marcar una tarea pendiente

- **WHEN** alguien marca como hecha una tarea que estaba pendiente
- **THEN** la tarea queda hecha y guarda la fecha en la que se marcó

#### Scenario: Desmarcar una tarea

- **WHEN** alguien quita la marca de una tarea que estaba hecha
- **THEN** la tarea vuelve a estar pendiente y NO DEBE conservar la fecha anterior

#### Scenario: Dar por hecha una tarea con recordatorio

- **WHEN** se da por hecha una tarea cuyo recordatorio aún no ha avisado
- **THEN** el recordatorio queda cancelado y NO DEBE avisar más tarde

## ADDED Requirements

### Requirement: Una tarea puede avisar una vez

Una tarea DEBE poder llevar la hora a la que avisar, y el aviso DEBE enviarse una sola vez
aunque el envío se ejecute muchas veces.

#### Scenario: La hora llega

- **WHEN** se ejecuta el envío y una tarea con recordatorio tiene la hora pasada
- **THEN** la tarea avisa una vez y queda marcada como avisada

#### Scenario: El envío se ejecuta otra vez

- **WHEN** se vuelve a ejecutar el envío sobre una tarea que ya avisó
- **THEN** NO DEBE avisar de nuevo
