import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config
from database import get_db

socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    CORS(app)
    socketio.init_app(
        app,
        async_mode=app.config['SOCKETIO_ASYNC_MODE'],
        cors_allowed_origins='*',
        logger=False,
        engineio_logger=False,
    )

    from routes.project import bp as project_bp
    from routes.activity import bp as activity_bp
    from routes.member import bp as member_bp
    from routes.budget import bp as budget_bp
    from routes.meeting import bp as meeting_bp
    from routes.report import bp as report_bp

    app.register_blueprint(project_bp, url_prefix='/projects')
    app.register_blueprint(activity_bp, url_prefix='/activities')
    app.register_blueprint(member_bp, url_prefix='/members')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(meeting_bp, url_prefix='/meeting')
    app.register_blueprint(report_bp, url_prefix='/report')

    from sockets import events  # noqa: F401 — registers socket handlers as side-effect

    @app.route('/')
    def index():
        conn = get_db()
        projects = [dict(r) for r in conn.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC"
        ).fetchall()]
        total_projects = len(projects)
        active_projects = sum(1 for p in projects if p['status'] == 'on_progress')
        recent_activities = [dict(r) for r in conn.execute("""
            SELECT a.*, p.judul as project_judul
            FROM activities a
            JOIN projects p ON a.project_id = p.id
            ORDER BY a.created_at DESC LIMIT 10
        """).fetchall()]
        conn.close()
        return render_template(
            'index.html',
            projects=projects,
            total_projects=total_projects,
            active_projects=active_projects,
            recent_activities=recent_activities,
            active_page='dashboard',
        )

    return app


if __name__ == '__main__':
    app = create_app()
    # use_reloader=False: Flask reloader + eventlet keduanya mencoba bind ke port yang sama
    # menyebabkan WinError 10048. Nonaktifkan reloader; restart manual jika ada perubahan.
    socketio.run(app, debug=True, host='0.0.0.0', port=5028, use_reloader=False)
