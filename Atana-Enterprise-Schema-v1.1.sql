-- Atana Enterprise Schema v1.0
-- PostgreSQL 14+
-- Multi-organisation, multi-project, ISO 19650 planning register
-- Companion to Atana-Platform-Specification-v1.0.docx

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ===== ENUMS =====
DO $$ BEGIN CREATE TYPE atana_status AS ENUM ('DRAFT','ACTIVE','RETIRED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE atana_info_state AS ENUM ('WIP','PEER_REVIEW','SHARED','TTM_APPROVAL','PUBLISHED','ARCHIVED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE atana_gen_model AS ENUM ('SPATIAL','SYSTEM','SITE','DOCUMENT','SPACE'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE atana_rule_type AS ENUM ('SYSTEM','ASSET','SPACE','STAGE','OPTIONAL','DEPENDENCY'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE atana_gen_status AS ENUM ('MANDATORY','OPTIONAL','PROJECT_MANDATORY','USER_ADDED','USER_REMOVED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE atana_authority AS ENUM ('OWN','AUT','VFY','RVW','APR','PUB','TRN','GOV'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE atana_ir_level AS ENUM ('L1','L2','L3','L4'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ===== IDENTITY =====
CREATE TABLE IF NOT EXISTS organisations (
  org_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_code TEXT NOT NULL UNIQUE,
  org_name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organisations(org_id),
  entra_oid TEXT UNIQUE,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  UNIQUE (org_id, email)
);

CREATE TABLE IF NOT EXISTS projects (
  project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organisations(org_id),
  project_number TEXT NOT NULL,
  project_name TEXT NOT NULL,
  client_name TEXT,
  originator TEXT DEFAULT 'ATA',
  project_type TEXT,
  current_stage TEXT DEFAULT 'S3',
  status TEXT NOT NULL DEFAULT 'active',
  catalogue_version_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (org_id, project_number)
);
CREATE INDEX IF NOT EXISTS ix_projects_org ON projects(org_id);

-- ===== BREAKDOWNS =====
CREATE TABLE IF NOT EXISTS functional_breakdowns (
  fb_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  fb_code TEXT NOT NULL,
  fb_name TEXT NOT NULL,
  selected BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE (project_id, fb_code)
);

CREATE TABLE IF NOT EXISTS spatial_breakdowns (
  sl_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  sl_code TEXT NOT NULL,
  sl_name TEXT NOT NULL,
  selected BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE (project_id, sl_code)
);

CREATE TABLE IF NOT EXISTS delivery_stages (
  stage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  stage_code TEXT NOT NULL,
  stage_label TEXT NOT NULL,
  gate TEXT NOT NULL,
  lod TEXT,
  loi TEXT,
  suitability TEXT,
  start_date DATE,
  end_date DATE,
  sort_order INT NOT NULL DEFAULT 0,
  UNIQUE (project_id, stage_code)
);

-- ===== MASTER CATALOGUES =====
CREATE TABLE IF NOT EXISTS catalogue_versions (
  catalogue_version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES organisations(org_id),
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  status atana_status NOT NULL DEFAULT 'ACTIVE',
  approved_at TIMESTAMPTZ,
  approved_by UUID REFERENCES users(user_id),
  UNIQUE (org_id, name, version)
);

CREATE TABLE IF NOT EXISTS task_teams (
  ro_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES organisations(org_id),
  catalogue_version_id UUID REFERENCES catalogue_versions(catalogue_version_id),
  ro_code TEXT NOT NULL,
  ro_name TEXT NOT NULL,
  generation_model atana_gen_model NOT NULL DEFAULT 'SYSTEM',
  status atana_status NOT NULL DEFAULT 'ACTIVE',
  UNIQUE (org_id, ro_code)
);

CREATE TABLE IF NOT EXISTS functional_roles (
  fr_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fr_code TEXT NOT NULL UNIQUE,
  fr_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS systems (
  ss_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  catalogue_version_id UUID REFERENCES catalogue_versions(catalogue_version_id),
  ss_code TEXT NOT NULL,
  ss_name TEXT NOT NULL,
  owner_ro TEXT,
  status atana_status NOT NULL DEFAULT 'ACTIVE',
  UNIQUE (catalogue_version_id, ss_code)
);

CREATE TABLE IF NOT EXISTS assets (
  asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  catalogue_version_id UUID REFERENCES catalogue_versions(catalogue_version_id),
  asset_name TEXT NOT NULL,
  ss_id UUID REFERENCES systems(ss_id),
  owner_ro TEXT,
  status atana_status NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS spaces (
  space_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  catalogue_version_id UUID REFERENCES catalogue_versions(catalogue_version_id),
  sl_code TEXT NOT NULL,
  sl_name TEXT NOT NULL,
  status atana_status NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS information_containers (
  container_code TEXT PRIMARY KEY,
  form_code TEXT NOT NULL,
  default_series INT NOT NULL DEFAULT 0,
  label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deliverable_types (
  type_code TEXT PRIMARY KEY,
  container_code TEXT NOT NULL REFERENCES information_containers(container_code)
);

-- ===== PROJECT SCOPE =====
CREATE TABLE IF NOT EXISTS project_task_teams (
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  ro_id UUID NOT NULL REFERENCES task_teams(ro_id),
  selected BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (project_id, ro_id)
);

CREATE TABLE IF NOT EXISTS project_systems (
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  ss_id UUID NOT NULL REFERENCES systems(ss_id),
  PRIMARY KEY (project_id, ss_id)
);

CREATE TABLE IF NOT EXISTS project_assets (
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  asset_id UUID NOT NULL REFERENCES assets(asset_id),
  PRIMARY KEY (project_id, asset_id)
);

CREATE TABLE IF NOT EXISTS project_optionals (
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  subject TEXT NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (project_id, subject)
);

CREATE TABLE IF NOT EXISTS user_assignments (
  ua_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(user_id),
  ro_id UUID REFERENCES task_teams(ro_id),
  fr_id UUID NOT NULL REFERENCES functional_roles(fr_id)
);
CREATE INDEX IF NOT EXISTS ix_ua_project ON user_assignments(project_id);

-- ===== RULES =====
CREATE TABLE IF NOT EXISTS rules (
  rule_id TEXT PRIMARY KEY,
  catalogue_version_id UUID REFERENCES catalogue_versions(catalogue_version_id),
  rule_type atana_rule_type NOT NULL,
  trigger TEXT NOT NULL,
  role_code TEXT,
  subject TEXT,
  output_package TEXT,
  children TEXT[],
  version TEXT NOT NULL DEFAULT '1.0',
  status atana_status NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS rule_dependencies (
  dep_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_subject TEXT NOT NULL,
  child_subject TEXT NOT NULL,
  dep_type TEXT
);

CREATE TABLE IF NOT EXISTS overrides (
  override_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  level TEXT NOT NULL,
  object_key TEXT NOT NULL,
  value TEXT NOT NULL,
  UNIQUE (project_id, level, object_key)
);

-- ===== PACKAGES / GENERATION =====
CREATE TABLE IF NOT EXISTS production_packages (
  pp_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  fb_id UUID NOT NULL REFERENCES functional_breakdowns(fb_id),
  ss_id UUID REFERENCES systems(ss_id),
  owner_ro TEXT,
  UNIQUE (project_id, fb_id, ss_id)
);

CREATE TABLE IF NOT EXISTS generation_runs (
  run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  stage_code TEXT,
  catalogue_version_id UUID REFERENCES catalogue_versions(catalogue_version_id),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  container_count INT DEFAULT 0,
  created_by UUID REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS deliverables (
  del_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES generation_runs(run_id),
  project_id UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  ro_code TEXT NOT NULL,
  fb_code TEXT,
  sl_code TEXT,
  form_code TEXT NOT NULL,
  container_code TEXT REFERENCES information_containers(container_code),
  doc_number TEXT NOT NULL,
  iso_number TEXT NOT NULL,
  description TEXT NOT NULL,
  package_title TEXT,
  ir_level atana_ir_level,
  ir_geometry TEXT,
  ir_data TEXT,
  ir_docs TEXT,
  gen_status atana_gen_status NOT NULL DEFAULT 'MANDATORY',
  wf_state atana_info_state NOT NULL DEFAULT 'WIP',
  wf_author TEXT,
  wf_peer TEXT,
  wf_ttim TEXT,
  wf_ttm TEXT,
  triggered_by TEXT,
  generated_from TEXT,
  UNIQUE (project_id, iso_number)
);
CREATE INDEX IF NOT EXISTS ix_del_project_ro ON deliverables(project_id, ro_code);
CREATE INDEX IF NOT EXISTS ix_del_seq ON deliverables(project_id, ro_code, fb_code, sl_code, form_code);

CREATE TABLE IF NOT EXISTS workflow_transitions (
  trn_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  del_id UUID NOT NULL REFERENCES deliverables(del_id) ON DELETE CASCADE,
  from_state atana_info_state,
  to_state atana_info_state NOT NULL,
  actor_id UUID REFERENCES users(user_id),
  fr_code TEXT,
  reason TEXT,
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS information_requirements (
  ir_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  object_type TEXT NOT NULL,
  object_name TEXT NOT NULL,
  gate TEXT NOT NULL,
  ir_level atana_ir_level NOT NULL,
  geometry TEXT,
  data TEXT,
  documentation TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
  audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID,
  project_id UUID,
  user_id UUID,
  fr_code TEXT,
  object_type TEXT NOT NULL,
  object_id TEXT,
  action TEXT NOT NULL,
  old_value TEXT,
  new_value TEXT,
  reason TEXT,
  at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_audit_at ON audit_log(at);

-- Seed containers
INSERT INTO information_containers(container_code, form_code, default_series, label) VALUES
  ('DRAWING','DR',1000,'Drawing'),
  ('MODEL','M3',0,'Model'),
  ('REPORT','RP',0,'Report'),
  ('CALCULATION','CA',0,'Calculation'),
  ('SCHEDULE','SH',5000,'Schedule'),
  ('SPECIFICATION','SP',0,'Specification'),
  ('DATASHEET','DS',0,'Data sheet'),
  ('REGISTER','RG',0,'Register'),
  ('SCHEMATIC','SC',6000,'Schematic')
ON CONFLICT (container_code) DO NOTHING;

INSERT INTO functional_roles(fr_code, fr_name) VALUES
  ('DTL','Delivery Team Lead'),
  ('PDM','Project Delivery Manager'),
  ('IM','Information Manager'),
  ('DM','Document Manager'),
  ('TTM','Task Team Manager'),
  ('TTIM','Task Team Information Manager'),
  ('IA','Information Author'),
  ('PR','Peer Reviewer')
ON CONFLICT (fr_code) DO NOTHING;


-- =========================================================
-- v1.1 ADDITIONS: session context, RLS, seed, procedures
-- =========================================================

ALTER TABLE organisations ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active';
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_platform_admin BOOLEAN NOT NULL DEFAULT FALSE;

-- Session GUC helpers (set by API from Entra token)
CREATE OR REPLACE FUNCTION atana_current_org() RETURNS UUID
LANGUAGE sql STABLE AS $$
  SELECT NULLIF(current_setting('atana.org_id', true), '')::uuid
$$;

CREATE OR REPLACE FUNCTION atana_current_user() RETURNS UUID
LANGUAGE sql STABLE AS $$
  SELECT NULLIF(current_setting('atana.user_id', true), '')::uuid
$$;

CREATE OR REPLACE FUNCTION atana_is_platform_admin() RETURNS BOOLEAN
LANGUAGE sql STABLE AS $$
  SELECT COALESCE((SELECT is_platform_admin FROM users WHERE user_id = atana_current_user()), false)
$$;

-- Enable RLS on tenant tables
DO $$ DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY[
    'projects','functional_breakdowns','spatial_breakdowns','delivery_stages',
    'project_task_teams','project_systems','project_assets','project_optionals',
    'user_assignments','overrides','production_packages','generation_runs',
    'deliverables','workflow_transitions','audit_log'
  ]
  LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
  END LOOP;
END $$;

DROP POLICY IF EXISTS p_projects_org ON projects;
CREATE POLICY p_projects_org ON projects
  USING (org_id = atana_current_org() OR atana_is_platform_admin())
  WITH CHECK (org_id = atana_current_org() OR atana_is_platform_admin());

DROP POLICY IF EXISTS p_fb_org ON functional_breakdowns;
CREATE POLICY p_fb_org ON functional_breakdowns
  USING (project_id IN (SELECT project_id FROM projects WHERE org_id = atana_current_org()) OR atana_is_platform_admin());

DROP POLICY IF EXISTS p_sl_org ON spatial_breakdowns;
CREATE POLICY p_sl_org ON spatial_breakdowns
  USING (project_id IN (SELECT project_id FROM projects WHERE org_id = atana_current_org()) OR atana_is_platform_admin());

DROP POLICY IF EXISTS p_del_org ON deliverables;
CREATE POLICY p_del_org ON deliverables
  USING (project_id IN (SELECT project_id FROM projects WHERE org_id = atana_current_org()) OR atana_is_platform_admin());

DROP POLICY IF EXISTS p_run_org ON generation_runs;
CREATE POLICY p_run_org ON generation_runs
  USING (project_id IN (SELECT project_id FROM projects WHERE org_id = atana_current_org()) OR atana_is_platform_admin());

DROP POLICY IF EXISTS p_audit_org ON audit_log;
CREATE POLICY p_audit_org ON audit_log
  USING (org_id = atana_current_org() OR atana_is_platform_admin());

-- Generic audit writer
CREATE OR REPLACE FUNCTION atana_write_audit(
  p_project UUID, p_object_type TEXT, p_object_id TEXT,
  p_action TEXT, p_old TEXT, p_new TEXT, p_reason TEXT
) RETURNS UUID
LANGUAGE plpgsql AS $$
DECLARE id UUID;
BEGIN
  INSERT INTO audit_log(org_id, project_id, user_id, object_type, object_id, action, old_value, new_value, reason)
  VALUES (atana_current_org(), p_project, atana_current_user(), p_object_type, p_object_id, p_action, p_old, p_new, p_reason)
  RETURNING audit_id INTO id;
  RETURN id;
END $$;

-- Number allocation: restart per originator+role+fb+spatial+form
CREATE OR REPLACE FUNCTION atana_next_number(
  p_project UUID, p_originator TEXT, p_role TEXT, p_fb TEXT, p_sl TEXT, p_form TEXT, p_start INT DEFAULT 1001
) RETURNS TEXT
LANGUAGE plpgsql AS $$
DECLARE n INT;
BEGIN
  CREATE TABLE IF NOT EXISTS number_counters (
    project_id UUID NOT NULL,
    originator TEXT NOT NULL,
    ro_code TEXT NOT NULL,
    fb_code TEXT NOT NULL,
    sl_code TEXT NOT NULL,
    form_code TEXT NOT NULL,
    last_number INT NOT NULL,
    PRIMARY KEY (project_id, originator, ro_code, fb_code, sl_code, form_code)
  );
  INSERT INTO number_counters(project_id, originator, ro_code, fb_code, sl_code, form_code, last_number)
  VALUES (p_project, p_originator, p_role, COALESCE(p_fb,''), COALESCE(p_sl,''), p_form, p_start)
  ON CONFLICT (project_id, originator, ro_code, fb_code, sl_code, form_code)
  DO UPDATE SET last_number = number_counters.last_number + 1
  RETURNING last_number INTO n;
  RETURN lpad(n::text, 4, '0');
END $$;

-- Mark USER_REMOVED
CREATE OR REPLACE FUNCTION atana_refine_deliverable(p_del UUID, p_remove BOOLEAN)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
  UPDATE deliverables
     SET gen_status = CASE WHEN p_remove THEN 'USER_REMOVED'::atana_gen_status ELSE 'MANDATORY'::atana_gen_status END
   WHERE del_id = p_del;
  PERFORM atana_write_audit(
    (SELECT project_id FROM deliverables WHERE del_id = p_del),
    'deliverable', p_del::text,
    CASE WHEN p_remove THEN 'USER_REMOVED' ELSE 'RESTORE' END,
    NULL, p_remove::text, 'refine'
  );
END $$;

-- Legal workflow transition
CREATE OR REPLACE FUNCTION atana_transition(p_del UUID, p_to atana_info_state, p_reason TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE cur atana_info_state;
BEGIN
  SELECT wf_state INTO cur FROM deliverables WHERE del_id = p_del FOR UPDATE;
  IF cur IS NULL THEN RAISE EXCEPTION 'deliverable not found'; END IF;
  INSERT INTO workflow_transitions(del_id, from_state, to_state, actor_id, reason)
  VALUES (p_del, cur, p_to, atana_current_user(), p_reason);
  UPDATE deliverables SET wf_state = p_to WHERE del_id = p_del;
  PERFORM atana_write_audit(
    (SELECT project_id FROM deliverables WHERE del_id = p_del),
    'deliverable', p_del::text, 'TRANSITION', cur::text, p_to::text, p_reason
  );
END $$;

-- Reporting views (Power BI)
CREATE OR REPLACE VIEW vw_midp_active AS
SELECT d.project_id, d.ro_code, d.fb_code, d.sl_code, d.form_code, d.container_code,
       d.iso_number, d.description, d.package_title, d.ir_level, d.gen_status, d.wf_state
FROM deliverables d
WHERE d.gen_status <> 'USER_REMOVED';

CREATE OR REPLACE VIEW vw_package_counts AS
SELECT project_id, ro_code, package_title, count(*) AS containers,
       count(*) FILTER (WHERE wf_state = 'PUBLISHED') AS published,
       count(*) FILTER (WHERE wf_state = 'WIP') AS wip
FROM vw_midp_active
GROUP BY 1,2,3;

-- Seed reference
INSERT INTO information_containers(container_code, form_code, default_series, label) VALUES
  ('DRAWING','DR',1000,'Drawing'),
  ('MODEL','M3',0,'Model'),
  ('REPORT','RP',0,'Report'),
  ('CALCULATION','CA',0,'Calculation'),
  ('SCHEDULE','SH',5000,'Schedule'),
  ('SPECIFICATION','SP',0,'Specification'),
  ('DATASHEET','DS',0,'Data sheet'),
  ('REGISTER','RG',0,'Register'),
  ('SCHEMATIC','SC',6000,'Schematic')
ON CONFLICT (container_code) DO NOTHING;

INSERT INTO deliverable_types(type_code, container_code) VALUES
  ('PLAN','DRAWING'),('LAYOUT','DRAWING'),('ELEVATION','DRAWING'),('SECTION','DRAWING'),('DETAIL','DRAWING'),
  ('SCHEDULE','SCHEDULE'),('SCHEMATIC','SCHEMATIC'),('REPORT','REPORT'),('CALCULATION','CALCULATION'),
  ('SPECIFICATION','SPECIFICATION'),('DATA SHEET','DATASHEET'),('REGISTER','REGISTER'),('MATRIX','REGISTER'),
  ('MODEL','MODEL')
ON CONFLICT (type_code) DO NOTHING;

INSERT INTO functional_roles(fr_code, fr_name) VALUES
  ('DTL','Delivery Team Lead'),('PDM','Project Delivery Manager'),('IM','Information Manager'),
  ('DM','Document Manager'),('TTM','Task Team Manager'),('TTIM','Task Team Information Manager'),
  ('IA','Information Author'),('PR','Peer Reviewer'),
  ('CON-CM','Construction Manager'),('CON-RE','Resident Engineer')
ON CONFLICT (fr_code) DO NOTHING;

INSERT INTO organisations(org_code, org_name)
VALUES ('ATA','Atana')
ON CONFLICT (org_code) DO NOTHING;

INSERT INTO task_teams(org_id, ro_code, ro_name, generation_model)
SELECT o.org_id, x.code, x.name, x.model::atana_gen_model
FROM organisations o
CROSS JOIN (VALUES
  ('AR','ARCHITECTURE','SPATIAL'),
  ('ST','STRUCTURAL','SPATIAL'),
  ('CV','CIVIL','SITE'),
  ('CW','CIVIL WATER','SITE'),
  ('HD','DRAINAGE','SITE'),
  ('HB','BRIDGES','SITE'),
  ('LA','LANDSCAPING','SITE'),
  ('EE','ELECTRICAL','SYSTEM'),
  ('ME','MECHANICAL','SYSTEM'),
  ('HE','HYDRAULIC','SYSTEM'),
  ('FD','FIRE DETECTION','SYSTEM'),
  ('FP','FIRE PROTECTION','SYSTEM'),
  ('YS','SECURITY SPECIALIST','SYSTEM'),
  ('YC','CONTROLS ENGINEER','DOCUMENT'),
  ('PE','PROCESS ENGINEER','DOCUMENT'),
  ('EV','ENVIRONMENTAL','DOCUMENT'),
  ('ID','INTERIOR DESIGN','SPACE')
) AS x(code,name,model)
WHERE o.org_code = 'ATA'
ON CONFLICT (org_id, ro_code) DO NOTHING;

INSERT INTO rules(rule_id, rule_type, trigger, role_code, subject, output_package, children) VALUES
  ('ME-HVAC-001','SYSTEM','SYSTEM_EXISTS','ME','HVAC','HVAC PACKAGE','{"HVAC CALCULATIONS"}'),
  ('EE-LIGHT-001','SYSTEM','SYSTEM_EXISTS','EE','LIGHTING','LIGHTING PACKAGE',NULL),
  ('FD-DET-001','SYSTEM','SYSTEM_EXISTS','FD','FIRE DETECTION','FIRE DETECTION PACKAGE','{"CAUSE AND EFFECT MATRIX"}'),
  ('ST-CONC-001','ASSET','ASSET_EXISTS','ST','CONCRETE','CONCRETE PACKAGE','{"REINFORCEMENT"}'),
  ('FD-VESDA-001','OPTIONAL','OPTIONAL_ENABLED','FD','VESDA','VESDA PACKAGE',NULL)
ON CONFLICT (rule_id) DO NOTHING;
