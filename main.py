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