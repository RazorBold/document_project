from flask import Blueprint, request, jsonify
from database import get_db

bp = Blueprint('member', __name__)


@bp.route('/project/<int:pid>')
def list_members(pid):
    conn = get_db()
    members = [dict(r) for r in conn.execute(
        "SELECT * FROM members WHERE project_id = ? ORDER BY nama", (pid,)
    ).fetchall()]
    conn.close()
    return jsonify(members)


@bp.route('/project/<int:pid>/add', methods=['POST'])
def add_member(pid):
    d = request.get_json() or {}
    nama = d.get('nama', '').strip()
    if not nama:
        return jsonify({'error': 'Nama harus diisi'}), 400
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO members (project_id, nama, aktif) VALUES (?, ?, 1)", (pid, nama)
    )
    conn.commit()
    row = dict(conn.execute("SELECT * FROM members WHERE id = ?", (cur.lastrowid,)).fetchone())
    conn.close()
    return jsonify(row)


@bp.route('/<int:id>/toggle', methods=['POST'])
def toggle_member(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM members WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    new_aktif = 0 if row['aktif'] else 1
    conn.execute("UPDATE members SET aktif = ? WHERE id = ?", (new_aktif, id))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': id, 'aktif': new_aktif})


@bp.route('/<int:id>/delete', methods=['POST'])
def delete_member(id):
    conn = get_db()
    conn.execute("DELETE FROM members WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': id})
