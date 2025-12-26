from . import db
from flask_login import login_user, logout_user, login_required, current_user
from .models import  User
from .models import Module
from .models import Lesson
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .models import Quiz, Question, Answer

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

@main.route('/delete_lesson/<int:id_lesson>', methods=['POST'])
@login_required
def delete_lesson(id_lesson):

    lesson = Lesson.query.get_or_404(id_lesson)
    module_id = lesson.id_module
    if current_user.role != 'admin':
        return redirect(url_for('main.lessons_list', module_id=module_id))
    db.session.delete(lesson)
    db.session.commit()
    return redirect(url_for('main.lessons_list', module_id=module_id))

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
    lessons = Lesson.query.filter_by(id_module=module_id).all()
    return render_template('lessons_list.html', module=module, lessons=lessons)

@main.route('/create_lesson/<int:module_id>', methods=['GET', 'POST'])
@login_required
def create_lesson(module_id):
    tinymce_key = os.environ.get('TINYMCE_KEY')
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))
    if request.method == 'POST':
        topic = request.form.get('name')
        content = request.form.get('content')
        new_lesson = Lesson(topic=topic, content=content, id_module=module_id)
        db.session.add(new_lesson)
        db.session.commit()
        return redirect(url_for('main.lessons_list', module_id=module_id))
    return render_template('create_lesson.html', module_id=module_id, api_key=tinymce_key)


@main.route('/edit_lesson/<int:id_lesson>', methods=['GET', 'POST'])
@login_required
def edit_lesson(id_lesson):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))

    tinymce_key = os.environ.get('TINYMCE_KEY')

    lesson = Lesson.query.get_or_404(id_lesson)

    if request.method == 'POST':
        lesson.topic = request.form.get('name')
        lesson.content = request.form.get('content')

        db.session.commit()

        return redirect(url_for('main.lessons_list', module_id=lesson.id_module))

    return render_template('create_lesson.html', lesson=lesson, api_key=tinymce_key)


@main.route('/lesson/<int:id_lesson>')
def view_lesson(id_lesson):
    lesson = Lesson.query.get_or_404(id_lesson)
    id_module = lesson.id_module
    module = Module.query.get_or_404(id_module)
    return render_template('lesson.html', lesson=lesson, module=module)

@main.route('/create_quiz/<int:id_lesson>', methods=['GET'])
@login_required
def create_quiz(id_lesson):
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))
    lesson = Lesson.query.get_or_404(id_lesson)
    existing_quiz = lesson.quiz
    tinymce_key = os.environ.get('TINYMCE_KEY')
    return render_template('create_quiz.html', lesson=lesson, quiz=existing_quiz, api_key=tinymce_key)


@main.route('/save_quiz/<int:id_lesson>', methods=['POST'])
@login_required
def save_quiz(id_lesson):
    if current_user.role != 'admin':
        return "Access denied", 403

    data = request.get_json()
    lesson = Lesson.query.get_or_404(id_lesson)

    if lesson.quiz:
        db.session.delete(lesson.quiz)

    new_quiz = Quiz(title=data.get('title'), id_lesson=id_lesson)
    db.session.add(new_quiz)
    db.session.flush()

    for q_data in data.get('questions', []):
        new_question = Question(
            question=q_data['text'],
            id_quiz=new_quiz.id_quiz
        )
        db.session.add(new_question)
        db.session.flush()

        for a_data in q_data.get('answers', []):
            new_answer = Answer(
                answer=a_data['text'],
                is_right=a_data['is_correct'],
                id_question=new_question.id_question
            )
            db.session.add(new_answer)

    db.session.commit()
    return {'status': 'success'}, 200


@main.route('/delete_quiz/<int:id_quiz>', methods=['POST'])
@login_required
def delete_quiz(id_quiz):
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    quiz = Quiz.query.get_or_404(id_quiz)
    lesson_id = quiz.id_lesson
    db.session.delete(quiz)
    db.session.commit()

    return redirect(url_for('main.view_lesson', id_lesson=lesson_id))
