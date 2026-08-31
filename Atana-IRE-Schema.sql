-- Atana Information Requirements Engine (IRE) v1.0
-- Additive to Atana-Enterprise-Schema-v1.1.sql
-- Scope Production Package is the persistent object.
-- Workstage holds LOD/LOI targets. IR rows come from the LOI catalogue.

CREATE TABLE IF NOT EXISTS ir_catalogues (
  catalogue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES organisations(org_id),
  source_name TEXT NOT NULL,
  source_hash TEXT,
  version TEXT NOT NULL DEFAULT '1.0',
  imported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One row per workbook line: Team / Category / Type / Attribute
CREATE TABLE IF NOT EXISTS information_requirements (
  ir_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  catalogue_id UUID NOT NULL REFERENCES ir_catalogues(catalogue_id) ON DELETE CASCADE,
  ro_code TEXT NOT NULL,
  category TEXT NOT NULL,
  type_name TEXT,
  attribute_name TEXT NOT NULL,
  parameter_name TEXT,
  data_type TEXT,
  unit TEXT,
  ifc_pset TEXT,
  parameter_type TEXT,
  loi2 BOOLEAN NOT NULL DEFAULT FALSE,
  loi3 BOOLEAN NOT NULL DEFAULT FALSE,
  loi4 BOOLEAN NOT NULL DEFAULT FALSE,
  loi5 BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE (catalogue_id, ro_code, category, attribute_name)
);
CREATE INDEX IF NOT EXISTS ix_ir_team_cat ON information_requirements(ro_code, category);

-- Persistent scope object (not per workstage)
CREATE TABLE IF NOT EXISTS scope_production_packages (
  spp_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  ss_code TEXT NOT NULL,
  ss_name TEXT NOT NULL,
  ro_code TEXT NOT NULL,
  fb_code TEXT,
  UNIQUE (project_id, ss_code, ro_code, COALESCE(fb_code, ''))
);
CREATE INDEX IF NOT EXISTS ix_spp_project ON scope_production_packages(project_id);

CREATE TABLE IF NOT EXISTS spp_stage_targets (
  spp_id UUID NOT NULL REFERENCES scope_production_packages(spp_id) ON DELETE CASCADE,
  stage_id TEXT NOT NULL,
  lod_target TEXT,
  loi_target TEXT,
  PRIMARY KEY (spp_id, stage_id)
);

CREATE TABLE IF NOT EXISTS spp_ir_links (
  spp_id UUID NOT NULL REFERENCES scope_production_packages(spp_id) ON DELETE CASCADE,
  ir_id UUID NOT NULL REFERENCES information_requirements(ir_id) ON DELETE CASCADE,
  required BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (spp_id, ir_id)
);

CREATE TABLE IF NOT EXISTS spp_deliverable_links (
  spp_id UUID NOT NULL REFERENCES scope_production_packages(spp_id) ON DELETE CASCADE,
  del_id UUID NOT NULL REFERENCES deliverables(del_id) ON DELETE CASCADE,
  PRIMARY KEY (spp_id, del_id)
);

-- Observed model / CDE values for compliance
CREATE TABLE IF NOT EXISTS ir_observations (
  obs_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  spp_id UUID REFERENCES scope_production_packages(spp_id) ON DELETE CASCADE,
  ir_id UUID NOT NULL REFERENCES information_requirements(ir_id),
  source TEXT NOT NULL DEFAULT 'MODEL', -- MODEL | CDE | MANUAL
  present BOOLEAN NOT NULL DEFAULT FALSE,
  observed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE VIEW vw_loi_compliance AS
SELECT
  s.project_id,
  s.spp_id,
  s.ss_code,
  s.ro_code,
  COUNT(l.ir_id) FILTER (WHERE l.required) AS required_n,
  COUNT(o.obs_id) FILTER (WHERE l.required AND o.present) AS present_n,
  CASE WHEN COUNT(l.ir_id) FILTER (WHERE l.required) = 0 THEN NULL
       ELSE ROUND(100.0 * COUNT(o.obs_id) FILTER (WHERE l.required AND o.present)
            / COUNT(l.ir_id) FILTER (WHERE l.required), 1)
  END AS compliance_pct
FROM scope_production_packages s
LEFT JOIN spp_ir_links l ON l.spp_id = s.spp_id
LEFT JOIN ir_observations o ON o.spp_id = s.spp_id AND o.ir_id = l.ir_id
GROUP BY s.project_id, s.spp_id, s.ss_code, s.ro_code;
