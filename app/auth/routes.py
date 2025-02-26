from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db, bcrypt
from app.auth import bp
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                current_app.logger.warning(f"Login attempt with non-existent email: {form.email.data}")
                flash('Invalid email or password', 'danger')
                return redirect(url_for('auth.login', next=request.args.get('next')))
            
            if not bcrypt.check_password_hash(user.password_hash, form.password.data):
                current_app.logger.warning(f"Failed login attempt for user: {user.email}")
                flash('Invalid email or password', 'danger')
                return redirect(url_for('auth.login', next=request.args.get('next')))
            
            login_user(user, remember=form.remember_me.data)
            current_app.logger.info(f"Successful login for user: {user.email}")
            
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                if user.role == 'student':
                    next_page = url_for('student.dashboard', _external=True)
                else:
                    next_page = url_for('faculty.dashboard', _external=True)
            
            return redirect(next_page)
            
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        
    # Log form validation errors
    if form.errors:
        current_app.logger.warning(f"Login form validation errors: {form.errors}")
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            email=form.email.data,
            password_hash=hashed_password,
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/signup.html', title='Sign Up', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
