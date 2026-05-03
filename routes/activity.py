from flask import Blueprint, render_template, request, jsonify
from database import get_db
from datetime import datetime

bp = Blueprint('activity', __name__)


def _calc_durasi(jam_mulai, jam_selesai):
    if not jam_mulai or not jam_selesai:
        return None
    fmt = '%H:%M'
    try:
        start = datetime.strptime(jam_mulai[:5], fmt)
        end = datetime.strptime(jam_selesai[:5], fmt)
        minutes = int((end - start).total_seconds() / 60)
        if minutes < 0:
            minutes += 24 * 60
        return minutes
    except ValueError:
        return None


def _format_durasi(minutes):
    if minutes is None:
        return '—'
    h, m = divmod(minutes, 60)
    return f'{h}j {m}m' if h else f'{m}m'


@bp.route('/project/<int:pid>')
def activity_table(pid):
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone()
    if not project:
        conn.close()
        return 'Project not found', 404
    activities = [dict(r) for r in conn.execute(
        "SELECT * FROM activities WHERE project_id = ? ORDER BY tanggal, jam_mulai", (pid,)
    ).fetchall()]
    members = [dict(r) for r in conn.execute(
        "SELECT * FROM members WHERE project_id = ? AND aktif = 1 ORDER BY nama", (pid,)
    ).fetchall()]
    conn.close()
    for a in activities:
        a['durasi_fmt'] = _format_durasi(a['durasi'])
    return render_template(
        'activity/table.html',
        project=dict(project),
        activities=activities,
        members=members,
        active_page='projects',
    )


@bp.route('/project/<int:pid>/add', methods=['POST'])
def add_activity(pid):
    d = request.get_json() or {}
    nama = d.get('nama', '').strip()
    if not nama:
        return jsonify({'error': 'Nama kegiatan harus diisi'}), 400
    jam_mulai = d.get('jam_mulai') or None
    jam_selesai = d.get('jam_selesai') or None
    durasi = _calc_durasi(jam_mulai, jam_selesai)
    conn = get_db()
    cur = conn.execute("""
        INSERT INTO activities (project_id, nama, tanggal, jam_mulai, jam_selesai,
            durasi, pelaksana, lokasi, output, status, catatan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (pid, nama, d.get('tanggal') or None, jam_mulai, jam_selesai, durasi,
          d.get('pelaksana'), d.get('lokasi'), d.get('output'),
          d.get('status', 'pending'), d.get('catatan')))
    conn.commit()
    row = dict(conn.execute("SELECT * FROM activities WHERE id = ?", (cur.lastrowid,)).fetchone())
    conn.close()
    row['durasi_fmt'] = _format_durasi(row['durasi'])
    from app import socketio
    socketio.emit('activity_added', row, room=f'project_{pid}')
    return jsonify(row)


@bp.route('/<int:id>/update', methods=['POST'])
def update_activity(id):
    d = request.get_json() or {}
    conn = get_db()
    row = conn.execute("SELECT * FROM activities WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404

    jam_mulai = d.get('jam_mulai', row['jam_mulai'])
    jam_selesai = d.get('jam_selesai', row['jam_selesai'])
    durasi = _calc_durasi(jam_mulai, jam_selesai)

    conn.execute("""
        UPDATE activities SET nama=?, tanggal=?, jam_mulai=?, jam_selesai=?,
            durasi=?, pelaksana=?, lokasi=?, output=?, status=?, catatan=?
        WHERE id=?
    """, (
        d.get('nama', row['nama']),
        d.get('tanggal', row['tanggal']),
        jam_mulai, jam_selesai, durasi,
        d.get('pelaksana', row['pelaksana']),
        d.get('lokasi', row['lokasi']),
        d.get('output', row['output']),
        d.get('status', row['status']),
        d.get('catatan', row['catatan']),
        id,
    ))
    conn.commit()
    updated = dict(conn.execute("SELECT * FROM activities WHERE id = ?", (id,)).fetchone())
    pid = updated['project_id']
    conn.close()
    updated['durasi_fmt'] = _format_durasi(updated['durasi'])
    from app import socketio
    socketio.emit('activity_updated', {'activity_id': id, 'changes': updated},
                  room=f'project_{pid}')
    return jsonify(updated)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete_activity(id):
    conn = get_db()
    row = conn.execute("SELECT project_id FROM activities WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    pid = row['project_id']
    conn.execute("DELETE FROM activities WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': id, 'project_id': pid})
