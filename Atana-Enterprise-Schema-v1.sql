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
