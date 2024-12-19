from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from .. import db
from ..models.traffic_light import TrafficLight, Survey

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def index():
    traffic_lights = TrafficLight.query.all()
    
    # Get all surveys with traffic light data
    surveys = db.session.query(Survey).all()
    
    # Calculate averages properly
    avg_satisfaction = 0
    avg_waiting_time = 0
    survey_count = len(surveys)
    
    if survey_count > 0:
        total_satisfaction = sum(survey.satisfaction for survey in surveys)
        total_waiting_time = sum(survey.waiting_time for survey in surveys)
        
        avg_satisfaction = total_satisfaction / survey_count
        avg_waiting_time = total_waiting_time / survey_count
    
    # Serialize traffic light data for charts
    traffic_light_data = [{
        'id': light.id,
        'location': light.location,
        'description': light.description,
        'density': light.density,
        'green_duration': light.green_duration,
        'rush_hour_factor': light.rush_hour_factor,
        'sensors': light.sensors,
        'cameras': light.cameras,
        'status': 'Active'
    } for light in traffic_lights]
    
    # Serialize survey data
    survey_data = [{
        'id': survey.id,
        'satisfaction': survey.satisfaction,
        'waiting_time': survey.waiting_time,
        'traffic_light_id': survey.traffic_light_id,
        'created_at': survey.created_at.strftime('%Y-%m-%d %H:%M:%S') if survey.created_at else None
    } for survey in surveys]
    
    return render_template('dashboard/index.html', 
                         traffic_lights=traffic_light_data,
                         raw_traffic_lights=traffic_lights,
                         surveys=survey_data,
                         avg_satisfaction=round(avg_satisfaction, 1),
                         avg_waiting_time=round(avg_waiting_time, 1))

@bp.route('/dashboard/manage-traffic-lights')
@login_required
def manage_traffic_lights():
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    traffic_lights = TrafficLight.query.all()
    return render_template('dashboard/manage_traffic_lights.html', traffic_lights=traffic_lights)

@bp.route('/dashboard/traffic-light/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_traffic_light(id):
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    traffic_light = TrafficLight.query.get_or_404(id)
    
    if request.method == 'POST':
        traffic_light.name = request.form.get('name')
        traffic_light.location = request.form.get('location')
        traffic_light.green_duration = int(request.form.get('green_duration'))
        traffic_light.rush_hour_factor = float(request.form.get('rush_hour_factor'))
        traffic_light.sensors = int(request.form.get('sensors'))
        traffic_light.cameras = int(request.form.get('cameras'))
        
        db.session.commit()
        flash('Traffic light updated successfully!', 'success')
        return redirect(url_for('dashboard.manage_traffic_lights'))
    
    return render_template('dashboard/edit_traffic_light.html', traffic_light=traffic_light)

@bp.route('/dashboard/traffic-light/new', methods=['GET', 'POST'])
@login_required
def new_traffic_light():
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        traffic_light = TrafficLight(
            name=request.form.get('name'),
            location=request.form.get('location'),
            green_duration=int(request.form.get('green_duration')),
            rush_hour_factor=float(request.form.get('rush_hour_factor')),
            sensors=int(request.form.get('sensors')),
            cameras=int(request.form.get('cameras'))
        )
        
        db.session.add(traffic_light)
        db.session.commit()
        flash('New traffic light added successfully!', 'success')
        return redirect(url_for('dashboard.manage_traffic_lights'))
    
    return render_template('dashboard/new_traffic_light.html')

@bp.route('/dashboard/traffic-light/<int:id>/delete', methods=['POST'])
@login_required
def delete_traffic_light(id):
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Access denied. Admin privileges required.'})
    
    traffic_light = TrafficLight.query.get_or_404(id)
    db.session.delete(traffic_light)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Traffic light deleted successfully!'})

@bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    traffic_lights = TrafficLight.query.all()
    surveys = Survey.query.all()
    
    # Calculate statistics
    stats = {
        'total_traffic_lights': len(traffic_lights),
        'total_surveys': len(surveys),
        'avg_satisfaction': sum(s.satisfaction for s in surveys) / len(surveys) if surveys else 0,
        'avg_waiting_time': sum(s.waiting_time for s in surveys) / len(surveys) if surveys else 0,
        'locations': list(set(t.location for t in traffic_lights)),
        'density_data': [{'location': t.location, 'density': t.density} for t in traffic_lights],
        'waiting_times': [{'location': t.location, 'time': t.green_duration} for t in traffic_lights]
    }
    
    return jsonify(stats)

@bp.route('/dashboard/analyze', methods=['POST'])
@login_required
def analyze_traffic_light():
    data = request.get_json()
    traffic_light_id = data.get('traffic_light_id')
    
    if not traffic_light_id:
        return jsonify({
            'success': False,
            'message': 'Traffic light ID is required'
        })
    
    traffic_light = TrafficLight.query.get_or_404(traffic_light_id)
    surveys = Survey.query.filter_by(traffic_light_id=traffic_light_id).all()
    
    # Calculate recommended changes based on surveys and current settings
    avg_waiting_time = sum(s.waiting_time for s in surveys) / len(surveys) if surveys else 0
    avg_congestion = sum(s.congestion_level for s in surveys) / len(surveys) if surveys else 0
    
    # Adjust green duration based on waiting time and congestion
    recommended_duration = traffic_light.green_duration
    if avg_waiting_time > 60:  # If average waiting time is more than 60 seconds
        recommended_duration = min(120, recommended_duration + 15)  # Increase but cap at 120s
    elif avg_waiting_time < 30:  # If average waiting time is less than 30 seconds
        recommended_duration = max(30, recommended_duration - 10)  # Decrease but not below 30s
    
    # Adjust rush hour factor based on congestion level
    recommended_factor = traffic_light.rush_hour_factor
    if avg_congestion > 3.5:  # High congestion
        recommended_factor = min(0.95, recommended_factor + 0.1)
    elif avg_congestion < 2.5:  # Low congestion
        recommended_factor = max(0.4, recommended_factor - 0.1)
    
    return jsonify({
        'success': True,
        'message': 'Analysis completed successfully. Recommendations based on survey data and current traffic patterns.',
        'green_duration': recommended_duration,
        'rush_hour_factor': round(recommended_factor, 2)
    }) 

@bp.route('/dashboard/apply-analysis', methods=['POST'])
@login_required
def apply_analysis():
    if not current_user.is_admin():
        return jsonify({
            'success': False,
            'message': 'Access denied. Admin privileges required.'
        })
    
    data = request.get_json()
    traffic_light_id = data.get('traffic_light_id')
    green_duration = data.get('green_duration')
    rush_hour_factor = data.get('rush_hour_factor')
    
    if not all([traffic_light_id, green_duration, rush_hour_factor]):
        return jsonify({
            'success': False,
            'message': 'Missing required parameters'
        })
    
    traffic_light = TrafficLight.query.get_or_404(traffic_light_id)
    traffic_light.green_duration = green_duration
    traffic_light.rush_hour_factor = rush_hour_factor
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Changes applied successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error applying changes: ' + str(e)
        }) 