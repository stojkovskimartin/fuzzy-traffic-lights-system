from traffic_light_system import create_app, db
from traffic_light_system.models.user import User
from traffic_light_system.models.traffic_light import TrafficLight, Survey

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'TrafficLight': TrafficLight,
        'Survey': Survey
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if it doesn't exist
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True) 