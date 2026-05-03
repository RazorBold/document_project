-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    kode        TEXT UNIQUE NOT NULL,
    judul       TEXT NOT NULL,
    pic         TEXT,
    start_date  DATE,
    end_date    DATE,
    status      TEXT DEFAULT 'planning',
    prioritas   TEXT DEFAULT 'medium',
    klien       TEXT,
    deskripsi   TEXT,
    progress    INTEGER DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS projects_updated_at
AFTER UPDATE ON projects
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Activities
CREATE TABLE IF NOT EXISTS activities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    nama        TEXT NOT NULL,
    tanggal     DATE,
    jam_mulai   TIME,
    jam_selesai TIME,
    durasi      INTEGER,
    pelaksana   TEXT,
    lokasi      TEXT,
    output      TEXT,
    status      TEXT DEFAULT 'pending',
    catatan     TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_activities_project ON activities(project_id);

-- Members
CREATE TABLE IF NOT EXISTS members (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    nama        TEXT NOT NULL,
    aktif       INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_members_project ON members(project_id);

-- Meeting Notes
CREATE TABLE IF NOT EXISTS meeting_notes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id  INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    judul        TEXT NOT NULL,
    tanggal      DATETIME,
    notulis      TEXT,
    agenda       TEXT,
    hasil        TEXT,
    lampiran     TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_meeting_notes_activity ON meeting_notes(activity_id);

-- Meeting Attendees
CREATE TABLE IF NOT EXISTS meeting_attendees (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_note_id INTEGER REFERENCES meeting_notes(id) ON DELETE CASCADE,
    member_id       INTEGER REFERENCES members(id) ON DELETE SET NULL,
    nama_manual     TEXT
);

-- Action Items
CREATE TABLE IF NOT EXISTS action_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_note_id INTEGER REFERENCES meeting_notes(id) ON DELETE CASCADE,
    uraian          TEXT NOT NULL,
    pic_member_id   INTEGER REFERENCES members(id) ON DELETE SET NULL,
    deadline        DATE,
    status          TEXT DEFAULT 'belum'
);

CREATE INDEX IF NOT EXISTS idx_action_items_meeting ON action_items(meeting_note_id);

-- Budget
CREATE TABLE IF NOT EXISTS budgets (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    kategori     TEXT,
    nama_item    TEXT,
    qty          REAL DEFAULT 0,
    satuan       TEXT,
    harga_satuan REAL DEFAULT 0,
    total_item   REAL DEFAULT 0,
    realisasi    REAL DEFAULT 0,
    keterangan   TEXT
);

CREATE INDEX IF NOT EXISTS idx_budgets_project ON budgets(project_id);

CREATE TRIGGER IF NOT EXISTS budgets_calc_total_insert
AFTER INSERT ON budgets
BEGIN
    UPDATE budgets SET total_item = NEW.qty * NEW.harga_satuan WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS budgets_calc_total_update
AFTER UPDATE OF qty, harga_satuan ON budgets
BEGIN
    UPDATE budgets SET total_item = NEW.qty * NEW.harga_satuan WHERE id = NEW.id;
END;

-- Milestones
CREATE TABLE IF NOT EXISTS milestones (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    nama        TEXT,
    target_date DATE,
    selesai     INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_milestones_project ON milestones(project_id);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    nama_dokumen TEXT,
    kategori    TEXT,
    filename    TEXT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id);
