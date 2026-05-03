# CLAUDE.md — Project Planning: Monitoring & Reporting Web App

## 📋 Project Overview

| Item | Detail |
|------|--------|
| **Nama Project** | Monitoring & Reporting System |
| **Stack** | HTML · CSS · Python (Flask) · WebSocket (Flask-SocketIO) · SQLite3 |
| **Tujuan** | Platform monitoring & pelaporan kegiatan proyek secara real-time |
| **Target User** | Project Manager, Tim Internal, Stakeholder |

---

## 🏗️ Arsitektur Sistem

```
monitoring-reporting/
│
├── app.py                        # Flask entry point + SocketIO setup
├── database.py                   # Koneksi & inisialisasi SQLite3
├── init_db.py                    # Script buat tabel pertama kali
├── config.py                     # Konfigurasi environment
├── requirements.txt              # Dependency Python
├── monitoring.db                 # File database SQLite3 (auto-generated)
├── CLAUDE.md                     # Dokumentasi project ini
│
├── routes/
│   ├── __init__.py
│   ├── project.py                # CRUD project
│   ├── activity.py               # CRUD kegiatan & jam
│   ├── member.py                 # Manajemen anggota
│   ├── budget.py                 # Manajemen anggaran
│   ├── meeting.py                # Note rapat & action items
│   └── report.py                 # Export & laporan
│
├── sockets/
│   ├── __init__.py
│   └── events.py                 # WebSocket event handlers
│
├── static/
│   ├── css/
│   │   ├── main.css              # Global styles
│   │   ├── dashboard.css
│   │   └── form.css
│   ├── js/
│   │   ├── socket.js             # Socket.IO client
│   │   ├── dashboard.js
│   │   ├── table.js              # Dynamic activity table
│   │   └── chart.js              # Progress charts
│   └── assets/
│       └── icons/
│
└── templates/
    ├── base.html                 # Layout dasar
    ├── index.html                # Dashboard utama
    ├── project/
    │   ├── list.html
    │   ├── detail.html
    │   └── form.html
    ├── activity/
    │   └── table.html            # Tabel kegiatan + jam
    ├── meeting/
    │   └── note.html             # Form note rapat + action items
    └── report/
        └── export.html
```

---

## 🔧 Tech Stack & Dependencies

### Backend
```
Flask==3.0.x
Flask-SocketIO==5.x
eventlet==0.x              # WebSocket async worker
python-dotenv==1.x
Flask-CORS==4.x
# sqlite3 sudah built-in di Python — tidak perlu install tambahan
```

### Frontend
- **Vanilla HTML5 + CSS3** (no framework, ringan & cepat)
- **Socket.IO Client** (CDN) — real-time update
- **Chart.js** (CDN) — visualisasi progress & anggaran
- **Font**: Geist + Geist Mono (Google Fonts)

---

## 📂 Fitur & Input Fields

### 1. 📁 Project (Header Info)
| Field | Type | Keterangan |
|-------|------|------------|
| Judul Project | Text | Nama project utama |
| Kode Project | Text | ID unik project |
| Timeline Mulai | Date | Tanggal mulai |
| Timeline Selesai | Date | Tanggal target selesai |
| PIC (Person In Charge) | Dropdown/Text | Penanggung jawab utama |
| Status Project | Select | Planning / On Progress / Done / Hold |
| Prioritas | Select | Low / Medium / High / Critical |
| Lokasi / Klien | Text | Nama klien atau lokasi kegiatan |
| Deskripsi Singkat | Textarea | Gambaran umum project |

---

### 2. 📅 Tabel Kegiatan (Activity Log)
Tabel dinamis — bisa tambah/hapus baris.

| Field | Type | Keterangan |
|-------|------|------------|
| No | Auto | Nomor urut otomatis |
| Nama Kegiatan | Text | Deskripsi aktivitas |
| Tanggal | Date | Tanggal kegiatan |
| Jam Mulai | Time | Format HH:MM |
| Jam Selesai | Time | Format HH:MM |
| Durasi | Auto-calc | Otomatis dihitung (Selesai - Mulai) |
| Pelaksana | Text / Select | Anggota yang bertugas |
| Lokasi | Text | Tempat kegiatan |
| Output / Hasil | Textarea | Hasil yang dicapai |
| Status | Badge | Selesai / Ongoing / Pending |
| Catatan | Text | Keterangan tambahan |

---

### 3. 👥 Anggota Tim
| Field | Type | Keterangan |
|-------|------|------------|
| Nama Lengkap | Text | Nama anggota tim |
| Status Keaktifan | Toggle | Aktif / Non-aktif |

---

### 3b. 📝 Note Rapat (per Kegiatan)
Setiap kegiatan bisa memiliki satu atau lebih catatan rapat yang diinput secara terpisah.

| Field | Type | Keterangan |
|-------|------|------------|
| Kegiatan (ref) | Auto | Terhubung ke baris kegiatan |
| Judul Rapat | Text | Topik / agenda rapat |
| Tanggal & Jam | Datetime | Waktu rapat berlangsung |
| Peserta Hadir | Multi-select | Pilih dari daftar anggota tim |
| Notulis | Text / Select | Siapa yang mencatat |
| Agenda | Textarea | Poin-poin yang dibahas |
| Hasil / Keputusan | Textarea | Kesimpulan dan keputusan rapat |
| Tindak Lanjut (Action Item) | Tabel | Tugas, PIC, dan deadline per item |
| Lampiran Notulen | File Input | Upload file notulen (opsional) |

**Tabel Action Item di dalam Note Rapat:**

| Field | Type | Keterangan |
|-------|------|------------|
| No | Auto | |
| Uraian Tugas | Text | Apa yang harus dikerjakan |
| PIC | Select | Anggota yang bertanggung jawab |
| Deadline | Date | Batas waktu penyelesaian |
| Status | Badge | Belum / Proses / Selesai |

---

### 4. 💰 Anggaran (Budget)
| Field | Type | Keterangan |
|-------|------|------------|
| Total Anggaran | Currency | Budget keseluruhan |
| Kategori | Select | SDM / Operasional / Peralatan / Lainnya |
| Nama Item | Text | Nama pengeluaran |
| Qty | Number | Jumlah |
| Satuan | Text | Unit (pcs, jam, hari, dll) |
| Harga Satuan | Currency | |
| Total Item | Auto-calc | Qty × Harga |
| Realisasi | Currency | Dana yang sudah terpakai |
| Sisa Anggaran | Auto-calc | Total - Realisasi |
| Keterangan | Text | |

---

### 5. 📊 Monitoring & Progress
| Field | Type | Keterangan |
|-------|------|------------|
| % Progress Fisik | Slider / Number | 0–100% |
| % Progress Keuangan | Auto-calc | Realisasi / Total × 100 |
| Milestone | Tabel | Target capaian per fase |
| Risiko | Textarea | Identifikasi risiko |
| Mitigasi | Textarea | Langkah antisipasi |
| Update Terbaru | Textarea | Progress update terakhir |
| Tanggal Update | Datetime | Auto-filled saat simpan |

---

### 6. 📎 Lampiran & Dokumen
| Field | Type | Keterangan |
|-------|------|------------|
| Upload File | File Input | PDF, DOCX, XLSX, gambar |
| Nama Dokumen | Text | Label file |
| Kategori Dokumen | Select | Proposal, RAB, Laporan, Foto |
| Tanggal Upload | Datetime | Auto |

---

## 🔌 WebSocket Events (Flask-SocketIO)

### Server → Client (emit)
| Event | Payload | Trigger |
|-------|---------|---------|
| `project_updated` | `{project_id, field, value}` | Saat ada perubahan project |
| `activity_added` | `{activity_data}` | Kegiatan baru ditambah |
| `activity_updated` | `{activity_id, changes}` | Kegiatan diupdate |
| `budget_changed` | `{total, realisasi, sisa}` | Perubahan anggaran |
| `progress_update` | `{project_id, progress}` | Update % progress |
| `notification` | `{type, message}` | Notifikasi sistem |

### Client → Server (on)
| Event | Payload | Aksi |
|-------|---------|------|
| `join_project` | `{project_id}` | Join room project |
| `update_activity` | `{activity_id, data}` | Edit baris kegiatan |
| `update_progress` | `{project_id, value}` | Update slider progress |
| `add_comment` | `{project_id, text}` | Tambah komentar live |

---

## 🗄️ Database — SQLite3

### Pola Koneksi (`database.py`)
```python
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'monitoring.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # akses kolom by name: row['judul']
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

### Init Tabel (`init_db.py`)
Jalankan sekali: `python init_db.py`

```python
from database import get_db

def init():
    conn = get_db()
    with open('schema.sql') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init()
    print("Database initialized.")
```

### Schema (`schema.sql`)

```sql
-- Projects
CREATE TABLE projects (
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

-- Activities
CREATE TABLE activities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id),
    nama        TEXT NOT NULL,
    tanggal     DATE,
    jam_mulai   TIME,
    jam_selesai TIME,
    durasi      INTEGER,          -- in minutes
    pelaksana   TEXT,
    lokasi      TEXT,
    output      TEXT,
    status      TEXT DEFAULT 'pending',
    catatan     TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Members
CREATE TABLE members (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id),
    nama        TEXT NOT NULL,
    aktif       BOOLEAN DEFAULT TRUE
);

-- Meeting Notes (terhubung ke activity)
CREATE TABLE meeting_notes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id  INTEGER REFERENCES activities(id),
    judul        TEXT NOT NULL,
    tanggal      DATETIME,
    notulis      TEXT,
    agenda       TEXT,
    hasil        TEXT,
    lampiran     TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Meeting Attendees
CREATE TABLE meeting_attendees (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_note_id INTEGER REFERENCES meeting_notes(id),
    member_id       INTEGER REFERENCES members(id),
    nama_manual     TEXT
);

-- Action Items (tindak lanjut per note rapat)
CREATE TABLE action_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_note_id INTEGER REFERENCES meeting_notes(id),
    uraian          TEXT NOT NULL,
    pic_member_id   INTEGER REFERENCES members(id),
    deadline        DATE,
    status          TEXT DEFAULT 'belum'
);

-- Budget
CREATE TABLE budgets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id),
    kategori    TEXT,
    nama_item   TEXT,
    qty         REAL,
    satuan      TEXT,
    harga_satuan REAL,
    total_item  REAL,
    realisasi   REAL DEFAULT 0,
    keterangan  TEXT
);

-- Milestones
CREATE TABLE milestones (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER REFERENCES projects(id),
    nama        TEXT,
    target_date DATE,
    selesai     BOOLEAN DEFAULT FALSE
);
```

---

## 🎨 UI Design Direction

- **Tema**: Dark professional — slate/navy dengan aksen teal/cyan
- **Layout**: Sidebar kiri (navigasi) + konten kanan (main panel)
- **Tabel Kegiatan**: Editable inline dengan tombol + / − per baris
- **Real-time**: Badge "LIVE" berkedip saat WebSocket aktif
- **Responsive**: Mobile-friendly (collapsible sidebar)
- **Notifikasi**: Toast notification saat ada update dari user lain

---

## 🚀 Development Phases

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | Setup Flask + SocketIO + DB schema | ⏳ Todo |
| Phase 2 | CRUD Project & Member | ⏳ Todo |
| Phase 3 | Tabel Kegiatan dinamis (jam mulai-selesai) | ⏳ Todo |
| Phase 4 | Budget management + auto-calc | ⏳ Todo |
| Phase 5 | WebSocket live update antar user | ⏳ Todo |
| Phase 6 | Dashboard monitoring + chart progress | ⏳ Todo |
| Phase 7 | Export laporan (PDF/Excel) | ⏳ Todo |
| Phase 8 | Upload dokumen lampiran | ⏳ Todo |

---

## ⚙️ Setup & Run

```bash
# Masuk folder project
cd monitoring-reporting

# Buat virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Copy env
cp .env.example .env

# Init database SQLite3 (jalankan sekali)
python init_db.py
# → monitoring.db terbuat otomatis

# Jalankan server
python app.py
# → http://localhost:5000
```

---

## 📝 .env.example

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DB_PATH=monitoring.db
SOCKETIO_ASYNC_MODE=eventlet
MAX_CONTENT_LENGTH=16777216    # 16MB max upload
```

---

## 🔜 Next Step

Setelah `CLAUDE.md` ini selesai, langkah selanjutnya:

1. **Buat `database.py`** — koneksi SQLite3 + helper `get_db()`
2. **Buat `schema.sql`** — definisi semua tabel
3. **Buat `init_db.py`** — script inisialisasi database
4. **Buat `app.py`** — Flask + SocketIO init
5. **Buat `templates/base.html`** — Layout HTML utama
6. **Buat `templates/index.html`** — Dashboard monitoring
7. **Buat `templates/project/form.html`** — Form input semua field
8. **Buat `static/js/socket.js`** — Koneksi WebSocket client
9. **Buat `static/js/table.js`** — Tabel kegiatan dinamis

---

*Generated by Claude · Monitoring & Reporting System · v1.0*