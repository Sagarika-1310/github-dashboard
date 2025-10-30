from flask import render_template, Blueprint

bp = Blueprint('auth', __name__)

# API Endpoints
@bp.route('/login')
def login():
    return render_template('login.html')


@bp.route('/logout')
def logout():
    return render_template('logout.html')
