# reports Specification

## Purpose
Los informes que la aplicación saca de las tareas: qué se hizo, cuándo y por quién.

## Requirements

### Requirement: Un informe dice de qué periodo habla

Todo informe DEBE llevar el periodo del que habla, con su fecha de inicio y su fecha de
fin, para que no pueda confundirse con otro sacado otro día.

#### Scenario: Sacar un informe de un mes

- **WHEN** se pide el informe de un mes concreto
- **THEN** el informe dice la fecha de inicio y la de fin de ese mes
