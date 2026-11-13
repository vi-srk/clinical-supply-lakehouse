# Governance as code

Unity Catalog configuration lives here, versioned and reviewed like any other code.

| File | Purpose | Phase |
| --- | --- | --- |
| `01_catalogs_and_schemas.sql` | Catalogs per environment, schemas per layer, ownership | 3 |
| `02_grants.sql` | Group-based, least-privilege grants | 3 |
| `03_tags_and_classification.sql` | PII / PHI tags on sensitive columns | 5 |
| `04_masking_policies.sql` | ABAC column masks and row filters | 5 |
| `05_audit_queries.sql` | Who accessed what, untagged tables, tables without owners | 5 |

Rules:
- Grant to **groups**, never to individual users.
- Every catalog and schema has an **owner** group.
- Every column holding PII/PHI carries a **classification tag** before it reaches Silver.
