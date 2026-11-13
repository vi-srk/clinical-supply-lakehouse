# ADR 0002: Medallion lakehouse on Azure Databricks, governed by Unity Catalog

- **Status:** Accepted
- **Date:** 2026-11-12

## Context

The platform must handle batch files, a change-data stream and an external API; serve BI and AI consumers; and protect patient PII/PHI with auditable access rules.

## Decision

- Store all data as **Delta Lake** tables in a **Bronze → Silver → Gold** (medallion) layout.
- Run on **Azure Databricks**, with **Unity Catalog** as the single governance layer: one catalog per environment (`clinical_supply_dev`, `_test`, `_prod`), schemas per layer.
- Patient PII lives only in a restricted Silver schema; Gold exposes pseudonymised keys.

## Consequences

- One security model (UC grants, tags, ABAC masks) covers tables, views, functions and models.
- Lineage and audit come from Unity Catalog and system tables without extra tooling.
- The team needs Databricks skills; Fabric is used downstream for BI via OneLake/Direct Lake rather than as the core engine.

## Alternatives considered

- **Microsoft Fabric as the core engine:** strong for BI-centric teams, but this project prioritises Spark engineering depth and Unity Catalog's fine-grained governance.
- **Separate warehouse + data lake:** duplicates data and splits governance across two systems.
