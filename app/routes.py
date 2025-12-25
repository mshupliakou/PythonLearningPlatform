from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from .models import Module, User
from .models import Module

main = Blueprint('main', __name__)

@main.route('/')
def base():
    return render_template('index.html')

@main.route('/modules')
def modules():
    all_courses = Module.query.all()
    return render_template('modules.html', courses=all_courses)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.modules'))

    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.modules'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return "Wrong username or password"

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.base'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            return "User already exists."
        new_user = User(username=username, email=email, role='user')
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/create_module', methods=['POST'])
@login_required
def create_module():
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        image_path = request.form.get('image_path')

        if not image_path:
            image_path = 'default_course.jpg'

        new_module = Module(name=name, description=description, image_path=image_path)
        db.session.add(new_module)
        db.session.commit()

        return redirect(url_for('main.modules'))

