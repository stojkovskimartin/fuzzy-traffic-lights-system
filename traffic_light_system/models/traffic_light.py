from .. import db
from datetime import datetime

class TrafficLight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)  # Added description field
    density = db.Column(db.Float, default=0)
    green_duration = db.Column(db.Integer, default=60)
    rush_hour_factor = db.Column(db.Float, default=1.0)
    sensors = db.Column(db.Integer, default=0)
    cameras = db.Column(db.Integer, default=0)
    surveys = db.relationship('Survey', backref='traffic_light', lazy=True)

    def __repr__(self):
        return f'<TrafficLight {self.location}>'

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    traffic_light_id = db.Column(db.Integer, db.ForeignKey('traffic_light.id'), nullable=False)
    waiting_time = db.Column(db.Integer, nullable=False)  # Time in seconds
    congestion_level = db.Column(db.Integer, nullable=False)  # Scale 1-5
    satisfaction = db.Column(db.Integer, nullable=False)  # Scale 1-5
    time_of_day = db.Column(db.String(20), nullable=False)  # morning_rush, midday, evening_rush, evening, night
    features = db.Column(db.JSON)  # List of observed smart features
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'waiting_time': self.waiting_time,
            'congestion_level': self.congestion_level,
            'satisfaction': self.satisfaction,
            'time_of_day': self.time_of_day,
            'features': self.features,
            'comments': self.comments,
            'created_at': self.created_at.isoformat(),
            'traffic_light_location': self.traffic_light.location,
            'user_name': self.user.username
        } 