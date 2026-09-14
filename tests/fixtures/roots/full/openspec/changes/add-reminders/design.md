## Context

Ver `proposal.md` — Why. La aplicación ya guarda la fecha de vencimiento de una tarea, así
que lo que falta es cuándo avisar y haber avisado.

## Goals / Non-Goals

**Goals:**

- Que un recordatorio avise una vez y quede constancia de que avisó.

**Non-Goals:**

- Recordatorios que se repiten. Llegan cuando alguien los pida.

## Decisions

### El aviso se marca al enviarse, no al leerse

Marcarlo al enviarse hace que un fallo de lectura no provoque un segundo aviso, que es lo
que más molesta de un recordatorio.

## Risks / Trade-offs

- **Un aviso perdido no se reintenta** → Es el precio de no insistir nunca de más.
