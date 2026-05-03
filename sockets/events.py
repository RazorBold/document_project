from flask_socketio import join_room, emit
from app import socketio
from database import get_db


@socketio.on('connect')
def on_connect():
    emit('notification', {'type': 'info', 'message': 'Terhubung ke server'})


@socketio.on('join_project')
def on_join(data):
    project_id = str(data.get('project_id', ''))
    if project_id:
        join_room(f'project_{project_id}')
        emit('notification', {
            'type': 'info',
            'message': f'Terhubung ke project #{project_id}',
        })


@socketio.on('update_activity')
def on_update_activity(data):
    activity_id = data.get('activity_id')
    changes = data.get('data', {})
    project_id = data.get('project_id')
    if not activity_id:
        return
    conn = get_db()
    row = conn.execute("SELECT * FROM activities WHERE id = ?", (activity_id,)).fetchone()
    if row:
        conn.execute("""
            UPDATE activities SET nama=?, tanggal=?, jam_mulai=?, jam_selesai=?,
                pelaksana=?, lokasi=?, output=?, status=?, catatan=?
            WHERE id=?
        """, (
            changes.get('nama', row['nama']),
            changes.get('tanggal', row['tanggal']),
            changes.get('jam_mulai', row['jam_mulai']),
            changes.get('jam_selesai', row['jam_selesai']),
            changes.get('pelaksana', row['pelaksana']),
            changes.get('lokasi', row['lokasi']),
            changes.get('output', row['output']),
            changes.get('status', row['status']),
            changes.get('catatan', row['catatan']),
            activity_id,
        ))
        conn.commit()
    conn.close()
    if project_id:
        socketio.emit('activity_updated',
                      {'activity_id': activity_id, 'changes': changes},
                      room=f'project_{project_id}')


@socketio.on('update_progress')
def on_update_progress(data):
    project_id = data.get('project_id')
    value = max(0, min(100, int(data.get('value', 0))))
    if not project_id:
        return
    conn = get_db()
    conn.execute("UPDATE projects SET progress = ? WHERE id = ?", (value, project_id))
    conn.commit()
    conn.close()
    socketio.emit('progress_update',
                  {'project_id': project_id, 'progress': value},
                  room=f'project_{project_id}')


@socketio.on('add_comment')
def on_add_comment(data):
    project_id = data.get('project_id')
    text = data.get('text', '')
    if project_id and text:
        socketio.emit('notification',
                      {'type': 'comment', 'message': text, 'project_id': project_id},
                      room=f'project_{project_id}')
