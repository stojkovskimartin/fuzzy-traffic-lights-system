from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .. import db
from ..models.user import User

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        success = True
        
        if username and username != current_user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user != current_user:
                flash('Username already exists', 'danger')
                success = False
            else:
                current_user.username = username
        
        if email and email != current_user.email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email and existing_email != current_user:
                flash('Email already registered', 'danger')
                success = False
            else:
                current_user.email = email
        
        if current_password and new_password:
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                flash('Password updated successfully', 'success')
            else:
                flash('Current password is incorrect', 'danger')
                success = False
        
        if success:
            db.session.commit()
            flash('Settings updated successfully', 'success')
            return redirect(url_for('main.profile'))
    
    return render_template('main/settings.html') 