-- Postgres (Neon / Supabase) schema for the Monitoring & Reporting app.
-- Date/time columns are TEXT on purpose: the app (written for SQLite) treats them as
-- 'YYYY-MM-DD' / 'HH:MM' / 'YYYY-MM-DD HH:MM:SS' strings in templates and JSON.
-- Run once in the Neon (or Supabase) SQL Editor.

CREATE OR REPLACE FUNCTION now_text() RETURNS text
LANGUAGE sql STABLE AS $$
  SELECT to_char(now() AT TIME ZONE 'utc', 'YYYY-MM-DD HH24:MI:SS')
$$;

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id          BIGSERIAL PRIMARY KEY,
    kode        TEXT UNIQUE NOT NULL,
    judul       TEXT NOT NULL,
    pic         TEXT,
    start_date  TEXT,
    end_date    TEXT,
    status      TEXT DEFAULT 'planning',
    prioritas   TEXT DEFAULT 'medium',
    klien       TEXT,
    deskripsi   TEXT,
    progress    INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT now_text(),
    updated_at  TEXT DEFAULT now_text()
);

CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := now_text();
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS projects_updated_at ON projects;
CREATE TRIGGER projects_updated_at
BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Activities
CREATE TABLE IF NOT EXISTS activities (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    nama        TEXT NOT NULL,
    tanggal     TEXT,
    jam_mulai   TEXT,
    jam_selesai TEXT,
    durasi      INTEGER,
    pelaksana   TEXT,
    lokasi      TEXT,
    output      TEXT,
    status      TEXT DEFAULT 'pending',
    catatan     TEXT,
    created_at  TEXT DEFAULT now_text()
);
CREATE INDEX IF NOT EXISTS idx_activities_project ON activities(project_id);

-- Members
CREATE TABLE IF NOT EXISTS members (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    nama        TEXT NOT NULL,
    aktif       INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_members_project ON members(project_id);

-- Meeting Notes
CREATE TABLE IF NOT EXISTS meeting_notes (
    id           BIGSERIAL PRIMARY KEY,
    activity_id  BIGINT REFERENCES activities(id) ON DELETE CASCADE,
    judul        TEXT NOT NULL,
    tanggal      TEXT,
    notulis      TEXT,
    agenda       TEXT,
    hasil        TEXT,
    lampiran     TEXT,
    created_at   TEXT DEFAULT now_text()
);
CREATE INDEX IF NOT EXISTS idx_meeting_notes_activity ON meeting_notes(activity_id);

-- Meeting Attendees
CREATE TABLE IF NOT EXISTS meeting_attendees (
    id              BIGSERIAL PRIMARY KEY,
    meeting_note_id BIGINT REFERENCES meeting_notes(id) ON DELETE CASCADE,
    member_id       BIGINT REFERENCES members(id) ON DELETE SET NULL,
    nama_manual     TEXT
);

-- Action Items
CREATE TABLE IF NOT EXISTS action_items (
    id              BIGSERIAL PRIMARY KEY,
    meeting_note_id BIGINT REFERENCES meeting_notes(id) ON DELETE CASCADE,
    uraian          TEXT NOT NULL,
    pic_member_id   BIGINT REFERENCES members(id) ON DELETE SET NULL,
    deadline        TEXT,
    status          TEXT DEFAULT 'belum'
);
CREATE INDEX IF NOT EXISTS idx_action_items_meeting ON action_items(meeting_note_id);

-- Budget
CREATE TABLE IF NOT EXISTS budgets (
    id           BIGSERIAL PRIMARY KEY,
    project_id   BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    kategori     TEXT,
    nama_item    TEXT,
    qty          DOUBLE PRECISION DEFAULT 0,
    satuan       TEXT,
    harga_satuan DOUBLE PRECISION DEFAULT 0,
    total_item   DOUBLE PRECISION DEFAULT 0,
    realisasi    DOUBLE PRECISION DEFAULT 0,
    keterangan   TEXT
);
CREATE INDEX IF NOT EXISTS idx_budgets_project ON budgets(project_id);

CREATE OR REPLACE FUNCTION budgets_calc_total() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.total_item := COALESCE(NEW.qty, 0) * COALESCE(NEW.harga_satuan, 0);
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS budgets_calc_total ON budgets;
CREATE TRIGGER budgets_calc_total
BEFORE INSERT OR UPDATE ON budgets
FOR EACH ROW EXECUTE FUNCTION budgets_calc_total();

-- Milestones
CREATE TABLE IF NOT EXISTS milestones (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    nama        TEXT,
    target_date TEXT,
    selesai     INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_milestones_project ON milestones(project_id);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id           BIGSERIAL PRIMARY KEY,
    project_id   BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    nama_dokumen TEXT,
    kategori     TEXT,
    filename     TEXT,
    uploaded_at  TEXT DEFAULT now_text()
);
CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id);

-- The Flask app connects as the table owner, so it is not affected by RLS.
-- Enabling RLS with no policies blocks access through public data APIs (Supabase/Neon Data API).
ALTER TABLE projects          ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities        ENABLE ROW LEVEL SECURITY;
ALTER TABLE members           ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_notes     ENABLE ROW LEVEL SECURITY;
ALTER TABLE meeting_attendees ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_items      ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets           ENABLE ROW LEVEL SECURITY;
ALTER TABLE milestones        ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents         ENABLE ROW LEVEL SECURITY;
