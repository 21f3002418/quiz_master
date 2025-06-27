## Author 
Harshvi Saini 
21f3002418@ds.study.iitm.ac.in 
I am a student of diploma level. I completed my bachelors of arts from B.K Birla Institute of 
Higher Education, Pilani along with BS in Data Science and Applications from IITM BS. I 
am working for a start up called “Department of Visual Media” now.  

## Description 
This project involves building Quiz Master - V2, an exam preparation platform starting with 
registration and login pages, featuring admin and user dashboards for managing quizzes 
and tracking performance across different subjects, chapters and quizzes. AI was used 
for debugging and feature refinement 


## Technologies Used 
Following are the major technologies used in the project 
● Flask: Flask, render_template, request, flash, redirect, url_for, etc 
● Flask-SQLAlchemy: SQLAlchemy 
● SQLite: sqlite3 
● Flask-CORS: CORS 
● Redis: redis.Redis 
● Celery:  celery_app 
● VueJS:  Vue, Vue CLI (for compiling .vue files) 
Flask drives the web framework and routing, Flask-SQLAlchemy and SQLite manage database 
operations, Flask-CORS enables cross-origin requests, Redis provides caching for user data, 
Celery handles asynchronous tasks like registration logging, and VueJS with Vue CLI creates 
dynamic, component-based UIs for user_dashboard.vue and admin_dashboard.vue. 


## DB Schema Design 
● Users 
○ user_id: primary key, string, unique, not null 
○ email_id: string, unique, not null 
○ name: string, not null 
○ qualification: string, not null 
○ dob: string, not null 
○ password: string, not null 
○ role: string, default 'user' 
● Subjects 
○ subject_id: primary key, integer, auto increment, unique, not null 
○ name: string, not null, unique 
○ description: string, not null, unique 
● Chapters 
  ○ chapter_id: primary key, integer, auto increment, unique, not null 
  ○ name: string, not null, unique 
  ○ description: string, not null, unique 
  ○ subject_id: integer, foreign key(Subjects), not null 
● Quizzes 
  ○ quiz_id: primary key, integer, auto increment, unique, not null 
  ○ name: string, not null 
  ○ chapter_id: integer, foreign key(Chapters), not null 
● Questions 
  ○ question_id: primary key, integer, auto increment, unique, not null 
  ○ quiz_id: integer, foreign key(Quizzes), not null 
  ○ question_statement: string, not null, unique 
  ○ option_1: string, not null 
  ○ option_2: string, not null 
  ○ correct_option: string, not null 
● Scores 
  ○ score_id: primary key, integer, auto increment, unique, not null 
  ○ quiz_id: integer, foreign key(Quizzes), not null 
  ○ user_id: string, foreign key(Users), not null 
  ○ total_score: integer, not null 
  ○ time_stamp_of_attempt: datetime, not null 
The hierarchical design with Users, Subjects, Chapters, Quizzes, Questions, and Scores supports 
a structured quiz system, ensuring data integrity with foreign keys and unique constraints for 
efficient management and tracking. 


## API Design 

All the APIs have been created using Flask, following are the major functionalities for which 
APIs have been created. 
 
● For user registration and login authentication 
● For admin to manage subjects, chapters, quizzes, and questions with CRUD operations 
● For retrieving user performance data and quiz content  
● For admin search and summary statistics  


## Architecture and Features 
The project and its code is organised in the following way: 
● QuizMaster-V2: This is the main repository. 
  ○ pycache 
   ○ static/js: Contains VueJS components (login.vue, register.vue, 
                                user_dashboard.vue, admin_dashboard.vue) for dynamic UIs                                                              
                            ○ templates: Holds HTML templates (login.html, register.html,                      
                                 user_dashboard.html, admin_dashboard.html) for rendering 
                            ○ application: Includes pycache, celery_config.py, config.py, models.py, 
                                resources.py for backend configuration and models 
                             ○ main.py: The main Flask app running all routes, APIs, and templates 
                             ○ quiz.db: The SQLite database storing user, subject, quiz, and score data 
                             ○ quiz.sqbpro: Database configuration file 
             The application, on running, will first show registration and login pages. 
                    ● User Registration/Login 
 
➢ Users can register with unique user_id and email_id, log in to access their dashboard with 
user_dashboard.vue for performance charts via /api/user/scores, and attempt quizzes, with 
scores saved and cache using Redis. 
● Admin Login 
 
➢ Only admins (e.g., user_id 'admin0901') can log in to manage subjects, chapters, quizzes, and 
questions with CRUD APIs using admin_dashboard.vue, search users/subjects/quizzes, and view 
summary stats, supported by Celery for logging registration events. 
The platform ensures role-based access, real-time quiz updates, and performance tracking, 
enhanced by VueJS components compiled with Vue CLI and secure password hashing. 
Version Control Configuration: 
The project uses a .gitignore file to exclude unnecessary files from version control, 
 
 
