from flask import Blueprint, render_template, redirect, url_for
from database import get_db
from datetime import date

bp = Blueprint('report', __name__)


@bp.route('/project/<int:pid>')
def export_report(pid):
    conn = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (pid,)).fetchone()
    if not project:
        conn.close()
        return redirect(url_for('project.list_projects'))
    project = dict(project)

    activities = [dict(r) for r in conn.execute(
        "SELECT * FROM activities WHERE project_id = ? ORDER BY tanggal, jam_mulai", (pid,)
    ).fetchall()]
    members = [dict(r) for r in conn.execute(
        "SELECT * FROM members WHERE project_id = ? ORDER BY nama", (pid,)
    ).fetchall()]
    budgets = [dict(r) for r in conn.execute(
        "SELECT * FROM budgets WHERE project_id = ? ORDER BY kategori, nama_item", (pid,)
    ).fetchall()]
    milestones = [dict(r) for r in conn.execute(
        "SELECT * FROM milestones WHERE project_id = ? ORDER BY target_date", (pid,)
    ).fetchall()]

    row = conn.execute("""
        SELECT COALESCE(SUM(total_item),0) AS total, COALESCE(SUM(realisasi),0) AS real
        FROM budgets WHERE project_id = ?
    """, (pid,)).fetchone()
    budget_summary = {
        'total': row['total'],
        'realisasi': row['real'],
        'sisa': row['total'] - row['real'],
        'pct': round(row['real'] / row['total'] * 100, 1) if row['total'] > 0 else 0,
    }

    meeting_notes = []
    for act in activities:
        notes = conn.execute(
            "SELECT * FROM meeting_notes WHERE activity_id = ? ORDER BY created_at", (act['id'],)
        ).fetchall()
        for n in notes:
            note = dict(n)
            note['activity_nama'] = act['nama']
            note['action_items'] = [dict(r) for r in conn.execute("""
                SELECT ai.*, m.nama as pic_nama FROM action_items ai
                LEFT JOIN members m ON ai.pic_member_id = m.id
                WHERE ai.meeting_note_id = ? ORDER BY ai.id
            """, (note['id'],)).fetchall()]
            meeting_notes.append(note)

    conn.close()

    total_durasi = sum(a['durasi'] or 0 for a in activities)
    h, m = divmod(total_durasi, 60)
    total_durasi_fmt = f'{h}j {m}m' if h else f'{m}m'

    return render_template(
        'report/export.html',
        project=project,
        activities=activities,
        members=members,
        budgets=budgets,
        milestones=milestones,
        budget_summary=budget_summary,
        meeting_notes=meeting_notes,
        total_durasi_fmt=total_durasi_fmt,
        today=date.today().isoformat(),
        active_page='report',
    )
