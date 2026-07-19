import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from database_models import db
from database_models.user import User
from database_models.log import ActivityLog
from authentication.security import verify_password, hash_password, sanitize_input_text, rate_limit

auth_bp = Blueprint('auth', __name__)

# Allowed file extensions for profile pictures
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        full_name = sanitize_input_text(request.form.get('full_name', ''))
        username = sanitize_input_text(request.form.get('username', '')).lower()
        email = sanitize_input_text(request.form.get('email', '')).lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not full_name or not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        # Check existing user
        user_by_name = User.query.filter_by(username=username).first()
        if user_by_name:
            flash('Username is already taken.', 'danger')
            return render_template('register.html')

        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email:
            flash('Email address is already registered.', 'danger')
            return render_template('register.html')

        try:
            # Create user
            hashed = hash_password(password)
            new_user = User(
                full_name=full_name,
                username=username,
                email=email,
                password_hash=hashed
            )
            db.session.add(new_user)
            db.session.commit()

            # Log event
            log = ActivityLog(
                user_id=new_user.id,
                action="User registered account",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            db.session.add(log)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(limit=10, period_seconds=60)
def login():
    """Handle user login authentication."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        login_id = sanitize_input_text(request.form.get('login_id', '')).lower()  # Can be username or email
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        if not login_id or not password:
            flash('All fields are required.', 'danger')
            return render_template('login.html')

        # Find user by email or username
        user = User.query.filter((User.username == login_id) | (User.email == login_id)).first()

        if not user or not verify_password(password, user.password_hash):
            # Log failed login attempt
            log = ActivityLog(
                user_id=None,
                action=f"Failed login attempt for account ID: {login_id}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            db.session.add(log)
            db.session.commit()

            flash('Invalid username/email or password.', 'danger')
            return render_template('login.html')

        if not user.is_active:
            flash('This account is suspended. Contact Administrator.', 'danger')
            return render_template('login.html')

        # Successful login
        login_user(user, remember=remember)

        # Log action
        log = ActivityLog(
            user_id=user.id,
            action="Logged in successfully",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()

        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('main.admin'))
        
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out user and clear sessions."""
    log = ActivityLog(
        user_id=current_user.id,
        action="Logged out successfully",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()

    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update profile information and profile photo."""
    full_name = sanitize_input_text(request.form.get('full_name', ''))
    email = sanitize_input_text(request.form.get('email', '')).lower()
    
    if not full_name or not email:
        flash('Fields cannot be empty.', 'danger')
        return redirect(url_for('main.profile'))

    # Check email duplicate
    email_check = User.query.filter(User.email == email, User.id != current_user.id).first()
    if email_check:
        flash('Email is already in use by another account.', 'danger')
        return redirect(url_for('main.profile'))

    current_user.full_name = full_name
    current_user.email = email

    # Handle profile pic file upload
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and file.filename != '' and allowed_file(file.filename):
            # Create uploads folder if missing
            upload_folder = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            filename = f"user_{current_user.id}_{secure_filename(file.filename)}"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            current_user.profile_pic = filename

    try:
        db.session.commit()
        # Log action
        log = ActivityLog(
            user_id=current_user.id,
            action="Updated profile details",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()

        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Update failed: {str(e)}', 'danger')

    return redirect(url_for('main.profile'))


@auth_bp.route('/profile/password', methods=['POST'])
@login_required
def change_password():
    """Update password."""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not current_password or not new_password or not confirm_password:
        flash('All password fields are required.', 'danger')
        return redirect(url_for('main.profile'))

    if not verify_password(current_password, current_user.password_hash):
        flash('Incorrect current password.', 'danger')
        return redirect(url_for('main.profile'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('main.profile'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters.', 'danger')
        return redirect(url_for('main.profile'))

    try:
        current_user.password_hash = hash_password(new_password)
        db.session.commit()

        # Log action
        log = ActivityLog(
            user_id=current_user.id,
            action="Updated user password",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()

        flash('Password changed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Password change failed: {str(e)}', 'danger')

    return redirect(url_for('main.profile'))


@auth_bp.route('/profile/theme', methods=['POST'])
@login_required
def update_theme():
    """API endpoint to save theme preference asynchronously."""
    data = request.get_json() or {}
    theme = sanitize_input_text(data.get('theme', 'midnight-blue'))
    
    current_user.theme_preference = theme
    db.session.commit()

    # Log action
    log = ActivityLog(
        user_id=current_user.id,
        action=f"Changed theme preference to {theme}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'success': True, 'theme': theme})
