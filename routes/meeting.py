from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from database import get_db

bp = Blueprint('meeting', __name__)


@bp.route('/activity/<int:aid>', methods=['GET', 'POST'])
def meeting_note(aid):
    conn = get_db()
    activity = conn.execute("""
        SELECT a.*, p.judul as project_judul, p.id as project_id
        FROM activities a JOIN projects p ON a.project_id = p.id
        WHERE a.id = ?
    """, (aid,)).fetchone()
    if not activity:
        conn.close()
        return 'Activity not found', 404

    if request.method == 'POST':
        d = request.form
        attendee_ids = request.form.getlist('attendee_ids[]')
        attendee_manual = request.form.getlist('attendee_manual[]')
        action_uraians = request.form.getlist('action_uraian[]')
        action_pics = request.form.getlist('action_pic[]')
        action_deadlines = request.form.getlist('action_deadline[]')
        action_statuses = request.form.getlist('action_status[]')

        # Handle file upload
        lampiran = None
        if 'lampiran' in request.files:
            f = request.files['lampiran']
            if f and f.filename:
                from werkzeug.utils import secure_filename
                import os
                from flask import current_app
                fname = secure_filename(f.filename)
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
                f.save(upload_path)
                lampiran = fname

        try:
            cur = conn.execute("""
                INSERT INTO meeting_notes (activity_id, judul, tanggal, notulis, agenda, hasil, lampiran)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (aid, d.get('judul'), d.get('tanggal') or None,
                  d.get('notulis'), d.get('agenda'), d.get('hasil'), lampiran))
            note_id = cur.lastrowid

            for mid in attendee_ids:
                if mid:
                    conn.execute(
                        "INSERT INTO meeting_attendees (meeting_note_id, member_id) VALUES (?, ?)",
                        (note_id, int(mid))
                    )
            for nama in attendee_manual:
                if nama.strip():
                    conn.execute(
                        "INSERT INTO meeting_attendees (meeting_note_id, nama_manual) VALUES (?, ?)",
                        (note_id, nama.strip())
                    )
            for i, uraian in enumerate(action_uraians):
                if uraian.strip():
                    pic_id = action_pics[i] if i < len(action_pics) and action_pics[i] else None
                    deadline = action_deadlines[i] if i < len(action_deadlines) and action_deadlines[i] else None
                    status = action_statuses[i] if i < len(action_statuses) else 'belum'
                    conn.execute("""
                        INSERT INTO action_items (meeting_note_id, uraian, pic_member_id, deadline, status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (note_id, uraian.strip(), pic_id or None, deadline, status))
            conn.commit()
        except Exception:
            conn.rollback()
            conn.close()
            raise
        conn.close()
        pid = activity['project_id']
        return redirect(url_for('project.project_detail', id=pid) + '#tab-activities')

    members = [dict(r) for r in conn.execute(
        "SELECT * FROM members WHERE project_id = ? AND aktif = 1 ORDER BY nama",
        (activity['project_id'],)
    ).fetchall()]
    notes = [dict(r) for r in conn.execute(
        "SELECT * FROM meeting_notes WHERE activity_id = ? ORDER BY created_at DESC", (aid,)
    ).fetchall()]
    conn.close()
    return render_template(
        'meeting/note.html',
        activity=dict(activity),
        members=members,
        notes=notes,
        active_page='projects',
    )


@bp.route('/<int:id>/detail')
def meeting_detail(id):
    conn = get_db()
    note = conn.execute("SELECT * FROM meeting_notes WHERE id = ?", (id,)).fetchone()
    if not note:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    note = dict(note)
    attendees = [dict(r) for r in conn.execute("""
        SELECT ma.*, m.nama as member_nama
        FROM meeting_attendees ma
        LEFT JOIN members m ON ma.member_id = m.id
        WHERE ma.meeting_note_id = ?
    """, (id,)).fetchall()]
    action_items = [dict(r) for r in conn.execute("""
        SELECT ai.*, m.nama as pic_nama
        FROM action_items ai
        LEFT JOIN members m ON ai.pic_member_id = m.id
        WHERE ai.meeting_note_id = ?
        ORDER BY ai.id
    """, (id,)).fetchall()]
    conn.close()
    return jsonify({'note': note, 'attendees': attendees, 'action_items': action_items})


@bp.route('/action/<int:id>/status', methods=['POST'])
def update_action_status(id):
    d = request.get_json() or {}
    status = d.get('status', 'belum')
    conn = get_db()
    conn.execute("UPDATE action_items SET status = ? WHERE id = ?", (status, id))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': id, 'status': status})
