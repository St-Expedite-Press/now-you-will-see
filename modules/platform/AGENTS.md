# Platform Module

Owns cross-module platform contracts, shared command surfaces, schemas, and
future module runtime integration.

## Scope

- Cross-module coordination and shared platform abstractions.
- Module manifests, shared schemas, and platform tools.
- Compatibility mapping for legacy machinery-owned infrastructure.

## Artifact Boundary

This module stages platform-facing module work. Do not edit legacy
`machinery/src/texgraph/`, root docs, or root tests from this module without
explicit scope approval.

## Local Layout

- `src/` module implementation
- `tests/` module tests
- `skills/` reusable workflows
- `schemas/` module-owned schemas
- `tools/` deterministic helpers

