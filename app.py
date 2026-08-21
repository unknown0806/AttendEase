import os
from flask import Flask, redirect, url_for, session
from config import Config
from db import db
from auth import get_current_user

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Context processor to inject current_user and user_role into all Jinja2 templates
    @app.context_processor
    def inject_user():
        user = get_current_user()
        return dict(
            current_user=user,
            user_role=session.get('role'),
            logged_in='user_id' in session
        )

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.teacher_routes import teacher_bp
    from routes.student_routes import student_bp
    from routes.admin_routes import admin_bp
    from routes.api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('role')
            if role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            elif role == 'student':
                return redirect(url_for('student.dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
