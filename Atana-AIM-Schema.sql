-- Atana AIM Engine v1.0 — additive to IRE + Enterprise Schema v1.1
-- Asset types are catalogue. Asset instances belong to a project + SPP.
-- Completeness is required IR vs observations, not drawing count.

CREATE TABLE IF NOT EXISTS asset_types (
  asset_type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES organisations(org_id),
  type_code TEXT NOT NULL,
  type_name TEXT NOT NULL,
  ro_code TEXT,
  ss_code TEXT,
  ifc_entity TEXT,
  UNIQUE (org_id, type_code)
);

CREATE TABLE IF NOT EXISTS asset_type_ir (
  asset_type_id UUID NOT NULL REFERENCES asset_types(asset_type_id) ON DELETE CASCADE,
  ir_id UUID NOT NULL REFERENCES information_requirements(ir_id) ON DELETE CASCADE,
  PRIMARY KEY (asset_type_id, ir_id)
);

CREATE TABLE IF NOT EXISTS asset_type_deliverables (
  asset_type_id UUID NOT NULL REFERENCES asset_types(asset_type_id) ON DELETE CASCADE,
  deliverable_type TEXT NOT NULL,
  form_code TEXT,
  PRIMARY KEY (asset_type_id, deliverable_type)
);

CREATE TABLE IF NOT EXISTS aim_assets (
  asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  asset_type_id UUID NOT NULL REFERENCES asset_types(asset_type_id),
  spp_id UUID REFERENCES scope_production_packages(spp_id),
  fb_code TEXT,
  sl_code TEXT,
  mark TEXT,
  ifc_guid TEXT,
  status TEXT NOT NULL DEFAULT 'PLANNED',
  UNIQUE (project_id, mark)
);
CREATE INDEX IF NOT EXISTS ix_aim_project ON aim_assets(project_id);
CREATE INDEX IF NOT EXISTS ix_aim_spp ON aim_assets(spp_id);

CREATE OR REPLACE VIEW vw_asset_completeness AS
SELECT
  a.project_id,
  a.asset_id,
  a.mark,
  t.type_code,
  t.ro_code,
  COUNT(ati.ir_id) AS required_n,
  COUNT(o.obs_id) FILTER (WHERE o.present) AS present_n,
  CASE WHEN COUNT(ati.ir_id) = 0 THEN NULL
       ELSE ROUND(100.0 * COUNT(o.obs_id) FILTER (WHERE o.present) / COUNT(ati.ir_id), 1)
  END AS completeness_pct
FROM aim_assets a
JOIN asset_types t ON t.asset_type_id = a.asset_type_id
LEFT JOIN asset_type_ir ati ON ati.asset_type_id = a.asset_type_id
LEFT JOIN ir_observations o ON o.ir_id = ati.ir_id AND o.spp_id = a.spp_id
GROUP BY a.project_id, a.asset_id, a.mark, t.type_code, t.ro_code;

CREATE OR REPLACE VIEW vw_asset_type_dashboard AS
SELECT
  project_id,
  type_code,
  ro_code,
  COUNT(*) AS assets_n,
  ROUND(AVG(completeness_pct)::numeric, 1) AS avg_completeness
FROM vw_asset_completeness
GROUP BY project_id, type_code, ro_code;
