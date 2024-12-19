from traffic_light_system import create_app, db
from traffic_light_system.models.traffic_light import TrafficLight, Survey
from traffic_light_system.models.user import User
import random
from datetime import datetime, timedelta

app = create_app()

def generate_traffic_lights():
    locations = [
        # Zurich
        "Bahnhofstrasse & Central", "Paradeplatz", "Bellevue & Quaibrücke", "Limmatquai & Central",
        "Löwenplatz", "Sihlstrasse & Bahnhofplatz", "Uraniastrasse & Central", "Talstrasse & Paradeplatz",
        
        # Geneva
        "Rue du Mont-Blanc & Quai des Bergues", "Place de Cornavin", "Rue du Rhône & Rue du Commerce",
        "Boulevard Georges-Favon", "Place de Bel-Air", "Rue de la Croix-d'Or", "Place Neuve",
        
        # Bern
        "Bundesplatz", "Bahnhofplatz", "Kornhausplatz", "Bärenplatz", "Waisenhausplatz",
        "Hirschengraben & Bubenbergplatz", "Zytglogge", "Kramgasse & Gerechtigkeitsgasse",
        
        # Basel
        "Marktplatz", "Barfüsserplatz", "Aeschenplatz", "Centralbahnplatz", "Messeplatz",
        "Claraplatz", "Wettsteinplatz", "St. Alban-Tor",
        
        # Lausanne
        "Place de la Riponne", "Place Saint-François", "Rue Centrale", "Place de la Palud",
        "Avenue du Théâtre", "Place de la Gare", "Rue de Bourg", "Place de l'Europe",
        
        # Fribourg
        "Place Python", "Boulevard de Pérolles", "Rue de Romont", "Place Georges-Python",
        "Avenue de la Gare", "Rue de Lausanne", "Place Jean-Tinguely", "Grand-Places",
        
        # Lucerne
        "Schwanenplatz", "Löwenplatz", "Bahnhofplatz", "Pilatusplatz",
        "Bundesplatz", "Hertensteinstrasse", "Kapellplatz", "Weinmarkt"
    ] * 2  # Duplicate the list to have enough locations for 100 traffic lights
    
    traffic_lights = []
    for i, location in enumerate(locations[:100], 1):
        traffic_light = TrafficLight(
            name=f'TL-{i:03d}',
            location=location,
            density=round(random.uniform(0.3, 0.9), 2),
            green_duration=random.randint(30, 120),
            rush_hour_factor=round(random.uniform(0.4, 0.95), 2),
            sensors=random.randint(2, 6),  # 2-6 sensors per traffic light
            cameras=random.randint(1, 4)   # 1-4 cameras per traffic light
        )
        traffic_lights.append(traffic_light)
    
    return traffic_lights

def generate_surveys(traffic_lights, users):
    surveys = []
    comments = [
        "Traffic flow is excellent during off-peak hours at this Swiss intersection",
        "Extended waiting times during peak hours, typical for this busy Swiss location",
        "Green light duration needs adjustment for better flow at this intersection",
        "Well-coordinated with nearby traffic lights in the city center",
        "Requires optimization during rush hours in this busy Swiss district",
        "Smart traffic management system works efficiently at this location",
        "The adaptive system responds well to changing traffic patterns",
        "Pedestrian crossing timing is well-balanced for this busy area",
        "Emergency vehicle detection system works perfectly at this intersection",
        "Sensors effectively manage traffic flow during peak times",
        "Camera monitoring significantly improves traffic management here",
        "Smart timing system effectively handles local traffic patterns",
        "Excellent integration with Swiss public transport system",
        "Responsive to pedestrian traffic in this busy city area",
        "Bicycle-friendly timing at this Swiss intersection"
    ]
    
    time_periods = ['morning_rush', 'midday', 'evening_rush', 'evening', 'night']
    features = [
        ['pedestrian', 'emergency', 'bicycle'],
        ['adaptive', 'public_transport'],
        ['coordination', 'pedestrian'],
        ['emergency', 'public_transport', 'adaptive'],
        ['bicycle', 'coordination']
    ]
    
    for light in traffic_lights:
        num_surveys = random.randint(5, 15)
        for _ in range(num_surveys):
            user = random.choice(users)
            survey = Survey(
                user_id=user.id,
                traffic_light_id=light.id,
                waiting_time=random.randint(15, 180),
                congestion_level=random.randint(1, 5),
                satisfaction=random.randint(1, 5),
                time_of_day=random.choice(time_periods),
                features=random.choice(features),
                comments=random.choice(comments),
                created_at=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            surveys.append(survey)
    
    return surveys

if __name__ == "__main__":
    with app.app_context():
        # Clear existing data
        Survey.query.delete()
        TrafficLight.query.delete()
        db.session.commit()
        
        print("Generating traffic lights...")
        traffic_lights = generate_traffic_lights()
        for light in traffic_lights:
            db.session.add(light)
        db.session.commit()
        
        print("Generating sample surveys...")
        users = User.query.all()
        if not users:
            print("No users found. Please create some users first.")
        else:
            surveys = generate_surveys(traffic_lights, users)
            for survey in surveys:
                db.session.add(survey)
            db.session.commit()
            
        print(f"Successfully imported {len(traffic_lights)} traffic lights and {len(surveys)} surveys!") 