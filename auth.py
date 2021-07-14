from flask import Blueprint, render_template, jsonify, flash, request, redirect, url_for
from flask_login import current_user, login_user, login_required, logout_user, fresh_login_required
from werkzeug.urls import url_parse
from . import mysql
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print('user authenticated already')
        # return jsonify({'message': 'User already logged in'}), 200
        return redirect(url_for('main.profile'))

    if request.method == 'GET':
        return render_template('login.html')

    data = request.form

    if 'username' not in data or data['username'] == '' or \
            'password' not in data or data['password'] == '':
        flash("Please provide username and password")
        return redirect(url_for('auth.login'))

    # remember = True if data['remember'] else False

    user = User.get_user(data['username'])

    if user and User.check_password(user.get_password(), data['password']):
        login_user(user)
        nextPage = data['nextPage']
        print(nextPage)

        if not nextPage or url_parse(nextPage).netloc != '':
            return redirect(url_for('main.profile'))

        return redirect(nextPage)

    flash('Please check your login details and try again')
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if User.get_admin_count() > 0:
        return render_template('page_403.html')
    if request.method == 'GET':
        return render_template('signup.html')

    data = request.form

    if 'email' not in data or data['email'] == '' or \
            'username' not in data or data['username'] == '' or \
            'password' not in data or data['password'] == '':
        flash("All fields are required")
        return redirect(url_for('auth.signup'))

    print(data)

    username = data['username']
    password = data['password']
    email = data['email']

    user = User.get_user(username)

    if user:
        flash('UserName already exists')
        return redirect(url_for('auth.signup'))

    User.create_user(username, password, email, admin=1)

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# @auth.route('/users')
# @fresh_login_required
# def users():
#     if not current_user.is_root():
#         return render_template('page_403.html')

#     return render_template('users.html')
# <li><a class="dropdown-item" href="{{ url_for('auth.users') }}">Users</a></li>

@auth.route('/api/user', methods=['GET', 'POST'])
@login_required
def user():
    if not current_user.is_root():
        return jsonify({'error': 'Only root admins can access this section.'})

    if request.method == 'GET':
        users = User.get_users()
        return jsonify({'users': users})

    userData = request.form
    user = User.get_user(userData['name'])

    if user:
        return jsonify({'error': 'A user with the same name already exists.'})

    result = User.create_user(
        userData['name'], userData['password'], userData['email'], userData['admin'])

    return jsonify(result)


@auth.route('/api/user/<id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def user_edit(id):
    if not current_user.is_root():
        return jsonify({'error': 'Only root admins can access this section.'})

    if request.method == 'GET':
        user = User.get_user_by_id(id)
        return jsonify(user)

    if request.method == 'PUT':
        userData = request.form
        user = User.get_user_by_name_not_id(userData['name'], id)

        if user:
            return jsonify({'error': 'A user with the same name already exists.'})

        result = User.update_user(
            id, userData['name'], userData['email'], userData['admin'])

        if current_user.id == int(id):
            logout_user()
            # return redirect(url_for('auth.users'))

        return jsonify(result)

    if current_user.id == int(id):
        return jsonify({'error': 'You can\'t remove yourself.'})

    result = User.delete_user(id)

    return jsonify(result)


@auth.route('/api/resetPassword/<id>', methods=['POST'])
@login_required
def user_reset_password(id):
    if not current_user.is_root():
        return jsonify({'error': 'Only root admins can access this section.'})

    passwordData = request.form
    result = User.update_password(id, passwordData['password'])

    if current_user.id == int(id):
        logout_user()

    return jsonify(result)


@auth.route('/api/updatePassword', methods=['POST'])
@login_required
def user_update_password():
    passwordData = request.form
    password = passwordData['password']
    newPassword = passwordData['newPassword']

    if not User.check_password(current_user.get_password(), password):
        return jsonify({'error': 'Incorrect password'})

    result = User.update_password(str(current_user.id), newPassword)

    logout_user()

    return jsonify(result)
