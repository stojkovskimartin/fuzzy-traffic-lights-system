from traffic_light_system import create_app, db
from traffic_light_system.models.traffic_light import TrafficLight

descriptions = {
    'Sihlstrasse & Bahnhofplatz': 'Major intersection connecting the train station area with high pedestrian and vehicle traffic',
    'Talstrasse & Paradeplatz': 'Central business district intersection with frequent public transport crossings',
    'Rue du Mont-Blanc & Quai des Bergues': 'Waterfront intersection with tourist attractions and shopping areas',
    'Place de Cornavin': 'Main railway station plaza with multiple public transport connections',
    'Rue du Rhône & Rue du Commerce': 'Prime shopping district with heavy pedestrian traffic',
    'Boulevard Georges-Favon': 'Major boulevard connecting cultural and business areas',
    'Place de Bel-Air': 'Historic center intersection with tram and bus connections',
    'Rue de la Croix-d\'Or': 'Shopping street intersection with high pedestrian volume',
    'Place Neuve': 'Cultural district intersection near theaters and museums'
}

def update_descriptions():
    app = create_app()
    with app.app_context():
        traffic_lights = TrafficLight.query.all()
        for light in traffic_lights:
            if light.location in descriptions:
                light.description = descriptions[light.location]
            else:
                light.description = 'Strategic traffic light location managing traffic flow'
        
        db.session.commit()
        print('Successfully updated traffic light descriptions')

if __name__ == '__main__':
    update_descriptions() 