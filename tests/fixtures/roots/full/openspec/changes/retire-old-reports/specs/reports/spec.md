## MODIFIED Requirements

### Requirement: Un informe dice de qué periodo habla

Todo informe DEBE llevar el periodo del que habla, con su fecha de inicio y su fecha de
fin, para que no pueda confundirse con otro sacado otro día. DEBE decir además quién cerró
cada tarea que incluye.

#### Scenario: Sacar un informe de un mes

- **WHEN** se pide el informe de un mes concreto
- **THEN** el informe dice la fecha de inicio y la de fin de ese mes, y quién cerró cada tarea

## REMOVED Requirements

### Requirement: Hay un informe semanal

**Reason**: Nadie lo abre desde que existe el mensual, y mantenerlo cuesta lo mismo.
**Migration**: Pedir el informe mensual y filtrar por la semana que interese.

## RENAMED Requirements

- FROM: `### Requirement: Un informe se puede exportar`
- TO: `### Requirement: Un informe se puede descargar`
