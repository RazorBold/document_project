"""
Script untuk mengisi database dengan data dummy / contoh.
Jalankan: python insert_dummy.py
"""
import sqlite3, os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(basedir, os.getenv('DB_PATH', 'monitoring.db'))

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

# ── Hapus data lama (opsional, comment jika tidak mau hapus) ──
tables = ['action_items','meeting_attendees','meeting_notes',
          'documents','milestones','budgets','activities','members','projects']
for t in tables:
    conn.execute(f'DELETE FROM {t}')
conn.commit()

# ═══════════════════════════════════════════════════
# PROJECT 1 — Pengembangan Sistem ERP
# ═══════════════════════════════════════════════════
cur = conn.execute("""
    INSERT INTO projects (kode,judul,pic,start_date,end_date,status,prioritas,klien,deskripsi,progress)
    VALUES (?,?,?,?,?,?,?,?,?,?)
""", ('PRJ-2024-001','Pengembangan Sistem ERP','Budi Santoso','2024-01-15','2024-12-31',
      'on_progress','high','PT Maju Bersama',
      'Implementasi sistem Enterprise Resource Planning terintegrasi meliputi modul keuangan, SDM, dan inventaris.',
      65))
p1 = cur.lastrowid

# Members
m1a = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p1,'Budi Santoso')).lastrowid
m1b = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p1,'Dewi Rahayu')).lastrowid
m1c = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p1,'Fajar Nugroho')).lastrowid
m1d = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,0)",(p1,'Rina Safitri')).lastrowid

# Activities
a1a = conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p1,'Kick-off Meeting & Requirement Gathering','2024-01-20','09:00','12:00',180,
     'Budi Santoso','Kantor Pusat','Dokumen SRS v1.0','selesai')).lastrowid
a1b = conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p1,'Desain Arsitektur Sistem','2024-02-10','08:00','17:00',540,
     'Fajar Nugroho','Remote','Blueprint arsitektur & ERD database','selesai')).lastrowid
a1c = conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p1,'Development Modul Keuangan','2024-03-01','08:00','16:00',480,
     'Fajar Nugroho','Remote','Source code modul keuangan v1.0','selesai')).lastrowid
a1d = conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p1,'Development Modul SDM','2024-05-15','08:00','17:00',540,
     'Dewi Rahayu','Remote','Source code modul SDM v1.0','ongoing')).lastrowid
a1e = conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p1,'User Acceptance Testing','2024-10-01','09:00','15:00',360,
     'Budi Santoso','Kantor Klien','Laporan UAT','pending')).lastrowid

# Budget
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p1,'SDM','Konsultan IT',12,'bulan',25000000,300000000,195000000))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p1,'Peralatan','Lisensi Software ERP',1,'paket',150000000,150000000,150000000))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p1,'Operasional','Perjalanan Dinas',10,'kali',5000000,50000000,22000000))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p1,'Operasional','Training User',2,'batch',15000000,30000000,0))

# Milestones
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p1,'Requirement & Desain Selesai','2024-02-28',1))
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p1,'Development Modul Inti Selesai','2024-06-30',0))
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p1,'UAT & Go-Live','2024-11-30',0))

# Meeting note untuk activity 1
note1 = conn.execute("""INSERT INTO meeting_notes(activity_id,judul,tanggal,notulis,agenda,hasil)
    VALUES(?,?,?,?,?,?)""",
    (a1a,'Kick-off ERP Project','2024-01-20 09:00','Dewi Rahayu',
     '1. Perkenalan tim\n2. Scope project\n3. Timeline dan milestone\n4. Resource allocation',
     'Disepakati scope project mencakup 3 modul utama. Timeline 12 bulan. Tim inti 4 orang.')).lastrowid
conn.execute("INSERT INTO meeting_attendees(meeting_note_id,member_id) VALUES(?,?)",(note1,m1a))
conn.execute("INSERT INTO meeting_attendees(meeting_note_id,member_id) VALUES(?,?)",(note1,m1b))
conn.execute("INSERT INTO meeting_attendees(meeting_note_id,member_id) VALUES(?,?)",(note1,m1c))
conn.execute("INSERT INTO action_items(meeting_note_id,uraian,pic_member_id,deadline,status) VALUES(?,?,?,?,?)",
    (note1,'Buat dokumen SRS v1.0',m1c,'2024-02-05','selesai'))
conn.execute("INSERT INTO action_items(meeting_note_id,uraian,pic_member_id,deadline,status) VALUES(?,?,?,?,?)",
    (note1,'Setup environment development',m1c,'2024-01-31','selesai'))
conn.execute("INSERT INTO action_items(meeting_note_id,uraian,pic_member_id,deadline,status) VALUES(?,?,?,?,?)",
    (note1,'Koordinasi dengan vendor ERP',m1a,'2024-02-10','selesai'))

# ═══════════════════════════════════════════════════
# PROJECT 2 — Renovasi Kantor Pusat
# ═══════════════════════════════════════════════════
cur = conn.execute("""
    INSERT INTO projects (kode,judul,pic,start_date,end_date,status,prioritas,klien,deskripsi,progress)
    VALUES (?,?,?,?,?,?,?,?,?,?)
""", ('PRJ-2024-002','Renovasi Kantor Pusat','Siti Aminah','2024-06-01','2024-09-30',
      'done','medium','Internal',
      'Renovasi total ruangan kantor pusat lantai 3 dan 4 meliputi partisi, furniture, dan instalasi jaringan.',
      100))
p2 = cur.lastrowid

m2a = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p2,'Siti Aminah')).lastrowid
m2b = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p2,'Ahmad Fauzi')).lastrowid
m2c = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p2,'Lestari Putri')).lastrowid

conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p2,'Survey & Perencanaan','2024-06-05','08:00','12:00',240,'Siti Aminah','Kantor Pusat Lt.3','Gambar denah renovasi','selesai'))
conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p2,'Pengerjaan Partisi & Cat','2024-07-01','07:00','17:00',600,'Ahmad Fauzi','Kantor Pusat Lt.3-4','Partisi & cat selesai','selesai'))
conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p2,'Instalasi Furniture & IT','2024-08-15','08:00','17:00',540,'Ahmad Fauzi','Kantor Pusat','Ruangan siap pakai','selesai'))
conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p2,'Serah Terima & Evaluasi','2024-09-28','09:00','11:00',120,'Siti Aminah','Kantor Pusat','Berita acara serah terima','selesai'))

conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p2,'Peralatan','Material Partisi & Cat',1,'paket',80000000,80000000,78500000))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p2,'Peralatan','Furniture Kantor',40,'unit',3500000,140000000,136000000))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p2,'Operasional','Jasa Kontraktor',1,'paket',45000000,45000000,45000000))

conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p2,'Desain & Approval Selesai','2024-06-15',1))
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p2,'Konstruksi Selesai','2024-09-01',1))
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p2,'Serah Terima','2024-09-30',1))

# ═══════════════════════════════════════════════════
# PROJECT 3 — Digital Transformation Program
# ═══════════════════════════════════════════════════
cur = conn.execute("""
    INSERT INTO projects (kode,judul,pic,start_date,end_date,status,prioritas,klien,deskripsi,progress)
    VALUES (?,?,?,?,?,?,?,?,?,?)
""", ('PRJ-2025-001','Digital Transformation Program','Rizki Hamdani','2025-01-01','2025-12-31',
      'on_progress','critical','Kementerian Komunikasi',
      'Program transformasi digital nasional mencakup digitalisasi layanan publik, pelatihan SDM, dan infrastruktur cloud.',
      35))
p3 = cur.lastrowid

m3a = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p3,'Rizki Hamdani')).lastrowid
m3b = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p3,'Yuni Kartika')).lastrowid
m3c = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p3,'Dani Prasetyo')).lastrowid
m3d = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p3,'Maya Sari')).lastrowid
m3e = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p3,'Eko Wahyudi')).lastrowid

conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p3,'Workshop Kebutuhan Digitalisasi','2025-01-15','09:00','16:00',420,'Rizki Hamdani','Jakarta','Roadmap digitalisasi','selesai'))
conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p3,'Setup Cloud Infrastructure','2025-02-01','08:00','17:00',540,'Dani Prasetyo','Remote','Cloud env ready','selesai'))
conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p3,'Development Portal Layanan Publik','2025-03-01','08:00','17:00',540,'Yuni Kartika','Remote','Portal v0.5','ongoing'))
conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p3,'Pelatihan SDM Batch 1','2025-04-10','08:00','15:00',420,'Maya Sari','Bandung','100 SDM terlatih','pending'))
conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p3,'Pilot Testing & Evaluasi','2025-06-01','09:00','15:00',360,'Rizki Hamdani','Jakarta','Laporan pilot','pending'))

conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p3,'SDM','Tim Developer',6,'orang',30000000,180000000,60000000))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p3,'Operasional','Cloud Server AWS',12,'bulan',20000000,240000000,40000000))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p3,'SDM','Trainer & Fasilitator',4,'sesi',15000000,60000000,0))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p3,'Operasional','Sosialisasi & Publikasi',1,'paket',50000000,50000000,12000000))

conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p3,'Infrastruktur Cloud Ready','2025-02-28',1))
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p3,'Portal Layanan Publik Launch','2025-05-31',0))
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p3,'500 SDM Terlatih','2025-08-31',0))
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p3,'Go-Live Nasional','2025-12-01',0))

# ═══════════════════════════════════════════════════
# PROJECT 4 — Audit IT Infrastructure
# ═══════════════════════════════════════════════════
cur = conn.execute("""
    INSERT INTO projects (kode,judul,pic,start_date,end_date,status,prioritas,klien,deskripsi,progress)
    VALUES (?,?,?,?,?,?,?,?,?,?)
""", ('PRJ-2025-002','Audit Keamanan IT Infrastructure','Hendra Wijaya','2025-02-01','2025-05-31',
      'hold','critical','PT Sekuriti Nusantara',
      'Audit menyeluruh terhadap keamanan infrastruktur IT perusahaan termasuk penetration testing, review kebijakan, dan rekomendasi mitigasi risiko.',
      30))
p4 = cur.lastrowid

m4a = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p4,'Hendra Wijaya')).lastrowid
m4b = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,1)",(p4,'Nanda Kurniawan')).lastrowid
m4c = conn.execute("INSERT INTO members(project_id,nama,aktif) VALUES(?,?,0)",(p4,'Bagas Saputra')).lastrowid

conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p4,'Kick-off & Scope Definition','2025-02-05','09:00','12:00',180,'Hendra Wijaya','Klien Site','Scope dokumen audit','selesai'))
conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p4,'Network Vulnerability Assessment','2025-02-20','08:00','17:00',540,'Nanda Kurniawan','Klien Site','Laporan VA network','selesai'))
conn.execute("""INSERT INTO activities(project_id,nama,tanggal,jam_mulai,jam_selesai,durasi,pelaksana,lokasi,output,status)
    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (p4,'Penetration Testing','2025-03-10','08:00','17:00',540,'Nanda Kurniawan','Remote','Laporan pentest','pending'))

conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p4,'SDM','Security Auditor',2,'orang',20000000,40000000,16000000))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p4,'Peralatan','Tools & Lisensi Audit',1,'paket',15000000,15000000,15000000))
conn.execute("""INSERT INTO budgets(project_id,kategori,nama_item,qty,satuan,harga_satuan,total_item,realisasi)
    VALUES(?,?,?,?,?,?,?,?)""",(p4,'Operasional','Akomodasi Tim',5,'hari',2000000,10000000,4000000))

conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p4,'Vulnerability Assessment Selesai','2025-03-01',1))
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p4,'Penetration Testing Selesai','2025-04-01',0))
conn.execute("INSERT INTO milestones(project_id,nama,target_date,selesai) VALUES(?,?,?,?)",
    (p4,'Laporan Final & Rekomendasi','2025-05-15',0))

conn.commit()
conn.close()

print("=" * 55)
print("  Data dummy berhasil dimasukkan!")
print("=" * 55)
print(f"  ✓ PRJ-2024-001  Pengembangan Sistem ERP        (65%)")
print(f"  ✓ PRJ-2024-002  Renovasi Kantor Pusat          (100%)")
print(f"  ✓ PRJ-2025-001  Digital Transformation Program  (35%)")
print(f"  ✓ PRJ-2025-002  Audit Keamanan IT Infrastructure(30%)")
print("=" * 55)
print("  Buka http://localhost:5000 untuk melihat hasilnya")
print("=" * 55)
