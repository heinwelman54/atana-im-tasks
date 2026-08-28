-- Atana PDS v1.0

-- Atana Physical Database Schema (PDS) v1.0
-- Target: PostgreSQL 14+
-- Source: ACDM Phase 11 → PDS Phase 12
-- Principle: Production Package = FB + Ss (unique). Workstages are maturity rows, not new packages.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ========== ENUMERATIONS ==========
DO $$ BEGIN
  CREATE TYPE atana_info_state AS ENUM ('WIP','SHARED','PUBLISHED','ARCHIVED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE atana_dep_strength AS ENUM ('C','M','m');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE atana_verification_result AS ENUM ('pending','pass','warning','fail');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ========== DOMAIN 1: REFERENCE ==========
CREATE TABLE IF NOT EXISTS projects (
  project_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_number    TEXT NOT NULL,
  project_name      TEXT NOT NULL,
  status            TEXT NOT NULL DEFAULT 'active',
  originator        TEXT,
  client_name       TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (project_number)
);

CREATE TABLE IF NOT EXISTS functional_breakdowns (
  fb_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id        UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  fb_code           TEXT NOT NULL,
  fb_name           TEXT NOT NULL,
  fb_type           TEXT,
  UNIQUE (project_id, fb_code)
);
CREATE INDEX IF NOT EXISTS ix_fb_project ON functional_breakdowns(project_id);

CREATE TABLE IF NOT EXISTS systems (
  ss_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ss_code           TEXT NOT NULL UNIQUE,
  ss_name           TEXT NOT NULL,
  description       TEXT
);

CREATE TABLE IF NOT EXISTS spatial_breakdowns (
  sl_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id        UUID REFERENCES projects(project_id) ON DELETE CASCADE,
  sl_code           TEXT NOT NULL,
  sl_name           TEXT NOT NULL,
  UNIQUE (project_id, sl_code)
);

CREATE TABLE IF NOT EXISTS products (
  pr_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pr_code           TEXT NOT NULL UNIQUE,
  pr_name           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS elements_functions (
  ef_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ef_code           TEXT NOT NULL UNIQUE,
  ef_name           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS forms_of_information (
  fi_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fi_code           TEXT NOT NULL UNIQUE,
  fi_name           TEXT NOT NULL
);

-- ========== DOMAIN 2: GOVERNANCE ==========
CREATE TABLE IF NOT EXISTS task_teams (
  ro_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id        UUID REFERENCES projects(project_id) ON DELETE CASCADE,
  ro_code           TEXT NOT NULL,
  ro_name           TEXT NOT NULL,
  UNIQUE (project_id, ro_code)
);

CREATE TABLE IF NOT EXISTS functional_roles (
  fr_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_code         TEXT NOT NULL UNIQUE,
  role_name         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS authorities (
  auth_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  authority_code    TEXT NOT NULL UNIQUE,
  authority_name    TEXT NOT NULL
);

-- ========== DOMAIN 3: PRODUCTION ==========
CREATE TABLE IF NOT EXISTS production_packages (
  pp_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id        UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  fb_id             UUID NOT NULL REFERENCES functional_breakdowns(fb_id),
  ss_id             UUID NOT NULL REFERENCES systems(ss_id),
  ro_id             UUID REFERENCES task_teams(ro_id),
  status            TEXT NOT NULL DEFAULT 'not_started',
  current_lod       TEXT,
  current_loi       TEXT,
  target_lod        TEXT,
  target_loi        TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at         TIMESTAMPTZ,
  UNIQUE (fb_id, ss_id)
);
CREATE INDEX IF NOT EXISTS ix_pp_fb ON production_packages(fb_id);
CREATE INDEX IF NOT EXISTS ix_pp_ss ON production_packages(ss_id);
CREATE INDEX IF NOT EXISTS ix_pp_project ON production_packages(project_id);

CREATE TABLE IF NOT EXISTS production_package_workstages (
  ppws_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pp_id             UUID NOT NULL REFERENCES production_packages(pp_id) ON DELETE CASCADE,
  workstage         TEXT NOT NULL,
  target_lod        TEXT,
  target_loi        TEXT,
  documentation_need TEXT,
  status            TEXT NOT NULL DEFAULT 'planned',
  UNIQUE (pp_id, workstage)
);

-- ========== DOMAIN 4: TIDP ==========
CREATE TABLE IF NOT EXISTS activities (
  act_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  activity_code     TEXT NOT NULL UNIQUE,
  activity_name     TEXT NOT NULL,
  activity_category TEXT
);

CREATE TABLE IF NOT EXISTS air_requirements (
  air_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  air_code          TEXT,
  air_type          TEXT NOT NULL,
  description       TEXT
);

CREATE TABLE IF NOT EXISTS tidp_rows (
  tr_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pp_id             UUID NOT NULL REFERENCES production_packages(pp_id) ON DELETE CASCADE,
  ppws_id           UUID REFERENCES production_package_workstages(ppws_id),
  act_id            UUID REFERENCES activities(act_id),
  air_id            UUID REFERENCES air_requirements(air_id),
  workstage         TEXT,
  status            TEXT NOT NULL DEFAULT 'created',
  func_role         TEXT,
  authority         TEXT,
  baseline_start    DATE,
  baseline_finish   DATE,
  forecast_start    DATE,
  forecast_finish   DATE,
  actual_start      DATE,
  actual_finish     DATE
);
CREATE INDEX IF NOT EXISTS ix_tr_pp ON tidp_rows(pp_id);

-- ========== DOMAIN 5: DEPENDENCIES ==========
CREATE TABLE IF NOT EXISTS dependencies (
  dep_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_pp_id      UUID NOT NULL REFERENCES production_packages(pp_id) ON DELETE CASCADE,
  target_pp_id      UUID NOT NULL REFERENCES production_packages(pp_id) ON DELETE CASCADE,
  dependency_type   TEXT NOT NULL,
  dependency_strength TEXT NOT NULL DEFAULT 'C',
  required_lod      TEXT,
  required_loi      TEXT,
  status            TEXT NOT NULL DEFAULT 'active',
  UNIQUE (source_pp_id, target_pp_id, dependency_type)
);
CREATE INDEX IF NOT EXISTS ix_dep_pair ON dependencies(source_pp_id, target_pp_id);

CREATE TABLE IF NOT EXISTS dependency_readiness (
  dep_ready_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dep_id            UUID NOT NULL REFERENCES dependencies(dep_id) ON DELETE CASCADE,
  readiness         TEXT NOT NULL,
  calculated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========== DOMAIN 6: INTERFACES ==========
CREATE TABLE IF NOT EXISTS interface_objects (
  if_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_pp_id      UUID NOT NULL REFERENCES production_packages(pp_id) ON DELETE CASCADE,
  target_pp_id      UUID NOT NULL REFERENCES production_packages(pp_id) ON DELETE CASCADE,
  interface_type    TEXT NOT NULL,
  owner_pp_id       UUID REFERENCES production_packages(pp_id),
  status            TEXT NOT NULL DEFAULT 'IFS00',
  readiness         TEXT NOT NULL DEFAULT 'IR0',
  required_lod      TEXT,
  required_loi      TEXT
);
CREATE INDEX IF NOT EXISTS ix_if_pair ON interface_objects(source_pp_id, target_pp_id);

CREATE TABLE IF NOT EXISTS interface_issues (
  iss_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  if_id             UUID NOT NULL REFERENCES interface_objects(if_id) ON DELETE CASCADE,
  title             TEXT NOT NULL,
  description       TEXT,
  priority          TEXT,
  status            TEXT NOT NULL DEFAULT 'open'
);
CREATE INDEX IF NOT EXISTS ix_iss_if ON interface_issues(if_id);

CREATE TABLE IF NOT EXISTS interface_packages (
  ifp_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              TEXT NOT NULL,
  description       TEXT
);

CREATE TABLE IF NOT EXISTS interface_package_members (
  ifpm_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ifp_id            UUID NOT NULL REFERENCES interface_packages(ifp_id) ON DELETE CASCADE,
  if_id             UUID NOT NULL REFERENCES interface_objects(if_id) ON DELETE CASCADE,
  UNIQUE (ifp_id, if_id)
);

-- ========== DOMAIN 7: MODELS ==========
CREATE TABLE IF NOT EXISTS model_packages (
  mp_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pp_id             UUID NOT NULL UNIQUE REFERENCES production_packages(pp_id) ON DELETE CASCADE,
  current_lod       TEXT,
  current_loi       TEXT,
  mri               NUMERIC(5,2),
  verification_status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS model_objects (
  mo_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mp_id             UUID NOT NULL REFERENCES model_packages(mp_id) ON DELETE CASCADE,
  external_id       TEXT NOT NULL,
  source_system     TEXT NOT NULL,
  fb_id             UUID REFERENCES functional_breakdowns(fb_id),
  ss_id             UUID REFERENCES systems(ss_id),
  pr_id             UUID REFERENCES products(pr_id),
  ef_id             UUID REFERENCES elements_functions(ef_id),
  last_sync         TIMESTAMPTZ,
  UNIQUE (source_system, external_id)
);
CREATE INDEX IF NOT EXISTS ix_mo_mp ON model_objects(mp_id);

CREATE TABLE IF NOT EXISTS verification_records (
  vr_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mp_id             UUID NOT NULL REFERENCES model_packages(mp_id) ON DELETE CASCADE,
  verification_type TEXT NOT NULL,
  result            TEXT NOT NULL DEFAULT 'pending',
  verifier          TEXT,
  checked_at        TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS search_sets (
  search_set_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mp_id             UUID REFERENCES model_packages(mp_id) ON DELETE CASCADE,
  name              TEXT NOT NULL,
  fb_code           TEXT,
  ss_code           TEXT,
  filter_expr       TEXT
);

CREATE TABLE IF NOT EXISTS clash_rules (
  clash_rule_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  if_id             UUID REFERENCES interface_objects(if_id) ON DELETE SET NULL,
  name              TEXT NOT NULL,
  search_set_a      UUID REFERENCES search_sets(search_set_id),
  search_set_b      UUID REFERENCES search_sets(search_set_id),
  status            TEXT DEFAULT 'defined'
);

-- ========== DOMAIN 8: INFORMATION ==========
CREATE TABLE IF NOT EXISTS deliverables (
  del_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id        UUID REFERENCES projects(project_id) ON DELETE CASCADE,
  container_name    TEXT NOT NULL,
  fi_id             UUID REFERENCES forms_of_information(fi_id),
  sl_id             UUID REFERENCES spatial_breakdowns(sl_id),
  suitability       TEXT,
  revision          TEXT,
  state             TEXT NOT NULL DEFAULT 'WIP'
);
CREATE INDEX IF NOT EXISTS ix_del_project ON deliverables(project_id);

CREATE TABLE IF NOT EXISTS deliverable_production_links (
  dpl_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  del_id            UUID NOT NULL REFERENCES deliverables(del_id) ON DELETE CASCADE,
  pp_id             UUID NOT NULL REFERENCES production_packages(pp_id) ON DELETE CASCADE,
  UNIQUE (del_id, pp_id)
);

CREATE TABLE IF NOT EXISTS information_packages (
  ip_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id        UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
  workstage         TEXT NOT NULL,
  fb_id             UUID REFERENCES functional_breakdowns(fb_id),
  ro_id             UUID REFERENCES task_teams(ro_id),
  state             TEXT NOT NULL DEFAULT 'IPS00',
  suitability       TEXT,
  revision          TEXT,
  iri               NUMERIC(5,2)
);
CREATE INDEX IF NOT EXISTS ix_ip_ws_fb ON information_packages(workstage, fb_id);

CREATE TABLE IF NOT EXISTS information_package_members (
  ipm_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ip_id             UUID NOT NULL REFERENCES information_packages(ip_id) ON DELETE CASCADE,
  del_id            UUID NOT NULL REFERENCES deliverables(del_id) ON DELETE CASCADE,
  UNIQUE (ip_id, del_id)
);
CREATE INDEX IF NOT EXISTS ix_ipm_ip_del ON information_package_members(ip_id, del_id);

CREATE TABLE IF NOT EXISTS exchange_events (
  ex_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ip_id             UUID NOT NULL REFERENCES information_packages(ip_id) ON DELETE CASCADE,
  sender            TEXT,
  recipient         TEXT,
  purpose           TEXT,
  event_date        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========== DOMAIN 9: LOIN ==========
CREATE TABLE IF NOT EXISTS loin_requirements (
  loin_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workstage         TEXT NOT NULL,
  target_lod        TEXT,
  target_loi        TEXT
);

CREATE TABLE IF NOT EXISTS documentation_needs (
  dn_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  loin_id           UUID NOT NULL REFERENCES loin_requirements(loin_id) ON DELETE CASCADE,
  fi_id             UUID NOT NULL REFERENCES forms_of_information(fi_id),
  required          BOOLEAN NOT NULL DEFAULT true
);

-- ========== DOMAIN 10: AUTOMATION ==========
CREATE TABLE IF NOT EXISTS events (
  ev_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type        TEXT NOT NULL,
  object_type       TEXT,
  object_id         TEXT,
  project_id        UUID REFERENCES projects(project_id) ON DELETE SET NULL,
  ts                TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_type ON events(event_type);

CREATE TABLE IF NOT EXISTS automation_rules (
  rule_id           TEXT PRIMARY KEY,
  trigger_event     TEXT NOT NULL,
  condition_expr    TEXT,
  action_code       TEXT NOT NULL,
  enabled           BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS rule_execution_history (
  reh_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_id           TEXT REFERENCES automation_rules(rule_id),
  ev_id             UUID REFERENCES events(ev_id),
  result            TEXT,
  ts                TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========== DOMAIN 11: SECURITY ==========
CREATE TABLE IF NOT EXISTS users (
  user_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              TEXT NOT NULL,
  email             TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS user_assignments (
  ua_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  ro_id             UUID REFERENCES task_teams(ro_id),
  fr_id             UUID REFERENCES functional_roles(fr_id),
  project_id        UUID REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS permissions (
  perm_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  authority         TEXT NOT NULL,
  object_type       TEXT NOT NULL,
  role_code         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
  audit_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID REFERENCES users(user_id),
  object_type       TEXT,
  object_id         TEXT,
  old_value         JSONB,
  new_value         JSONB,
  ts                TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========== DOMAIN 12: METRICS ==========
CREATE TABLE IF NOT EXISTS readiness_records (
  ready_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pp_id             UUID NOT NULL REFERENCES production_packages(pp_id) ON DELETE CASCADE,
  production_readiness NUMERIC(5,2),
  dependency_readiness NUMERIC(5,2),
  interface_readiness  NUMERIC(5,2),
  loin_readiness       NUMERIC(5,2),
  calculated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS asset_readiness (
  ari_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fb_id             UUID NOT NULL REFERENCES functional_breakdowns(fb_id) ON DELETE CASCADE,
  ari_score         NUMERIC(5,2),
  calculated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS information_readiness (
  iri_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ip_id             UUID NOT NULL REFERENCES information_packages(ip_id) ON DELETE CASCADE,
  iri_score         NUMERIC(5,2),
  calculated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_readiness (
  mri_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mp_id             UUID NOT NULL REFERENCES model_packages(mp_id) ON DELETE CASCADE,
  mri_score         NUMERIC(5,2),
  calculated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed functional roles & authorities
INSERT INTO functional_roles (role_code, role_name) VALUES
  ('DTL','Delivery Team Lead'),('PDM','Project Delivery Manager'),('IM','Information Manager'),
  ('TTM','Task Team Manager'),('TTIM','Task Team Information Manager'),('IA','Information Author'),('PR','Peer Reviewer')
ON CONFLICT (role_code) DO NOTHING;

INSERT INTO authorities (authority_code, authority_name) VALUES
  ('OWN','Own'),('AUT','Author'),('VFY','Verify'),('RVW','Review'),
  ('APR','Approve'),('PUB','Publish'),('TRN','Transmit'),('GOV','Govern')
ON CONFLICT (authority_code) DO NOTHING;

INSERT INTO activities (activity_code, activity_name, activity_category) VALUES
  ('Plan','Plan','PLN'),('Model','Model','AUT'),('Document','Document','AUT'),
  ('Coordinate','Coordinate','CRD'),('Verify','Verify','VFY'),('Review','Review','APR'),('Approve','Approve','APR')
ON CONFLICT (activity_code) DO NOTHING;

-- Atana DGE v1 — Generation Models (extend PDS)
CREATE TABLE IF NOT EXISTS GenerationModels (
  Model_ID   TEXT PRIMARY KEY,
  Code       TEXT NOT NULL UNIQUE,
  Pattern    TEXT NOT NULL,
  Description TEXT
);
INSERT INTO GenerationModels (Model_ID, Code, Pattern, Description) VALUES
  ('GM-SPATIAL', 'SPATIAL', '[SPATIAL BREAKDOWN] [DELIVERABLE]', 'Architecture / structure by storey'),
  ('GM-SYSTEM', 'SYSTEM', '[SYSTEM] [DELIVERABLE] - [SPATIAL BREAKDOWN]', 'Building services by system'),
  ('GM-SITE', 'SITE', '[SYSTEM/ASSET] [DELIVERABLE] - [SPATIAL BREAKDOWN]', 'Site infrastructure'),
  ('GM-DOCUMENT', 'DOCUMENT', '[SUBJECT] [DOCUMENT TYPE]', 'Reports and schedules'),
  ('GM-SPACE', 'SPACE', '[SPACE] [DELIVERABLE]', 'Fit-out / interiors')
ON CONFLICT (Code) DO NOTHING;

ALTER TABLE TaskTeams ADD COLUMN IF NOT EXISTS Generation_Model TEXT REFERENCES GenerationModels(Code);
ALTER TABLE TaskTeams ADD COLUMN IF NOT EXISTS Generation_Subjects TEXT;

CREATE TABLE IF NOT EXISTS DgeSystems (
  SS_ID TEXT PRIMARY KEY,
  Code TEXT NOT NULL,
  Name TEXT NOT NULL,
  Uniclass_Ss TEXT,
  Default_Ro TEXT
);
CREATE TABLE IF NOT EXISTS DgeAssets (
  Asset_ID TEXT PRIMARY KEY,
  Code TEXT NOT NULL,
  Name TEXT NOT NULL,
  Default_Ro TEXT
);
CREATE TABLE IF NOT EXISTS DgeSpaces (
  Space_ID TEXT PRIMARY KEY,
  Code TEXT NOT NULL,
  Name TEXT NOT NULL,
  Uniclass_Sl TEXT
);
CREATE TABLE IF NOT EXISTS GenerationRules (
  Rule_ID TEXT PRIMARY KEY,
  Model TEXT NOT NULL REFERENCES GenerationModels(Code),
  Deliverable_Type TEXT NOT NULL,
  Form TEXT,
  Series INTEGER,
  Scope TEXT,
  Title_Pattern TEXT NOT NULL,
  Mandatory INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS GeneratedDeliverables (
  DEL_ID TEXT PRIMARY KEY,
  Project_ID TEXT,
  Task_Team TEXT,
  Model TEXT,
  Spatial_Code TEXT,
  Spatial_Label TEXT,
  System_Name TEXT,
  Asset_Name TEXT,
  Space_Name TEXT,
  Title TEXT NOT NULL,
  Form TEXT,
  Number TEXT
);

CREATE TABLE IF NOT EXISTS DeliverablePackages (
  PKG_ID TEXT PRIMARY KEY,
  Project_ID TEXT,
  Task_Team TEXT,
  Model TEXT,
  Package_Type TEXT,
  Subject TEXT,
  Title TEXT
);
CREATE TABLE IF NOT EXISTS PackageItems (
  ITEM_ID TEXT PRIMARY KEY,
  PKG_ID TEXT REFERENCES DeliverablePackages(PKG_ID),
  Deliverable_Type TEXT,
  Title_Pattern TEXT,
  Form TEXT,
  Scope TEXT,
  Stage_Concept TEXT,
  Stage_Preliminary TEXT,
  Stage_Detailed TEXT,
  Stage_Tender TEXT,
  Stage_Construction TEXT,
  Stage_AsBuilt TEXT,
  LOD TEXT,
  LOI TEXT
);

CREATE TABLE IF NOT EXISTS DeliveryFrameworks (
  FW_ID TEXT PRIMARY KEY,
  Project_ID TEXT,
  Version TEXT
);
CREATE TABLE IF NOT EXISTS DeliveryStages (
  Stage_Row_ID TEXT PRIMARY KEY,
  Project_ID TEXT,
  Stage_ID TEXT,
  Gate TEXT,
  Label TEXT,
  LOD INTEGER,
  LOI INTEGER,
  Suitability TEXT,
  Info_State TEXT
);
CREATE TABLE IF NOT EXISTS DeliverableApplicability (
  APP_ID TEXT PRIMARY KEY,
  Rule_Or_Item_ID TEXT,
  Gate TEXT,
  Applicability TEXT,
  Mandatory INTEGER
);

CREATE TABLE IF NOT EXISTS DecisionRules (
  Rule_ID TEXT PRIMARY KEY,
  Rule_Type TEXT,
  Trigger TEXT,
  Role_Code TEXT,
  Subject TEXT,
  Output_Package TEXT,
  Conditions TEXT
);
CREATE TABLE IF NOT EXISTS DecisionDependencies (
  DEP_ID TEXT PRIMARY KEY,
  Parent_Subject TEXT,
  Child_Subject TEXT,
  Dep_Type TEXT
);

CREATE TABLE IF NOT EXISTS GovernanceAudit (
  AUDIT_ID TEXT PRIMARY KEY,
  Project_ID TEXT,
  Who TEXT,
  Action TEXT,
  Object TEXT,
  Why TEXT,
  Old_Value TEXT,
  New_Value TEXT,
  At TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS CatalogueEntries (
  CAT_ID TEXT PRIMARY KEY,
  Catalogue TEXT,
  Name TEXT,
  Status TEXT,
  Version TEXT,
  Owner TEXT,
  Approved TEXT
);

CREATE TABLE IF NOT EXISTS InformationContainers (
  Container_Code TEXT PRIMARY KEY,
  Form_Code TEXT,
  Default_Series INTEGER,
  Label TEXT
);
CREATE TABLE IF NOT EXISTS DeliverableTypeMap (
  Deliverable_Type TEXT PRIMARY KEY,
  Container_Code TEXT REFERENCES InformationContainers(Container_Code)
);

CREATE TABLE IF NOT EXISTS InformationRequirements (
  IR_ID TEXT PRIMARY KEY,
  Object_Type TEXT,
  Object_Name TEXT,
  Gate TEXT,
  IR_Level TEXT,
  Geometry TEXT,
  Data TEXT,
  Documentation TEXT
);
