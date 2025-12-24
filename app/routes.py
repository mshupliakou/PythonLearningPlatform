from flask import Blueprint, render_template, request, redirect, url_for
from . import db
from .models import Module, User
from .models import Module

main = Blueprint('main', __name__)

@main.route('/')
def base():
    return render_template('index.html')

@main.route('/modules')
def modules():
    all_courses = Module.query.all()
    return render_template('modules.html')


@main.route('/login')
def login():
    return render_template('login.html')

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