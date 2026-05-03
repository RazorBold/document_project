from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from database import get_db
from datetime import date

bp = Blueprint('project', __name__)


def _budget_summary(project_id, conn):
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


@bp.route('/')
def list_projects():
    conn = get_db()
    projects = [dict(r) for r in conn.execute(
        "SELECT * FROM projects ORDER BY updated_at DESC"
    ).fetchall()]
    conn.close()
    return render_template('project/list.html', projects=projects, active_page='projects')


@bp.route('/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        d = request.form
        conn = get_db()
        cur = conn.execute("""
            INSERT INTO projects (kode, judul, pic, start_date, end_date, status, prioritas, klien, deskripsi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (d['kode'], d['judul'], d.get('pic'), d.get('start_date') or None,
              d.get('end_date') or None, d.get('status', 'planning'),
              d.get('prioritas', 'medium'), d.get('klien'), d.get('deskripsi')))
        conn.commit()
        project_id = cur.lastrowid
        conn.close()
        return redirect(url_for('project.project_detail', id=project_id))
    return render_template('project/form.html', project=None, active_page='projects')


@bp.route('/<int:id>')
def project_detail(id):
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (id,)).fetchone()
    if not project:
        conn.close()
        return redirect(url_for('project.list_projects'))
    project = dict(project)

    activities = [dict(r) for r in conn.execute(
        "SELECT * FROM activities WHERE project_id = ? ORDER BY tanggal, jam_mulai", (id,)
    ).fetchall()]
    members = [dict(r) for r in conn.execute(
        "SELECT * FROM members WHERE project_id = ? ORDER BY nama", (id,)
    ).fetchall()]
    budgets = [dict(r) for r in conn.execute(
        "SELECT * FROM budgets WHERE project_id = ? ORDER BY kategori, nama_item", (id,)
    ).fetchall()]
    milestones = [dict(r) for r in conn.execute(
        "SELECT * FROM milestones WHERE project_id = ? ORDER BY target_date", (id,)
    ).fetchall()]
    budget_summary = _budget_summary(id, conn)

    # Chart data
    kategori_rows = conn.execute("""
        SELECT kategori,
               COALESCE(SUM(total_item), 0) AS total,
               COALESCE(SUM(realisasi), 0)  AS real
        FROM budgets WHERE project_id = ? GROUP BY kategori
    """, (id,)).fetchall()
    conn.close()

    chart_data = {
        'progress': project['progress'],
        'budget_pct': budget_summary['pct'],
        'labels': [r['kategori'] or 'Lainnya' for r in kategori_rows],
        'anggaran': [r['total'] for r in kategori_rows],
        'realisasi': [r['real'] for r in kategori_rows],
    }

    return render_template(
        'project/detail.html',
        project=project,
        activities=activities,
        members=members,
        budgets=budgets,
        milestones=milestones,
        budget_summary=budget_summary,
        chart_data=chart_data,
        today=date.today().isoformat(),
        active_page='projects',
    )


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_project(id):
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (id,)).fetchone()
    if not project:
        conn.close()
        return redirect(url_for('project.list_projects'))
    if request.method == 'POST':
        d = request.form
        conn.execute("""
            UPDATE projects SET kode=?, judul=?, pic=?, start_date=?, end_date=?,
                status=?, prioritas=?, klien=?, deskripsi=?
            WHERE id=?
        """, (d['kode'], d['judul'], d.get('pic'), d.get('start_date') or None,
              d.get('end_date') or None, d.get('status', 'planning'),
              d.get('prioritas', 'medium'), d.get('klien'), d.get('deskripsi'), id))
        conn.commit()
        conn.close()
        return redirect(url_for('project.project_detail', id=id))
    project = dict(project)
    conn.close()
    return render_template('project/form.html', project=project, active_page='projects')


@bp.route('/<int:id>/delete', methods=['POST'])
def delete_project(id):
    conn = get_db()
    conn.execute("DELETE FROM projects WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('project.list_projects'))


@bp.route('/<int:id>/progress', methods=['POST'])
def update_progress(id):
    data = request.get_json()
    value = max(0, min(100, int(data.get('value', 0))))
    conn = get_db()
    conn.execute("UPDATE projects SET progress = ? WHERE id = ?", (value, id))
    conn.commit()
    conn.close()
    from app import socketio
    socketio.emit('progress_update', {'project_id': id, 'progress': value},
                  room=f'project_{id}')
    return jsonify({'ok': True, 'progress': value})
