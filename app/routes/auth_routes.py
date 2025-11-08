"""Authentication urls for application"""

from flask import render_template, Blueprint, session, flash, request, redirect, url_for
from flask import current_app as app

from app.repositories.auth_repo import username_exists, create_user, init_auth_table

bp = Blueprint('auth', __name__)

USER = {"username": "admin", "password": "admin123"}


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Method to login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USER['username'] and password == USER['password']:
            app.logger.info(f"User {USER['username']} logged in successfully!")
            session['user'] = username
            return redirect(url_for('repo.home'))
        app.logger.info("Invalid credentials!")
        flash('Invalid credentials!', 'danger')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    """Method to logout"""
    app.logger.info(f"User {session['user']} logged out successfully!")
    return redirect(url_for('auth.login'))


@bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Method to create new user"""
    if request.method == 'POST':
        init_auth_table()
        username = request.form["username"]
        if username_exists(username):
            flash("Username already exists!")
            return redirect(url_for('auth.add_user'))
        user = request.form.to_dict()
        create_user(user)
        flash("Account created successfully! Login to proceed.")
    return render_template('add_user.html')
