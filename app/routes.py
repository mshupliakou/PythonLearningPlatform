from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from .models import  User
from .models import Module
import os
from werkzeug.utils import secure_filename

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
            return render_template('login.html')

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

    name = request.form.get('name')
    description = request.form.get('description')

    file = request.files.get('image')

    image_filename = 'default_course.jpg'

    if file and file.filename:
        filename = secure_filename(file.filename)
        save_path = os.path.join('app', 'static', 'images', 'modules', filename)
        file.save(save_path)
        image_filename = filename
    new_module = Module(name=name, description=description, image_path=image_filename)

    db.session.add(new_module)
    db.session.commit()

    return redirect(url_for('main.modules'))

@main.route('/delete_module/<int:module_id>', methods=['POST'])
@login_required
def delete_module(module_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    module = Module.query.get_or_404(module_id)

    if module.image_path and module.image_path != 'default_course.jpg':
        file_path = os.path.join('app', 'static', 'images', 'modules', module.image_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")

    db.session.delete(module)
    db.session.commit()

    return redirect(url_for('main.modules'))

@main.route('/edit_module/<int:module_id>', methods=['POST'])
@login_required
def edit_module(module_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    module = Module.query.get_or_404(module_id)

    name = request.form.get('name')
    description = request.form.get('description')
    file = request.files.get('image')

    module.name=name
    module.description=description

    if file and file.filename:
        filename = secure_filename(file.filename)
        save_path = os.path.join('app', 'static', 'images', 'modules', filename)
        file.save(save_path)
        module.image_path = filename

    db.session.commit()

    return redirect(url_for('main.modules'))

@main.route('/module/<int:module_id>')
def lessons_list(module_id):
    module = Module.query.get_or_404(module_id)
    return render_template('lessons_list.html', module=module)

@main.route('/create_lesson', methods=['POST'])
@login_required
def create_lesson():
    if current_user.role != 'admin':
        return redirect(url_for('main.lessons_list'))

    topic = request.form.get('topic')
    description = request.form.get('description')
    content = request.form.get('content')

    db.session.commit()

    return redirect(url_for('main.lessons_list'))