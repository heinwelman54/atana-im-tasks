-- Atana Executive Command Center analytics schema v1.0
-- Companion to docs/COMMAND-CENTER.md
-- Does not replace PDS. Schema ecc is read-mostly snapshots.

CREATE SCHEMA IF NOT EXISTS ecc;

-- Optional portfolio grain on existing PDS projects (no second project table).
ALTER TABLE projects ADD COLUMN IF NOT EXISTS portfolio_id UUID;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS weight NUMERIC(12,4) NOT NULL DEFAULT 1;

CREATE TABLE IF NOT EXISTS ecc.score_weight (
  score_version     TEXT PRIMARY KEY,
  ih_oir            NUMERIC(5,4) NOT NULL DEFAULT 0.15,
  ih_pir            NUMERIC(5,4) NOT NULL DEFAULT 0.15,
  ih_eir            NUMERIC(5,4) NOT NULL DEFAULT 0.15,
  ih_air            NUMERIC(5,4) NOT NULL DEFAULT 0.20,
  ih_aim            NUMERIC(5,4) NOT NULL DEFAULT 0.20,
  ih_ids            NUMERIC(5,4) NOT NULL DEFAULT 0.15,
  dh_ontime         NUMERIC(5,4) NOT NULL DEFAULT 0.40,
  dh_pub            NUMERIC(5,4) NOT NULL DEFAULT 0.30,
  dh_pkg            NUMERIC(5,4) NOT NULL DEFAULT 0.30,
  ph_ih             NUMERIC(5,4) NOT NULL DEFAULT 0.30,
  ph_dh             NUMERIC(5,4) NOT NULL DEFAULT 0.25,
  ph_cs             NUMERIC(5,4) NOT NULL DEFAULT 0.20,
  ph_risk           NUMERIC(5,4) NOT NULL DEFAULT 0.15,
  ph_wf             NUMERIC(5,4) NOT NULL DEFAULT 0.10,
  or_aim5           NUMERIC(5,4) NOT NULL DEFAULT 0.40,
  or_cmms           NUMERIC(5,4) NOT NULL DEFAULT 0.20,
  or_twin           NUMERIC(5,4) NOT NULL DEFAULT 0.20,
  or_opsdocs        NUMERIC(5,4) NOT NULL DEFAULT 0.20,
  tr_ident          NUMERIC(5,4) NOT NULL DEFAULT 0.25,
  tr_ifc            NUMERIC(5,4) NOT NULL DEFAULT 0.25,
  tr_cobie          NUMERIC(5,4) NOT NULL DEFAULT 0.20,
  tr_aim            NUMERIC(5,4) NOT NULL DEFAULT 0.20,
  tr_bind           NUMERIC(5,4) NOT NULL DEFAULT 0.10,
  risk_norm         NUMERIC(8,2) NOT NULL DEFAULT 12,
  active            BOOLEAN NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO ecc.score_weight (score_version) VALUES ('1.0')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS ecc.req_coverage (
  project_id        UUID NOT NULL,
  as_of             TIMESTAMPTZ NOT NULL,
  oir_req           INTEGER NOT NULL,
  oir_ok            INTEGER NOT NULL,
  pir_req           INTEGER NOT NULL,
  pir_ok            INTEGER NOT NULL,
  eir_req           INTEGER NOT NULL,
  eir_ok            INTEGER NOT NULL,
  air_req           INTEGER NOT NULL,
  air_ok            INTEGER NOT NULL,
  PRIMARY KEY (project_id, as_of)
);

CREATE TABLE IF NOT EXISTS ecc.asset_score (
  project_id        UUID NOT NULL,
  asset_id          UUID NOT NULL,
  as_of             TIMESTAMPTZ NOT NULL,
  loi               INTEGER NOT NULL,
  present           INTEGER NOT NULL,
  required          INTEGER NOT NULL,
  aim_pct           NUMERIC(6,2) NOT NULL,
  ids_pass          BOOLEAN,
  has_ifcguid       BOOLEAN NOT NULL DEFAULT FALSE,
  has_cmms          BOOLEAN NOT NULL DEFAULT FALSE,
  has_twin          BOOLEAN NOT NULL DEFAULT FALSE,
  has_element_id    BOOLEAN NOT NULL DEFAULT FALSE,
  missing           TEXT[] NOT NULL DEFAULT '{}',
  PRIMARY KEY (project_id, asset_id, as_of, loi)
);
CREATE INDEX IF NOT EXISTS ix_ecc_asset_latest ON ecc.asset_score (project_id, asset_id, loi, as_of DESC);

CREATE TABLE IF NOT EXISTS ecc.project_score (
  project_id        UUID NOT NULL,
  as_of             TIMESTAMPTZ NOT NULL,
  stage             TEXT NOT NULL,
  score_version     TEXT NOT NULL REFERENCES ecc.score_weight(score_version),
  oir_cov           NUMERIC(6,4) NOT NULL,
  pir_cov           NUMERIC(6,4) NOT NULL,
  eir_cov           NUMERIC(6,4) NOT NULL,
  air_cov           NUMERIC(6,4) NOT NULL,
  aim_pct           NUMERIC(6,2) NOT NULL,
  ids_pct           NUMERIC(6,2) NOT NULL,
  del_ontime        NUMERIC(6,4) NOT NULL,
  del_pub           NUMERIC(6,4) NOT NULL,
  pkg_clear         NUMERIC(6,4) NOT NULL,
  wf_thru           NUMERIC(6,4) NOT NULL,
  risk_idx          NUMERIC(6,4) NOT NULL,
  cmms_bind         NUMERIC(6,4) NOT NULL,
  twin_bind         NUMERIC(6,4) NOT NULL,
  ifc_pct           NUMERIC(6,4) NOT NULL,
  cobie_pct         NUMERIC(6,4) NOT NULL,
  ident_pct         NUMERIC(6,4) NOT NULL,
  ih                NUMERIC(6,2) NOT NULL,
  cs                NUMERIC(6,2) NOT NULL,
  dh                NUMERIC(6,2) NOT NULL,
  rs                NUMERIC(6,2) NOT NULL,
  op_readiness      NUMERIC(6,2) NOT NULL,
  tr                NUMERIC(6,2) NOT NULL,
  ph                NUMERIC(6,2) NOT NULL,
  gate_threshold    NUMERIC(6,2) NOT NULL DEFAULT 95,
  p1_open           INTEGER NOT NULL DEFAULT 0,
  blocked_packages  INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (project_id, as_of)
);
CREATE INDEX IF NOT EXISTS ix_ecc_project_latest ON ecc.project_score (project_id, as_of DESC);

CREATE TABLE IF NOT EXISTS ecc.forecast (
  project_id        UUID NOT NULL,
  as_of             TIMESTAMPTZ NOT NULL,
  model_version     TEXT NOT NULL,
  forecast_delay_d  NUMERIC(8,2) NOT NULL,
  drivers           JSONB NOT NULL DEFAULT '[]',
  PRIMARY KEY (project_id, as_of, model_version)
);

CREATE TABLE IF NOT EXISTS ecc.snapshot (
  snapshot_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id        UUID,
  portfolio_id      UUID,
  as_of             TIMESTAMPTZ NOT NULL,
  frozen_by         TEXT NOT NULL,
  reason            TEXT,
  payload           JSONB NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ecc.watchlist (
  watchlist_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_entra_id    TEXT NOT NULL,
  persona           TEXT NOT NULL,
  name              TEXT NOT NULL,
  filter            JSONB NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ecc.alert (
  alert_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id        UUID,
  kpi_id            TEXT NOT NULL,
  band              TEXT NOT NULL,
  message           TEXT NOT NULL,
  event_id          TEXT,
  ack_by            TEXT,
  ack_at            TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ecc.acl (
  entra_id          TEXT NOT NULL,
  project_id        UUID NOT NULL,
  persona           TEXT NOT NULL,
  PRIMARY KEY (entra_id, project_id, persona)
);

-- Ratio helpers
CREATE OR REPLACE FUNCTION ecc.ratio(ok NUMERIC, req NUMERIC)
RETURNS NUMERIC LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE WHEN req IS NULL OR req = 0 THEN 1 ELSE ok / req END;
$$;

CREATE OR REPLACE FUNCTION ecc.band(score NUMERIC, gate NUMERIC DEFAULT NULL)
RETURNS TEXT LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE
    WHEN gate IS NOT NULL AND score < gate THEN 'Red'
    WHEN score >= 85 THEN 'Green'
    WHEN score >= 70 THEN 'Amber'
    ELSE 'Red'
  END;
$$;

-- Latest project score view
CREATE OR REPLACE VIEW ecc.v_project_latest AS
SELECT DISTINCT ON (project_id)
  ps.*,
  ecc.band(ps.ph, NULL) AS ph_band,
  ecc.band(ps.rs, ps.gate_threshold) AS rs_band,
  ecc.band(ps.ih, NULL) AS ih_band
FROM ecc.project_score ps
ORDER BY project_id, as_of DESC;

CREATE MATERIALIZED VIEW IF NOT EXISTS ecc.mv_portfolio AS
SELECT
  p.portfolio_id,
  COUNT(*) AS project_count,
  SUM(CASE WHEN v.ph < 70 THEN 1 ELSE 0 END) AS red_projects,
  AVG(v.ph) AS poh_unweighted,
  SUM(v.p1_open) AS p1_open
FROM ecc.v_project_latest v
JOIN projects p ON p.project_id = v.project_id
GROUP BY p.portfolio_id;

-- NOTE: projects.portfolio_id may be added as a nullable column on PDS projects
-- if not present. Do not invent a second project table.

CREATE OR REPLACE VIEW ecc.v_info_waterfall AS
SELECT project_id, as_of,
  oir_cov * 100 AS oir, pir_cov * 100 AS pir, eir_cov * 100 AS eir,
  air_cov * 100 AS air, aim_pct AS aim, ids_pct AS ids, ih
FROM ecc.v_project_latest;
