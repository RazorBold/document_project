from flask import Blueprint, request, jsonify
from database import get_db

bp = Blueprint('budget', __name__)


def get_budget_summary(project_id, conn):
    row = conn.execute("""
        SELECT
            COALESCE(SUM(total_item), 0) AS total_anggaran,
            COALESCE(SUM(realisasi), 0)  AS total_realisasi
        FROM budgets WHERE project_id = ?
    """, (project_id,)).fetchone()
    total = row['total_anggaran']
    real = row['total_realisasi']
    return {
        'total': total,
        'realisasi': real,
        'sisa': total - real,
        'pct': round(real / total * 100, 1) if total > 0 else 0,
    }


@bp.route('/project/<int:pid>/add', methods=['POST'])
def add_budget(pid):
    d = request.get_json() or {}
    conn = get_db()
    qty = float(d.get('qty', 0) or 0)
    harga = float(d.get('harga_satuan', 0) or 0)
    cur = conn.execute("""
        INSERT INTO budgets (project_id, kategori, nama_item, qty, satuan,
            harga_satuan, realisasi, keterangan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (pid, d.get('kategori'), d.get('nama_item'), qty,
          d.get('satuan'), harga, float(d.get('realisasi', 0) or 0),
          d.get('keterangan')))
    conn.commit()
    row = dict(conn.execute("SELECT * FROM budgets WHERE id = ?", (cur.lastrowid,)).fetchone())
    summary = get_budget_summary(pid, conn)
    conn.close()
    from app import socketio
    socketio.emit('budget_changed', {'project_id': pid, 'summary': summary},
                  room=f'project_{pid}')
    return jsonify({'item': row, 'summary': summary})


@bp.route('/<int:id>/update', methods=['POST'])
def update_budget(id):
    d = request.get_json() or {}
    conn = get_db()
    row = conn.execute("SELECT * FROM budgets WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    qty = float(d.get('qty', row['qty']) or 0)
    harga = float(d.get('harga_satuan', row['harga_satuan']) or 0)
    conn.execute("""
        UPDATE budgets SET kategori=?, nama_item=?, qty=?, satuan=?,
            harga_satuan=?, realisasi=?, keterangan=?
        WHERE id=?
    """, (
        d.get('kategori', row['kategori']),
        d.get('nama_item', row['nama_item']),
        qty, d.get('satuan', row['satuan']), harga,
        float(d.get('realisasi', row['realisasi']) or 0),
        d.get('keterangan', row['keterangan']),
        id,
    ))
    conn.commit()
    updated = dict(conn.execute("SELECT * FROM budgets WHERE id = ?", (id,)).fetchone())
    pid = updated['project_id']
    summary = get_budget_summary(pid, conn)
    conn.close()
    from app import socketio
    socketio.emit('budget_changed', {'project_id': pid, 'summary': summary},
                  room=f'project_{pid}')
    return jsonify({'item': updated, 'summary': summary})


@bp.route('/<int:id>/delete', methods=['POST'])
def delete_budget(id):
    conn = get_db()
    row = conn.execute("SELECT project_id FROM budgets WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    pid = row['project_id']
    conn.execute("DELETE FROM budgets WHERE id = ?", (id,))
    conn.commit()
    summary = get_budget_summary(pid, conn)
    conn.close()
    from app import socketio
    socketio.emit('budget_changed', {'project_id': pid, 'summary': summary},
                  room=f'project_{pid}')
    return jsonify({'ok': True, 'id': id, 'summary': summary})


@bp.route('/milestone/<int:pid>/add', methods=['POST'])
def add_milestone(pid):
    d = request.get_json() or {}
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO milestones (project_id, nama, target_date, selesai) VALUES (?, ?, ?, 0)",
        (pid, d.get('nama'), d.get('target_date') or None)
    )
    conn.commit()
    row = dict(conn.execute("SELECT * FROM milestones WHERE id = ?", (cur.lastrowid,)).fetchone())
    conn.close()
    return jsonify(row)


@bp.route('/milestone/<int:id>/toggle', methods=['POST'])
def toggle_milestone(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM milestones WHERE id = ?", (id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    new_val = 0 if row['selesai'] else 1
    conn.execute("UPDATE milestones SET selesai = ? WHERE id = ?", (new_val, id))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': id, 'selesai': new_val})


@bp.route('/milestone/<int:id>/delete', methods=['POST'])
def delete_milestone(id):
    conn = get_db()
    conn.execute("DELETE FROM milestones WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': id})
