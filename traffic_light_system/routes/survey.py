from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from .. import db
from ..models.traffic_light import TrafficLight, Survey
from ..models.user import User

bp = Blueprint('survey', __name__)

@bp.route('/surveys')
@login_required
def index():
    # Join with TrafficLight to get location
    surveys = db.session.query(Survey, TrafficLight)\
        .join(TrafficLight, Survey.traffic_light_id == TrafficLight.id)\
        .all()
    
    # Calculate averages
    avg_stats = db.session.query(
        func.avg(Survey.waiting_time).label('avg_waiting_time'),
        func.avg(Survey.satisfaction).label('avg_satisfaction')
    ).first()
    
    # Format survey data for template
    survey_data = []
    for survey, traffic_light in surveys:
        survey_data.append({
            'id': survey.id,
            'traffic_light_id': survey.traffic_light_id,
            'location': traffic_light.location,
            'waiting_time': survey.waiting_time,
            'congestion_level': survey.congestion_level,
            'satisfaction': survey.satisfaction,
            'time_of_day': survey.time_of_day,
            'features': survey.features,
            'comments': survey.comments,
            'created_at': survey.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return render_template('survey/index.html', 
                         surveys=survey_data,
                         avg_waiting_time=round(avg_stats.avg_waiting_time or 0, 1),
                         avg_satisfaction=round(avg_stats.avg_satisfaction or 0, 1))

@bp.route('/survey/new', methods=['GET', 'POST'])
@login_required
def new_survey():
    if request.method == 'POST':
        traffic_light_id = request.form.get('traffic_light_id')
        waiting_time = request.form.get('waiting_time')
        congestion_level = request.form.get('congestion_level')
        satisfaction = request.form.get('satisfaction')
        time_of_day = request.form.get('time_of_day')
        features = request.form.getlist('features[]')
        comments = request.form.get('comments')
        
        survey = Survey(
            user_id=current_user.id,
            traffic_light_id=traffic_light_id,
            waiting_time=int(float(waiting_time)),
            congestion_level=int(congestion_level),
            satisfaction=int(satisfaction),
            time_of_day=time_of_day,
            features=features,
            comments=comments
        )
        
        db.session.add(survey)
        db.session.commit()
        
        flash('Thank you for your evaluation! Your feedback helps improve our smart traffic system.', 'success')
        return redirect(url_for('survey.index'))
    
    traffic_lights = TrafficLight.query.all()
    return render_template('survey/new.html', traffic_lights=traffic_lights)

@bp.route('/surveys/view')
@login_required
def view_surveys():
    # Debug: Check if there are any surveys in the database
    survey_count = db.session.query(func.count(Survey.id)).scalar()
    print(f"Total number of surveys in database: {survey_count}")
    
    # Debug: Get a sample survey
    sample_survey = db.session.query(Survey).first()
    if sample_survey:
        print(f"Sample survey - ID: {sample_survey.id}, Satisfaction: {sample_survey.satisfaction}, Waiting Time: {sample_survey.waiting_time}")
    
    # Calculate averages using SQLAlchemy
    avg_stats = db.session.query(
        func.avg(Survey.waiting_time).label('avg_waiting_time'),
        func.avg(Survey.satisfaction).label('avg_satisfaction')
    ).first()
    
    print(f"Average stats from query - Waiting Time: {avg_stats.avg_waiting_time}, Satisfaction: {avg_stats.avg_satisfaction}")
    
    # Join with TrafficLight and User to get location and username
    surveys = db.session.query(Survey, TrafficLight, User)\
        .join(TrafficLight, Survey.traffic_light_id == TrafficLight.id)\
        .join(User, Survey.user_id == User.id)\
        .all()
    
    survey_data = []
    for survey_tuple in surveys:
        survey = survey_tuple[0]  # Get the Survey object from the tuple
        traffic_light = survey_tuple[1]  # Get the TrafficLight object
        user = survey_tuple[2]  # Get the User object
        
        survey_data.append({
            'id': survey.id,
            'location': traffic_light.location,
            'waiting_time': survey.waiting_time,
            'congestion_level': survey.congestion_level,
            'satisfaction': survey.satisfaction,
            'time_of_day': survey.time_of_day,
            'user': user.username,
            'created_at': survey.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'comments': survey.comments
        })
    
    # Debug: Print the final values being sent to template
    print(f"Values being sent to template - Avg Waiting Time: {round(avg_stats.avg_waiting_time or 0, 1)}, Avg Satisfaction: {round(avg_stats.avg_satisfaction or 0, 1)}")
    
    return render_template('survey/view_surveys.html', 
                         surveys=survey_data,
                         avg_waiting_time=round(avg_stats.avg_waiting_time or 0, 1),
                         avg_satisfaction=round(avg_stats.avg_satisfaction or 0, 1))

@bp.route('/api/survey/stats')
@login_required
def survey_stats():
    traffic_light_id = request.args.get('traffic_light_id')
    surveys = Survey.query.filter_by(traffic_light_id=traffic_light_id).all()
    
    if not surveys:
        return jsonify({'error': 'No surveys found for this traffic light'})
    
    # Aggregate data by time of day
    time_data = {}
    for period in ['morning_rush', 'midday', 'evening_rush', 'evening', 'night']:
        period_surveys = [s for s in surveys if s.time_of_day == period]
        if period_surveys:
            time_data[period] = {
                'avg_waiting': sum(s.waiting_time for s in period_surveys) / len(period_surveys),
                'avg_congestion': sum(s.congestion_level for s in period_surveys) / len(period_surveys),
                'avg_satisfaction': sum(s.satisfaction for s in period_surveys) / len(period_surveys),
                'count': len(period_surveys)
            }
    
    # Analyze feature effectiveness
    feature_counts = {}
    for survey in surveys:
        if survey.features:
            for feature in survey.features:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
    
    data = {
        'waiting_times': [s.waiting_time for s in surveys],
        'congestion_levels': [s.congestion_level for s in surveys],
        'satisfaction_scores': [s.satisfaction for s in surveys],
        'time_data': time_data,
        'feature_counts': feature_counts,
        'total_surveys': len(surveys),
        'recent_comments': [s.comments for s in surveys[-5:]]  # Last 5 comments
    }
    
    return jsonify(data) 