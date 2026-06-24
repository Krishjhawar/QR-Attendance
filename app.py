# app.py - Main Flask application entry point
# Run with: python app.py

from flask import Flask
from flask_login import LoginManager
from config import Config
from models.user_model import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth_routes import auth
    from routes.teacher_routes import teacher
    from routes.student_routes import student
    from routes.attendance_routes import attendance

    app.register_blueprint(auth)
    app.register_blueprint(teacher)
    app.register_blueprint(student)
    app.register_blueprint(attendance)

    with app.app_context():
        db.create_all()
        seed_demo_users()

    return app


def seed_demo_users():
    from models.user_model import User
    from models.user_model import db
    if User.query.count() == 0:
        demo_users = [
            User(username='teacher1', password='teach123', role='teacher'),
            User(username='teacher2', password='teach123', role='teacher'),
            User(username='student1', password='stud123', role='student'),
            User(username='student2', password='stud123', role='student'),
            User(username='student3', password='stud123', role='student'),
            User(username='student4', password='stud123', role='student'),
            User(username='student5', password='stud123', role='student'),
        ]
        db.session.add_all(demo_users)
        db.session.commit()
        print('[AcadScan] Demo users seeded.')


if __name__ == '__main__':
    app = create_app()
    
    # Import after app creation so Config is loaded
    from config import Config
    
    print('\n========================================')
    print('  AcadScan - Smart QR Attendance System')
    print(f'  Local:   http://127.0.0.1:{Config.SERVER_PORT}')
    print(f'  Network: http://{Config.SERVER_IP}:{Config.SERVER_PORT}')
    print('  Teacher: teacher1 / teach123')
    print('  Student: student1 / stud123')
    print('========================================\n')

    # host='0.0.0.0' means Flask listens on ALL network interfaces
    # This allows phones on the same WiFi to connect via your LAN IP
    # Without this, Flask only listens on 127.0.0.1 (localhost only)
    app.run(debug=True, host='0.0.0.0', port=Config.SERVER_PORT)