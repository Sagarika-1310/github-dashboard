from flask import render_template, Blueprint, session, flash, request, redirect, url_for

bp = Blueprint('auth', __name__)

USER = {"username": "admin", "password": "admin123"}


# API Endpoints
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USER['username'] and password == USER['password']:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('repo.home'))
        flash('Invalid credentials!', 'danger')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    return render_template('logout.html')
