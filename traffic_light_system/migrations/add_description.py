from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add description column
    op.add_column('traffic_light', sa.Column('description', sa.Text, nullable=True))
    
    # Update existing records with descriptions
    op.execute("""
        UPDATE traffic_light
        SET description = CASE location
            WHEN 'Sihlstrasse & Bahnhofplatz' THEN 'Major intersection connecting the train station area with high pedestrian and vehicle traffic'
            WHEN 'Talstrasse & Paradeplatz' THEN 'Central business district intersection with frequent public transport crossings'
            WHEN 'Rue du Mont-Blanc & Quai des Bergues' THEN 'Waterfront intersection with tourist attractions and shopping areas'
            WHEN 'Place de Cornavin' THEN 'Main railway station plaza with multiple public transport connections'
            WHEN 'Rue du Rhône & Rue du Commerce' THEN 'Prime shopping district with heavy pedestrian traffic'
            WHEN 'Boulevard Georges-Favon' THEN 'Major boulevard connecting cultural and business areas'
            WHEN 'Place de Bel-Air' THEN 'Historic center intersection with tram and bus connections'
            WHEN 'Rue de la Croix-d''Or' THEN 'Shopping street intersection with high pedestrian volume'
            WHEN 'Place Neuve' THEN 'Cultural district intersection near theaters and museums'
            ELSE 'Strategic traffic light location managing traffic flow'
        END
        WHERE description IS NULL;
    """) 