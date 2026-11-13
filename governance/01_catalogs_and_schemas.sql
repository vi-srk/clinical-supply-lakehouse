-- Phase 3: environment catalogs and layer schemas.
-- Run per environment by the deployment pipeline; ${env} is substituted (dev | test | prod).

CREATE CATALOG IF NOT EXISTS clinical_supply_${env}
  COMMENT 'Clinical supply lakehouse - ${env}';
ALTER CATALOG clinical_supply_${env} OWNER TO `data-platform-admins`;

CREATE SCHEMA IF NOT EXISTS clinical_supply_${env}.bronze
  COMMENT 'Raw, append-only ingested data';
CREATE SCHEMA IF NOT EXISTS clinical_supply_${env}.silver
  COMMENT 'Cleaned, conformed, deduplicated data';
CREATE SCHEMA IF NOT EXISTS clinical_supply_${env}.silver_restricted
  COMMENT 'Patient PII/PHI - restricted access';
CREATE SCHEMA IF NOT EXISTS clinical_supply_${env}.gold
  COMMENT 'Business-ready star schema';
CREATE SCHEMA IF NOT EXISTS clinical_supply_${env}.quarantine
  COMMENT 'Records that failed quality rules';

ALTER SCHEMA clinical_supply_${env}.bronze            OWNER TO `data-engineering`;
ALTER SCHEMA clinical_supply_${env}.silver            OWNER TO `data-engineering`;
ALTER SCHEMA clinical_supply_${env}.silver_restricted OWNER TO `data-engineering`;
ALTER SCHEMA clinical_supply_${env}.gold              OWNER TO `data-engineering`;
ALTER SCHEMA clinical_supply_${env}.quarantine        OWNER TO `data-engineering`;
