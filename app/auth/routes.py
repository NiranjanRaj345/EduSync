from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db, bcrypt
import logging

logger = logging.getLogger(__name__)
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
            logger.info(f"Login attempt for email: {form.email.data}")
            
            if user is None:
                logger.warning(f"Login failed: User not found for email: {form.email.data}")
                flash('Invalid email or password', 'danger')
                return redirect(url_for('auth.login'))
            
            if not bcrypt.check_password_hash(user.password_hash, form.password.data):
                logger.warning(f"Login failed: Invalid password for email: {form.email.data}")
                flash('Invalid email or password', 'danger')
                return redirect(url_for('auth.login'))
            
            login_success = login_user(user, remember=form.remember_me.data)
            if not login_success:
                logger.error(f"Login failed: Could not login user: {form.email.data}")
                flash('Error during login. Please try again.', 'danger')
                return redirect(url_for('auth.login'))
            
            logger.info(f"Login successful for user: {user.email} (role: {user.role})")
            next_page = request.args.get('next')
            
            if not next_page or urlparse(next_page).netloc != '':
                if user.role == 'student':
                    next_page = url_for('student.dashboard')
                else:
                    next_page = url_for('faculty.dashboard')
            return redirect(next_page)
            
        except Exception as e:
            logger.error(f"Database error during login: {str(e)}", exc_info=True)
            if "SSL SYSCALL error" in str(e):
                logger.error("Neon database SSL connection error detected")
            flash('A system error occurred. Please try again later.', 'danger')
            return redirect(url_for('auth.login'))
        
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        else:
            return redirect(url_for('faculty.dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
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
            logger.info(f"New user registered: {user.email} (role: {user.role})")
        
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            if "SSL SYSCALL error" in str(e):
                logger.error("Neon database SSL connection error detected during registration")
            db.session.rollback()
            flash('Error during registration. Please try again.', 'danger')
            return redirect(url_for('auth.signup'))
        
    return render_template('auth/signup.html', title='Sign Up', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
