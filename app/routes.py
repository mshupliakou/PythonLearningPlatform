from . import db
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Module, Lesson, User_Answer, Quiz, Question, Answer
import os
from flask import jsonify, Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Create a Blueprint named 'main'. This helps organize the application routes.
main = Blueprint('main', __name__)


# --- HOME & GENERAL ROUTES ---

@main.route('/')
def base():
    """Renders the landing page (index.html)."""
    return render_template('index.html')


@main.route('/modules')
def modules():
    """
    Fetches all available modules (courses) from the database
    and renders them on the modules page.
    """
    all_courses = Module.query.all()
    return render_template('modules.html', courses=all_courses)


# --- AUTHENTICATION ROUTES ---

@main.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    GET: Renders the login form.
    POST: Processes the form data, verifies credentials, and logs the user in.
    """
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.modules'))

    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')

        # Find user by username
        user = User.query.filter_by(username=username).first()

        # Verify password hash
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
    """Logs out the current user and redirects to the home page."""
    logout_user()
    return redirect(url_for('main.base'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles new user registration.
    Checks if email already exists, creates a new User object,
    hashes the password, and saves to DB.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            return "User already exists."  # Simple error return

        # Create new user instance (default role is 'user')
        new_user = User(username=username, email=email, role='user')
        new_user.set_password(password)  # Hash password

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('register.html')


# --- MODULE MANAGEMENT (ADMIN ONLY) ---

@main.route('/create_module', methods=['POST'])
@login_required
def create_module():
    """
    Creates a new learning module.
    Only accessible by users with 'admin' role.
    Handles image upload for the module cover.
    """
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    name = request.form.get('name')
    description = request.form.get('description')
    file = request.files.get('image')

    image_filename = 'default_course.jpg'  # Default image

    # Process image upload if provided
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Construct path: app/static/images/modules/filename
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
    """
    Deletes a module and its associated image file (if not default).
    """
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    module = Module.query.get_or_404(module_id)

    # Remove the image file from the server to save space
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
    """Updates module details (name, description, image)."""
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    module = Module.query.get_or_404(module_id)

    name = request.form.get('name')
    description = request.form.get('description')
    file = request.files.get('image')

    module.name = name
    module.description = description

    if file and file.filename:
        filename = secure_filename(file.filename)
        save_path = os.path.join('app', 'static', 'images', 'modules', filename)
        file.save(save_path)
        module.image_path = filename

    db.session.commit()

    return redirect(url_for('main.modules'))


# --- LESSON MANAGEMENT ---

@main.route('/module/<int:module_id>')
def lessons_list(module_id):
    """Displays the list of lessons within a specific module."""
    module = Module.query.get_or_404(module_id)
    lessons = Lesson.query.filter_by(id_module=module_id).all()
    return render_template('lessons_list.html', module=module, lessons=lessons)


@main.route('/create_lesson/<int:module_id>', methods=['GET', 'POST'])
@login_required
def create_lesson(module_id):
    """
    Admin: Creates a new lesson.
    GET: Renders the editor (TinyMCE).
    POST: Saves the lesson content to DB.
    """
    tinymce_key = os.environ.get('TINYMCE_KEY')
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    if request.method == 'POST':
        topic = request.form.get('name')
        content = request.form.get('content')  # HTML content from editor
        new_lesson = Lesson(topic=topic, content=content, id_module=module_id)
        db.session.add(new_lesson)
        db.session.commit()
        return redirect(url_for('main.lessons_list', module_id=module_id))

    return render_template('create_lesson.html', module_id=module_id, api_key=tinymce_key)


@main.route('/edit_lesson/<int:id_lesson>', methods=['GET', 'POST'])
@login_required
def edit_lesson(id_lesson):
    """Admin: Edits an existing lesson."""
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


@main.route('/delete_lesson/<int:id_lesson>', methods=['POST'])
@login_required
def delete_lesson(id_lesson):
    """Admin: Deletes a lesson."""
    lesson = Lesson.query.get_or_404(id_lesson)
    module_id = lesson.id_module

    if current_user.role != 'admin':
        return redirect(url_for('main.lessons_list', module_id=module_id))

    db.session.delete(lesson)
    db.session.commit()
    return redirect(url_for('main.lessons_list', module_id=module_id))


@main.route('/lesson/<int:id_lesson>')
def view_lesson(id_lesson):
    """View a single lesson page."""
    lesson = Lesson.query.get_or_404(id_lesson)
    id_module = lesson.id_module
    module = Module.query.get_or_404(id_module)
    return render_template('lesson.html', lesson=lesson, module=module)


# --- QUIZ MANAGEMENT (CREATION & EDITING) ---

@main.route('/create_quiz/<int:id_lesson>', methods=['GET'])
@login_required
def create_quiz(id_lesson):
    """
    Admin: Renders the Quiz Editor page.
    Passes the existing quiz (if any) to populate the form for editing.
    """
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    lesson = Lesson.query.get_or_404(id_lesson)
    existing_quiz = lesson.quiz  # Relationship to get the quiz attached to this lesson
    tinymce_key = os.environ.get('TINYMCE_KEY')

    return render_template('create_quiz.html', lesson=lesson, quiz=existing_quiz, api_key=tinymce_key)


@main.route('/save_quiz/<int:id_lesson>', methods=['POST'])
@login_required
def save_quiz(id_lesson):
    """
    Admin: API Endpoint to save or update a quiz.
    Expects JSON data with title, questions, and answers.
    Strategy: Deletes the old quiz (if exists) and creates a fresh structure to avoid complexity.
    """
    if current_user.role != 'admin':
        return "Access denied", 403

    data = request.get_json()
    lesson = Lesson.query.get_or_404(id_lesson)

    # 1. Delete old quiz to perform a full update
    if lesson.quiz:
        db.session.delete(lesson.quiz)

    # 2. Create new Quiz
    new_quiz = Quiz(title=data.get('title'), id_lesson=id_lesson)
    db.session.add(new_quiz)
    db.session.flush()  # Flush to generate id_quiz for questions to use

    # 3. Loop through questions from JSON
    for q_data in data.get('questions', []):
        new_question = Question(
            question=q_data['text'],
            id_quiz=new_quiz.id_quiz
        )
        db.session.add(new_question)
        db.session.flush()  # Flush to generate id_question for answers to use

        # 4. Loop through answers for this question
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
    """Admin: Deletes a quiz (Cascade delete handles questions/answers in DB)."""
    if current_user.role != 'admin':
        return redirect(url_for('main.modules'))

    quiz = Quiz.query.get_or_404(id_quiz)
    lesson_id = quiz.id_lesson
    db.session.delete(quiz)
    db.session.commit()

    return redirect(url_for('main.view_lesson', id_lesson=lesson_id))


# --- QUIZ TAKING & SCORING ---

@main.route('/quiz/<int:id_quiz>', methods=['GET', 'POST'])
@login_required
def quiz(id_quiz):
    """
    Handles taking a quiz.
    POST: Processes AJAX submission, saves user answers, calculates score.
    GET: Displays the quiz, checks if already taken to show results immediately.
    """
    quiz = Quiz.query.get_or_404(id_quiz)

    # === HANDLE SUBMISSION (AJAX) ===
    if request.method == 'POST':
        data = request.get_json()
        answers_data = data.get('answers', {})  # Dictionary {question_id: answer_id}

        score = 0
        total = len(quiz.questions)

        # Process each submitted answer
        for q_id, a_id in answers_data.items():
            # Check if this user already answered this specific answer (avoid duplicates)
            existing = User_Answer.query.filter_by(id_user=current_user.id_user, id_answer=int(a_id)).first()
            if not existing:
                # Save the user's choice to the database
                new_ua = User_Answer(id_user=current_user.id_user, id_answer=int(a_id))
                db.session.add(new_ua)

            # Check if the selected answer is correct to calculate score
            ans = Answer.query.get(int(a_id))
            if ans and ans.is_right:
                score += 1

        db.session.commit()

        # Calculate percentage
        percentage = round((score / total) * 100) if total > 0 else 0

        # Return JSON response for the frontend JS
        return jsonify({
            'success': True,
            'score': score,
            'total': total,
            'percentage': percentage
        })

    # === HANDLE PAGE LOAD (GET) ===

    # We need to check if the user has ALREADY taken this quiz to show their result
    user_answers_ids = []
    already_taken = False
    score = 0
    total = len(quiz.questions)

    # Loop through all questions in this quiz
    for q in quiz.questions:
        for a in q.answers:
            # Check if current user has selected this specific answer option
            ua = User_Answer.query.filter_by(id_user=current_user.id_user, id_answer=a.id_answer).first()
            if ua:
                user_answers_ids.append(a.id_answer)  # Add to list of selected IDs for frontend styling
                already_taken = True
                if a.is_right:
                    score += 1

    percentage = round((score / total) * 100) if total > 0 else 0

    return render_template('quiz.html',
                           quiz=quiz,
                           user_answers_ids=user_answers_ids,  # List of IDs user selected
                           already_taken=already_taken,  # Boolean flag to disable inputs
                           percentage=percentage)  # Score to display