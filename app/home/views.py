from flask import render_template, session
from flask_login import login_required
from flask import abort, render_template
from flask_login import current_user, login_required
from . import home


@home.route('/')
def homepage():

    return render_template('home/index.html', title="Welcome")


@home.route('/dashboard')
@login_required
def dashboard():
    return render_template('home/dashboard.html', title="Dashboard")

@home.route('/admin/dashboard')
@login_required
def admin_dashboard():


    if not current_user.email=='bhavika301297@gmail.com':
        abort(403)

    return render_template('home/admin_dashboard.html', title="Dashboard")


