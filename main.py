from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import hashlib
import os
import redis
import json
from application.celery_config import app as celery_app
import traceback
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Harsh/Desktop/Mad2/quiz.db?timeout=30'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key'
db = SQLAlchemy(app)
CORS(app)

# Redis setup for caching with error handling
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    print("Connected to Redis successfully")
except redis.ConnectionError as e:
    print(f"Failed to connect to Redis: {e}")
    redis_client = None

# Celery task
@celery_app.task
def log_user_registration(user_id, email_id):
    with open('registration_log.txt', 'a') as f:
        f.write(f"User registered: {user_id}, {email_id}\n")

# Models
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String, nullable=False, primary_key=True, unique=True)
    email_id = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    qualification = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default='user')

class Subject(db.Model):
    __tablename__ = 'subject'
    subject_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False, unique=True)

class Chapter(db.Model):
    __tablename__ = 'chapter'
    chapter_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False, unique=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable=False)

class Quiz(db.Model):
    __tablename__ = 'quiz'
    quiz_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    name = db.Column(db.String, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.chapter_id'), nullable=False)

class Question(db.Model):
    __tablename__ = 'question'
    question_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    question_statement = db.Column(db.String, nullable=False, unique=True)
    option_1 = db.Column(db.String, nullable=False)
    option_2 = db.Column(db.String, nullable=False)
    correct_option = db.Column(db.String, nullable=False)

class Score(db.Model):
    __tablename__ = 'score'
    score_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)  
    total_score = db.Column(db.Integer, nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email_id=email).first()
        if user and user.password == password:
            session['user_id'] = user.user_id
            return redirect(url_for('user_dashboard'))
        return "<h1>Invalid credentials</h1><a href='/login'>Try again</a>"
    return render_template('login.html')

@app.route('/dashboard')
def redirect_dashboard():
    return redirect(url_for('user_dashboard'))

@app.route('/user-dashboard')
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return "<h1>Please log in to access the dashboard.</h1><a href='/'>Login</a>"
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return "<h1>User data not found.</h1><a href='/'>Login</a>"
    if user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    if redis_client:
        try:
            user_data = redis_client.get(f"user:{user_id}")
            if user_data:
                user = json.loads(user_data)
                print(f"User data fetched from Redis: {user}")
                return render_template('user_dashboard.html', user_name=user['name'], user_id=user_id)
        except redis.ConnectionError as e:
            print(f"Redis error in user_dashboard: {e}")
    if user:
        print(f"User data fetched from database: {user.user_id}, {user.name}")
        return render_template('user_dashboard.html', user_name=user.name, user_id=user_id)
    return "<h1>User data not found.</h1><a href='/'>Login</a>"

@app.route('/admin-dashboard')
def admin_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return "<h1>Please log in to access the admin dashboard.</h1><a href='/'>Login</a>"
    user = User.query.filter_by(user_id=user_id).first()
    if not user or user.role != 'admin':
        return "<h1>Unauthorized access. Admins only.</h1><a href='/'>Login</a>"
    return render_template('admin_dashboard.html')

# API Endpoints
@app.route('/api/admin/users', methods=['GET'])
def get_users():
    users = User.query.filter(User.role != 'admin').all()
    return jsonify([{
        'user_id': user.user_id,
        'email_id': user.email_id,
        'name': user.name,
        'qualification': user.qualification,
        'dob': user.dob,
        'role': user.role
    } for user in users]), 200

@app.route('/api/admin/subjects', methods=['GET', 'POST'])
def manage_subjects():
    if request.method == 'GET':
        subjects = Subject.query.all()
        return jsonify([{
            'subject_id': subject.subject_id,
            'name': subject.name,
            'description': subject.description
        } for subject in subjects]), 200
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        if not name or not description:
            return jsonify({'message': 'Name and description are required'}), 400
        if Subject.query.filter_by(name=name).first():
            return jsonify({'message': 'Subject name already exists'}), 400
        if Subject.query.filter_by(description=description).first():
            return jsonify({'message': 'Subject description already exists'}), 400
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        return jsonify({'message': 'Subject created successfully'}), 201

@app.route('/api/admin/subjects/<int:subject_id>', methods=['PUT', 'DELETE'])
def edit_delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({'message': 'Subject not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        if not name or not description:
            return jsonify({'message': 'Name and description are required'}), 400
        if name != subject.name and Subject.query.filter_by(name=name).first():
            return jsonify({'message': 'Subject name already exists'}), 400
        if description != subject.description and Subject.query.filter_by(description=description).first():
            return jsonify({'message': 'Subject description already exists'}), 400
        subject.name = name
        subject.description = description
        db.session.commit()
        return jsonify({'message': 'Subject updated successfully'}), 200
    elif request.method == 'DELETE':
        db.session.delete(subject)
        db.session.commit()
        return jsonify({'message': 'Subject deleted successfully'}), 200

@app.route('/api/admin/chapters', methods=['GET', 'POST'])
def manage_chapters():
    if request.method == 'GET':
        chapters = Chapter.query.all()
        return jsonify([{
            'chapter_id': chapter.chapter_id,
            'name': chapter.name,
            'description': chapter.description,
            'subject_id': chapter.subject_id
        } for chapter in chapters]), 200
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        subject_id = data.get('subject_id')
        if not name or not description or not subject_id:
            return jsonify({'message': 'Name, description, and subject_id are required'}), 400
        if not Subject.query.get(subject_id):
            return jsonify({'message': 'Subject not found'}), 404
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return jsonify({'message': 'Chapter created successfully'}), 201

@app.route('/api/admin/chapters/<int:chapter_id>', methods=['PUT', 'DELETE'])
def edit_delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return jsonify({'message': 'Chapter not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        subject_id = data.get('subject_id')
        if not name or not description or not subject_id:
            return jsonify({'message': 'Name, description, and subject_id are required'}), 400
        if not Subject.query.get(subject_id):
            return jsonify({'message': 'Subject not found'}), 404
        chapter.name = name
        chapter.description = description
        chapter.subject_id = subject_id
        db.session.commit()
        return jsonify({'message': 'Chapter updated successfully'}), 200
    elif request.method == 'DELETE':
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({'message': 'Chapter deleted successfully'}), 200

@app.route('/api/admin/quizzes', methods=['GET', 'POST'])
def manage_quizzes():
    if request.method == 'GET':
        quizzes = Quiz.query.all()
        return jsonify([{
            'quiz_id': quiz.quiz_id,
            'name': quiz.name,
            'chapter_id': quiz.chapter_id
        } for quiz in quizzes]), 200
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        chapter_id = data.get('chapter_id')
        if not Chapter.query.get(chapter_id):
            return jsonify({'message': 'Chapter not found'}), 404
        new_quiz = Quiz(name=name, chapter_id=chapter_id)
        db.session.add(new_quiz)
        db.session.commit()
        return jsonify({'message': 'Quiz created successfully', 'quiz_id': new_quiz.quiz_id}), 201

@app.route('/api/admin/quizzes/<int:quiz_id>', methods=['PUT', 'DELETE'])
def edit_delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'message': 'Quiz not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        name = data.get('name')
        chapter_id = data.get('chapter_id')
        if not Chapter.query.get(chapter_id):
            return jsonify({'message': 'Chapter not found'}), 404
        quiz.name = name
        quiz.chapter_id = chapter_id
        db.session.commit()
        return jsonify({'message': 'Quiz updated successfully'}), 200
    elif request.method == 'DELETE':
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({'message': 'Quiz deleted successfully'}), 200

@app.route('/api/admin/questions', methods=['GET', 'POST'])
def manage_questions():
    if request.method == 'GET':
        questions = Question.query.all()
        return jsonify([{
            'question_id': question.question_id,
            'quiz_id': question.quiz_id,
            'question_statement': question.question_statement,
            'option_1': question.option_1,
            'option_2': question.option_2,
            'correct_option': question.correct_option
        } for question in questions]), 200
    elif request.method == 'POST':
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        question_statement = data.get('question_statement')
        option_1 = data.get('option_1')
        option_2 = data.get('option_2')
        correct_option = data.get('correct_option')
        if not all([quiz_id, question_statement, option_1, option_2, correct_option]):
            return jsonify({'message': 'All fields are required'}), 400
        if not Quiz.query.get(quiz_id):
            return jsonify({'message': 'Quiz not found'}), 404
        if Question.query.filter_by(question_statement=question_statement).first():
            return jsonify({'message': 'Question statement already exists'}), 400
        if correct_option not in [option_1, option_2]:
            return jsonify({'message': 'Correct option must match one of the provided options'}), 400
        new_question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option_1=option_1,
            option_2=option_2,
            correct_option=correct_option
        )
        db.session.add(new_question)
        db.session.commit()
        return jsonify({'message': 'Question created successfully'}), 201

@app.route('/api/admin/questions/<int:question_id>', methods=['PUT', 'DELETE'])
def edit_delete_question(question_id):
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'message': 'Question not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        question_statement = data.get('question_statement')
        option_1 = data.get('option_1')
        option_2 = data.get('option_2')
        correct_option = data.get('correct_option')
        if not all([quiz_id, question_statement, option_1, option_2, correct_option]):
            return jsonify({'message': 'All fields are required'}), 400
        if not Quiz.query.get(quiz_id):
            return jsonify({'message': 'Quiz not found'}), 404
        if question_statement != question.question_statement and Question.query.filter_by(question_statement=question_statement).first():
            return jsonify({'message': 'Question statement already exists'}), 400
        if correct_option not in [option_1, option_2]:
            return jsonify({'message': 'Correct option must match one of the provided options'}), 400
        question.quiz_id = quiz_id
        question.question_statement = question_statement
        question.option_1 = option_1
        question.option_2 = option_2
        question.correct_option = correct_option
        db.session.commit()
        return jsonify({'message': 'Question updated successfully'}), 200
    elif request.method == 'DELETE':
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted successfully'}), 200

@app.route('/api/admin/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()
    users = User.query.filter(
        (db.func.lower(User.user_id).like(f'%{query}%')) |
        (db.func.lower(User.email_id).like(f'%{query}%')) |
        (db.func.lower(User.name).like(f'%{query}%'))
    ).all()
    subjects = Subject.query.filter(
        (db.func.lower(Subject.name).like(f'%{query}%')) |
        (db.func.lower(Subject.description).like(f'%{query}%'))
    ).all()
    quizzes = Quiz.query.filter(
        (db.func.lower(Quiz.name).like(f'%{query}%'))
    ).all()
    return jsonify({
        'users': [{'user_id': user.user_id, 'email_id': user.email_id, 'name': user.name} for user in users],
        'subjects': [{'subject_id': subject.subject_id, 'name': subject.name, 'description': subject.description} for subject in subjects],
        'quizzes': [{'quiz_id': quiz.quiz_id, 'name': quiz.name, 'chapter_id': quiz.chapter_id} for quiz in quizzes]
    }), 200

@app.route('/api/admin/summary', methods=['GET'])
def summary():
    user_count = User.query.count()
    subject_count = Subject.query.count()
    quiz_count = Quiz.query.count()
    return jsonify({
        'user_count': user_count,
        'subject_count': subject_count,
        'quiz_count': quiz_count
    }), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    user_id = data.get('user_id')
    email_id = data.get('email_id')
    name = data.get('name')
    qualification = data.get('qualification')
    dob = data.get('dob')
    password = data.get('password')

    print(f"Registering user: {user_id}, {email_id}")

    salt = os.urandom(16)
    iterations = 260000
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations).hex()
    salt_hex = salt.hex()
    hashed_password = f"{salt_hex}:{hashed_password}"

    existing_user = User.query.filter(
        (db.func.lower(User.user_id) == db.func.lower(user_id)) |
        (db.func.lower(User.email_id) == db.func.lower(email_id))
    ).first()

    if existing_user:
        print(f"User already exists: {user_id} or {email_id}")
        return jsonify({'message': 'You have already registered, go to the login page'}), 400

    new_user = User(
        user_id=user_id,
        email_id=email_id,
        name=name,
        qualification=qualification,
        dob=dob,
        password=hashed_password,
        role='user'
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        print(f"User {user_id} successfully added to database")
        if redis_client:
            try:
                user_data = {
                    'user_id': user_id,
                    'email_id': email_id,
                    'name': name,
                    'qualification': qualification,
                    'dob': dob,
                    'role': 'user'
                }
                redis_client.setex(f"user:{user_id}", 3600, json.dumps(user_data))
                print(f"User {user_id} cached in Redis")
            except redis.ConnectionError as e:
                print(f"Redis error during registration caching: {e}")
        session['user_id'] = user_id
        try:
            log_user_registration.delay(user_id, email_id)
            print(f"Celery task triggered for {user_id}")
        except Exception as e:
            print(f"Celery task failed: {e}")
        return jsonify({'message': 'Registration successful!'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {str(e)}")
        return jsonify({'message': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    print(f"Login attempt for user: {user_id}")

    user = User.query.filter(db.func.lower(User.user_id) == db.func.lower(user_id)).first()

    if not user:
        print(f"User not found: {user_id}")
        return jsonify({'message': 'Invalid username or password'}), 401

    stored_password = user.password
    try:
        salt_hex, stored_hash = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        print("Invalid password format in database")
        return jsonify({'message': 'Invalid password format in database'}), 500

    iterations = 260000
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations).hex()

    if hashed_password == stored_hash:
        session['user_id'] = user.user_id
        print(f"Login successful for user: {user_id}")
        return jsonify({'message': 'Login successful!'}), 200
    else:
        print(f"Invalid password for user: {user_id}")
        return jsonify({'message': 'Invalid username or password'}), 401

@app.route('/api/user/subjects')
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{'subject_id': s.subject_id, 'name': s.name, 'description': s.description} for s in subjects])

@app.route('/api/user/chapters')
def get_chapters():
    chapters = Chapter.query.all()
    return jsonify([{'chapter_id': c.chapter_id, 'name': c.name, 'description': c.description, 'subject_id': c.subject_id} for c in chapters])

@app.route('/api/user/quizzes')
def get_quizzes():
    quizzes = Quiz.query.all()
    return jsonify([{'quiz_id': q.quiz_id, 'name': q.name, 'chapter_id': q.chapter_id} for q in quizzes])

@app.route('/api/user/questions')
def get_questions():
    quiz_id = request.args.get('quiz_id')
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify([{'question_id': q.question_id, 'question_statement': q.question_statement, 'option_1': q.option_1, 'option_2': q.option_2, 'correct_option': q.correct_option, 'quiz_id': q.quiz_id} for q in questions])

@app.route('/api/user/scores', methods=['POST'])
def save_score():
    data = request.get_json()
    if not data or 'quiz_id' not in data or 'user_id' not in data or 'total_score' not in data or 'time_stamp_of_attempt' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        quiz = Quiz.query.get(data['quiz_id'])
        if not quiz:
            return jsonify({'message': 'Invalid quiz_id'}), 400

        try:
            time_stamp = datetime.strptime(data['time_stamp_of_attempt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            return jsonify({'message': 'Invalid time_stamp_of_attempt format'}), 400

        score = Score(
            quiz_id=data['quiz_id'],
            user_id=data['user_id'],
            total_score=data['total_score'],
            time_stamp_of_attempt=time_stamp
        )
        db.session.add(score)
        db.session.commit()
        return jsonify({'message': 'Score saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Failed to save score: {str(e)}'}), 500

@app.route('/api/user/scores')
def get_scores():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400
    try:
        scores = Score.query.filter_by(user_id=user_id).all()
        result = []
        for score in scores:
            quiz = Quiz.query.get(score.quiz_id)
            if quiz:
                chapter = Chapter.query.get(quiz.chapter_id)
                if chapter:
                    subject = Subject.query.get(chapter.subject_id)
                    subject_name = subject.name if subject else 'Unknown'
                    chapter_name = chapter.name if chapter else 'Unknown'
                else:
                    subject_name = 'Unknown'
                    chapter_name = 'Unknown'
            else:
                subject_name = 'Unknown'
                chapter_name = 'Unknown'
            total_questions = Question.query.filter_by(quiz_id=score.quiz_id).count() or 1
            result.append({
                'score_id': score.score_id,
                'quiz_id': score.quiz_id,
                'user_id': score.user_id,
                'total_score': score.total_score,
                'time_stamp_of_attempt': score.time_stamp_of_attempt.isoformat() + 'Z',
                'subject_name': subject_name,
                'chapter_name': chapter_name,
                'total_questions': total_questions,
                'quiz_name': quiz.name if quiz else 'Unknown'
            })
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching scores: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Failed to fetch scores: {str(e)}'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            admin_user = User.query.filter_by(user_id='admin0901').first()
            if not admin_user:
                salt = os.urandom(16)
                iterations = 260000
                hashed_password = hashlib.pbkdf2_hmac('sha256', '0901'.encode(), salt, iterations).hex()
                salt_hex = salt.hex()
                admin_password = f"{salt_hex}:{hashed_password}"
                admin = User(
                    user_id='admin0901',
                    email_id='admin@quizmaster.com',
                    name='Admin',
                    qualification='N/A',
                    dob='2000-01-01',
                    password=admin_password,
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("Admin user created: admin0901")
            else:
                print("Admin user already exists")
            print("Database tables created")
        except Exception as e:
            print(f"Database initialization failed: {str(e)}")
            raise
    app.run(debug=True, port=5000)