---
name: snapshots
description: "Usar cuando reconstruir un agregado event-sourced desde sus eventos es lento y se plantean snapshots; subskill de event-sourcing."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# Snapshots

## Cuándo aplicar y cuándo no
- Aplica cuando se ha medido que cargar el agregado (leer y plegar todos sus eventos) supera el presupuesto de latencia.
- No aplica "por si acaso" ni con streams cortos (decenas de eventos): es optimización prematura. Subskill de `event-sourcing`.

## Reglas
- **MUST** medir antes: número de eventos por stream y tiempo de carga; documentar el umbral que justifica el snapshot.
- **MUST** tratar el snapshot como caché reconstruible, nunca como fuente de verdad: borrarlos todos no debe perder información.
- **MUST** guardar con el snapshot la `version` del último evento aplicado y un `snapshotSchemaVersion`.
- **MUST** cargar: último snapshot válido + eventos con `version` posterior; si el esquema del snapshot no coincide, ignorarlo y reconstruir desde los eventos.
- **MUST** escribir el snapshot de forma asíncrona o fuera de la ruta del comando, y tolerar que falle.
- **MUST NOT** actualizar el snapshot en la misma operación que decide el estado como si fuera un segundo estado (sería una segunda fuente de verdad).
- **SHOULD** crear snapshots cada N eventos (N medido, p. ej. múltiplo de 100) o por tiempo.
- **SHOULD** guardarlos con clave separada del stream (`pk = SNAPSHOT#ORDER#<id>`) para no mezclarlos con eventos.
- **MUST** probar que `fold(eventos)` y `snapshot + eventos posteriores` dan el mismo estado.

## Por qué
El snapshot es un atajo de lectura. Si se vuelve autoritativo, el sistema pasa a tener dos verdades que pueden divergir, y los cambios de esquema del estado obligan a migraciones. Como caché descartable, un snapshot corrupto o antiguo se ignora y listo.

## Ejemplos
### Mal
```java
state = snapshotRepo.load(id);              // se confía sin comprobar versión ni esquema
snapshotRepo.save(state.apply(cmd));        // el comando actualiza el snapshot en vez de añadir eventos
```
### Bien
```java
public AccountState load(String id) {
    Optional<Snapshot> snap = snapshots.latest(id).filter(s -> s.schemaVersion() == AccountState.SCHEMA);
    long from = snap.map(Snapshot::version).orElse(0L);
    AccountState base = snap.map(Snapshot::state).orElseGet(AccountState::empty);
    return events.readFrom(id, from + 1).stream().reduce(base, Evolver::evolve, (a, b) -> b);
}

// Fuera de la ruta del comando:
void maybeSnapshot(String id, AccountState s, long version) {
    if (version % SNAPSHOT_EVERY == 0) snapshots.saveAsync(id, version, AccountState.SCHEMA, s);
}
```
```java
@Test
void snapshotPlusTailEqualsFullReplay() {
    assertThat(loader.loadWithSnapshot(id)).isEqualTo(loader.loadFullReplay(id));
}
```

## Checklist de revisión
- [ ] Hay medición que justifica el snapshot.
- [ ] Se puede borrar todo snapshot sin pérdida.
- [ ] Incluyen `version` y `snapshotSchemaVersion`; esquema distinto se ignora.
- [ ] Test de equivalencia con la reconstrucción completa.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de equivalencia snapshot/replay (lo incluye el proyecto generado) | 1 | tests del proyecto generado |
| Revisión humana de la justificación medida | 4 | revisión humana en el ADR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `dynamodb-event-store`, `rebuilds-and-replays`, `aggregates-and-event-design`, `caching`.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
