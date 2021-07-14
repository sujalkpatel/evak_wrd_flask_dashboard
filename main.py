from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import mysql, models

main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/about')
def about():
    return render_template('about.html')
