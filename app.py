from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, StringField, PasswordField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os, csv
from datetime import datetime
import time
from flask import get_flashed_messages
import csv
from flask import Response
from flask_wtf.csrf import CSRFProtect
from urllib.parse import unquote

# --- Flask Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# --- Ensure upload folder exists ---
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}

# --- Neon PostgreSQL (persistent) ---
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://neondb_owner:npg_97DuTpZbOLJY@ep-cold-resonance-a1ldqo6i-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
)

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"connect_timeout": 15},
    "pool_pre_ping": True,        # 🩺 checks if connection is alive before using it
    "pool_recycle": 300,          # 🔁 reconnects every 5 minutes
    "pool_size": 5,               # 💧 keep 5 connections ready
    "max_overflow": 10            # 🚀 allow temporary burst of 10
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Upload settings ---
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin/Instructor/Student

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    section = db.Column(db.String(50))
    subject = db.Column(db.String(100), primary_key=True)

    # Attendance
    midterm_attendance1 = db.Column(db.String(10), default='0')
    midterm_attendance2 = db.Column(db.String(10), default='0')
    midterm_attendance3 = db.Column(db.String(10), default='0')
    midterm_attendance4 = db.Column(db.String(10), default='0')
    final_attendance1 = db.Column(db.String(10), default='0')
    final_attendance2 = db.Column(db.String(10), default='0')
    final_attendance3 = db.Column(db.String(10), default='0')
    final_attendance4 = db.Column(db.String(10), default='0')

    # Midterm Quizzes
    midterm_quiz1 = db.Column(db.String(10), default='0')
    midterm_quiz2 = db.Column(db.String(10), default='0')
    midterm_quiz3 = db.Column(db.String(10), default='0')
    midterm_quiz4 = db.Column(db.String(10), default='0')
    midterm_e_quiz1 = db.Column(db.String(10), default='0')
    midterm_e_quiz2 = db.Column(db.String(10), default='0')
    midterm_e_quiz3 = db.Column(db.String(10), default='0')
    midterm_e_quiz4 = db.Column(db.String(10), default='0')
    midterm_l_quiz1 = db.Column(db.String(10), default='0')
    midterm_l_quiz2 = db.Column(db.String(10), default='0')
    midterm_l_quiz3 = db.Column(db.String(10), default='0')
    midterm_l_quiz4 = db.Column(db.String(10), default='0')

    # Final Quizzes
    final_quiz1 = db.Column(db.String(10), default='0')
    final_quiz2 = db.Column(db.String(10), default='0')
    final_quiz3 = db.Column(db.String(10), default='0')
    final_quiz4 = db.Column(db.String(10), default='0')
    final_e_quiz1 = db.Column(db.String(10), default='0')
    final_e_quiz2 = db.Column(db.String(10), default='0')
    final_e_quiz3 = db.Column(db.String(10), default='0')
    final_e_quiz4 = db.Column(db.String(10), default='0')
    final_l_quiz1 = db.Column(db.String(10), default='0')
    final_l_quiz2 = db.Column(db.String(10), default='0')
    final_l_quiz3 = db.Column(db.String(10), default='0')
    final_l_quiz4 = db.Column(db.String(10), default='0')

    # PIT
    midterm_pit1 = db.Column(db.String(10), default='0')
    midterm_pit2 = db.Column(db.String(10), default='0')
    midterm_pit3 = db.Column(db.String(10), default='0')
    midterm_pit4 = db.Column(db.String(10), default='0')
    final_pit1 = db.Column(db.String(10), default='0')
    final_pit2 = db.Column(db.String(10), default='0')
    final_pit3 = db.Column(db.String(10), default='0')
    final_pit4 = db.Column(db.String(10), default='0')

    # Exercises
    midterm_exercise1 = db.Column(db.String(10), default='0')
    midterm_exercise2 = db.Column(db.String(10), default='0')
    midterm_exercise3 = db.Column(db.String(10), default='0')
    midterm_exercise4 = db.Column(db.String(10), default='0')
    final_exercise1 = db.Column(db.String(10), default='0')
    final_exercise2 = db.Column(db.String(10), default='0')
    final_exercise3 = db.Column(db.String(10), default='0')
    final_exercise4 = db.Column(db.String(10), default='0')

    # Laboratory
    midterm_laboratory1 = db.Column(db.String(10), default='0')
    midterm_laboratory2 = db.Column(db.String(10), default='0')
    midterm_laboratory3 = db.Column(db.String(10), default='0')
    midterm_laboratory4 = db.Column(db.String(10), default='0')
    final_laboratory1 = db.Column(db.String(10), default='0')
    final_laboratory2 = db.Column(db.String(10), default='0')
    final_laboratory3 = db.Column(db.String(10), default='0')
    final_laboratory4 = db.Column(db.String(10), default='0')

    # Report
    midterm_report1 = db.Column(db.String(10), default='0')
    final_report1 = db.Column(db.String(10), default='0')

    # Exams
    midterm_exam = db.Column(db.String(10), default='0')
    final_exam = db.Column(db.String(10), default='0')
    midterm_laboratory_exam = db.Column(db.String(10), default='0')
    final_laboratory_exam = db.Column(db.String(10), default='0')

    # Grades and remarks (separated)
    midterm_grade = db.Column(db.String(10), default='0')
    final_grade = db.Column(db.String(10), default='0')
    midterm_remarks = db.Column(db.String(50))
    final_remarks = db.Column(db.String(50))

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject', name='uix_student_subject'),
    )

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- Utility Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_log(user, action):
    log_entry = Log(user=user, action=action)
    db.session.add(log_entry)
    db.session.commit()

def get_dashboard_url():
    role = session.get('role')
    if role == 'Admin':
        return url_for('dashboard_admin')
    elif role == 'Instructor':
        return url_for('dashboard_instructor')
    return url_for('login')

def patch_update(obj, data_dict):
    for key, value in data_dict.items():
        if hasattr(obj, key):

            if value is None:
                continue

            val = str(value).strip()

            # CLEAR keyword → set to blank (NULL in DB)
            if val.upper() == "CLEAR":
                setattr(obj, key, None)

            # normal update (includes 0)
            elif val != "":
                setattr(obj, key, val)

def clean_input(value):
    return value if value not in [None, ""] else None

def get_student(student_id):
    # fetch student from DB
    pass

def get_quiz_records(student_id):
    pass

def get_pit_records(student_id):
    pass

def get_laboratory_records(student_id):
    pass

def get_exercise_records(student_id):
    pass

def get_exam_records(student_id):
    pass

# --- Forms ---
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('Instructor','Instructor'), ('Student','Student')], validators=[DataRequired()])
    submit = SubmitField('Create User')

class StudentForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    section = StringField('Section', validators=[Optional()])
    subject = StringField('Subject', validators=[Optional()])

    # Attendance
    midterm_attendance1 = StringField('Midterm Attendance 1', validators=[Optional()])
    midterm_attendance2 = StringField('Midterm Attendance 2', validators=[Optional()])
    midterm_attendance3 = StringField('Midterm Attendance 3', validators=[Optional()])
    midterm_attendance4 = StringField('Midterm Attendance 4', validators=[Optional()])
    final_attendance1 = StringField('Final Attendance 1', validators=[Optional()])
    final_attendance2 = StringField('Final Attendance 2', validators=[Optional()])
    final_attendance3 = StringField('Final Attendance 3', validators=[Optional()])
    final_attendance4 = StringField('Final Attendance 4', validators=[Optional()])
    
    # Midterm Quizzes
    midterm_quiz1 = StringField('Midterm Quiz 1', validators=[Optional()])
    midterm_quiz2 = StringField('Midterm Quiz 2', validators=[Optional()])
    midterm_quiz3 = StringField('Midterm Quiz 3', validators=[Optional()])
    midterm_quiz4 = StringField('Midterm Quiz 4', validators=[Optional()])
    midterm_e_quiz1 = StringField('Midterm Exercise Quiz 1', validators=[Optional()])
    midterm_e_quiz2 = StringField('Midterm Exercise Quiz 2', validators=[Optional()])
    midterm_e_quiz3 = StringField('Midterm Exercise Quiz 3', validators=[Optional()])
    midterm_e_quiz4 = StringField('Midterm Exercise Quiz 4', validators=[Optional()])
    midterm_l_quiz1 = StringField('Midterm Laboratory Quiz 1', validators=[Optional()])
    midterm_l_quiz2 = StringField('Midterm Laboratory Quiz 2', validators=[Optional()])
    midterm_l_quiz3 = StringField('Midterm Laboratory Quiz 3', validators=[Optional()])
    midterm_l_quiz4 = StringField('Midterm Laboratory Quiz 4', validators=[Optional()])

    # Final Quizzes
    final_quiz1 = StringField('Final Quiz 1', validators=[Optional()])
    final_quiz2 = StringField('Final Quiz 2', validators=[Optional()])
    final_quiz3 = StringField('Final Quiz 3', validators=[Optional()])
    final_quiz4 = StringField('Final Quiz 4', validators=[Optional()])
    final_e_quiz1 = StringField('Final Exercise Quiz 1', validators=[Optional()])
    final_e_quiz2 = StringField('Final Exercise Quiz 2', validators=[Optional()])
    final_e_quiz3 = StringField('Final Exercise Quiz 3', validators=[Optional()])
    final_e_quiz4 = StringField('Final Exercise Quiz 4', validators=[Optional()])
    final_l_quiz1 = StringField('Final Laboratory Quiz 1', validators=[Optional()])
    final_l_quiz2 = StringField('Final Laboratory Quiz 2', validators=[Optional()])
    final_l_quiz3 = StringField('Final Laboratory Quiz 3', validators=[Optional()])
    final_l_quiz4 = StringField('Final Laboratory Quiz 4', validators=[Optional()])

    # PIT
    midterm_pit1 = StringField('PIT 1', validators=[Optional()])
    midterm_pit2 = StringField('PIT 2', validators=[Optional()])
    midterm_pit3 = StringField('PIT 3', validators=[Optional()])
    midterm_pit4 = StringField('PIT 4', validators=[Optional()])
    final_pit1 = StringField('PIT 1', validators=[Optional()])
    final_pit2 = StringField('PIT 2', validators=[Optional()])
    final_pit3 = StringField('PIT 3', validators=[Optional()])
    final_pit4 = StringField('PIT 4', validators=[Optional()])

    # Exercises
    midterm_exercise1 = StringField('Exercise 1', validators=[Optional()])
    midterm_exercise2 = StringField('Exercise 2', validators=[Optional()])
    midterm_exercise3 = StringField('Exercise 3', validators=[Optional()])
    midterm_exercise4 = StringField('Exercise 4', validators=[Optional()])
    final_exercise1 = StringField('Exercise 1', validators=[Optional()])
    final_exercise2 = StringField('Exercise 2', validators=[Optional()])
    final_exercise3 = StringField('Exercise 3', validators=[Optional()])
    final_exercise4 = StringField('Exercise 4', validators=[Optional()])

    # Laboratories
    midterm_laboratory1 = StringField('Laboratory 1', validators=[Optional()])
    midterm_laboratory2 = StringField('Laboratory 2', validators=[Optional()])
    midterm_laboratory3 = StringField('Laboratory 3', validators=[Optional()])
    midterm_laboratory4 = StringField('Laboratory 4', validators=[Optional()])
    final_laboratory1 = StringField('Laboratory 1', validators=[Optional()])
    final_laboratory2 = StringField('Laboratory 2', validators=[Optional()])
    final_laboratory3 = StringField('Laboratory 3', validators=[Optional()])
    final_laboratory4 = StringField('Laboratory 4', validators=[Optional()])

    # Reports
    midterm_report1 = StringField('Midterm Report 1', validators=[Optional()])
    final_report1 = StringField('Final Report 1', validators=[Optional()])

    # Exams and grades
    midterm_exam = StringField('Midterm Exam', validators=[Optional()])
    final_exam = StringField('Final Exam', validators=[Optional()])
    midterm_laboratory_exam = StringField('Midterm Laboratory Exam', validators=[Optional()])
    final_laboratory_exam = StringField('Final Laboratory Exam', validators=[Optional()])
    midterm_grade = StringField('Midterm Grade', validators=[Optional()])
    final_grade = StringField('Final Grade', validators=[Optional()])

    # Midterm & Finals remarks
    midterm_remarks = StringField('Midterm Remarks', validators=[Optional()])
    final_remarks = StringField('Final Remarks', validators=[Optional()])

    submit = SubmitField('Save Changes')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

class UploadCSVForm(FlaskForm):
    file = FileField('CSV File', validators=[DataRequired()])
    submit = SubmitField('Upload')

# --- Login Required Decorator ---
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in first.", "danger")
                return redirect(url_for('login'))
            if role and session.get('role') not in (role if isinstance(role, list) else [role]):
                flash("Access denied.", "danger")
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Routes ---

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # ✅ Store integer primary key in session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Logged in successfully as {user.username}', 'success')
            add_log(user.username, 'Logged in')
            time.sleep(1)  # Let DB/session settle

            # Redirect based on role
            if user.role == 'Admin':
                return redirect(url_for('dashboard_admin'))
            elif user.role == 'Instructor':
                return redirect(url_for('dashboard_instructor'))
            else:  # Student
                return redirect(url_for('dashboard_student'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


# Logout
@app.route('/logout')
def logout():
    user = session.get('username')
    session.clear()
    if user:
        add_log(user, 'Logged out')
        time.sleep(1)  # 🕒 Prevent SQLite lock or empty data
    return redirect(url_for('login'))

# Change Password
@app.route('/change_password', methods=['GET', 'POST'])
@login_required()
def change_password():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Validate current password
        if not check_password_hash(user.password, current_password):
            flash("❌ Current password is incorrect.", "danger")
            return redirect(url_for('change_password'))

        # Ensure new password matches confirmation
        if new_password != confirm_password:
            flash("⚠️ New passwords do not match.", "warning")
            return redirect(url_for('change_password'))

        # Ensure new password isn't same as current
        if check_password_hash(user.password, new_password):
            flash("⚠️ New password must be different from the current one.", "warning")
            return redirect(url_for('change_password'))

        # Update password securely
        user.password = generate_password_hash(new_password)
        db.session.commit()

        # Log the event
        add_log(
            user.username,
            f"Changed their password (Role: {user.role})"
        )
        time.sleep(1)

        # Force logout for security
        session.clear()
        flash("✅ Nautro na imuhang password! Pwede na ta manlupad.", "success")
        return redirect(url_for('login'))

    return render_template('change_password.html')

# --- Dashboards ---
# ---- Admin Dashboard ----
@app.route('/dashboard/admin')
@login_required(role='Admin')
def dashboard_admin():
    # Fetch all students
    students = Student.query.all()
    
    # Fetch all instructors
    instructors = User.query.filter_by(role='Instructor').all()
    
    # Fetch all logs (newest first)
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    
    # Render template
    return render_template(
        'dashboard_admin.html',
        students=students,
        instructors=instructors,
        logs=logs
    )

# ---- Instructor Dashboard ----
@app.route('/dashboard/instructor')
@login_required(role='Instructor')
def dashboard_instructor():
    # Fetch all students (or filter by instructor if needed)
    students = Student.query.all()  

    return render_template(
        'dashboard_instructor.html',
        students=students
    )

# ---- Student Dashboard ----
@app.route('/dashboard/student')
@login_required(role=['Student','Admin','Instructor'])
def dashboard_student():

    role = session.get('role')

    # STUDENT
    if role == 'Student':
        student_id = session.get('username')

    # ADMIN / INSTRUCTOR
    else:
        student_id = request.args.get('student_id')

        if not student_id:
            students = []
            return render_template("dashboard_student.html", students=students, student_name=None)

    students = Student.query.filter_by(student_id=student_id).all()

    # 🔥 FIX: ALWAYS define name safely
    student_name = students[0].name if students and students[0].name else "Student"

    return render_template(
        "dashboard_student.html",
        students=students,
        student_name=student_name,
        role=role
    )

@app.route('/admin/view_student/<student_id>')
def admin_view_student(student_id):
    return redirect(url_for('dashboard_student', student_id=student_id))

# View Logs (Admin)
@app.route('/view_logs')
@login_required(role='Admin')
def view_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    logs_with_student_name = []
    for log in logs:
        student = Student.query.filter_by(student_id=log.user).first()
        student_name = student.name if student else None
        logs_with_student_name.append({
            'id': log.id,
            'student_name': student_name,
            'user': log.user,
            'action': log.action,
            'timestamp': log.timestamp
        })
    return render_template('logs.html', logs=logs_with_student_name)

# Bulk Delete Logs (Admin)
@app.route('/logs/bulk_delete', methods=['POST'])
@login_required(role='Admin')
def bulk_delete_logs():
    log_ids = request.form.getlist('log_ids')
    if log_ids:
        deleted_logs = []
        for lid in log_ids:
            log = Log.query.get(int(lid))
            if log:
                deleted_logs.append(f"{log.user} - {log.action}")
                db.session.delete(log)
        db.session.commit()
        add_log(session['username'], f'Bulk deleted logs: {", ".join(deleted_logs)}')
        flash(f'{len(log_ids)} log(s) deleted successfully!', 'success')
    else:
        flash('No logs selected for deletion.', 'warning')
    return redirect(url_for('view_logs'))

# Create User (Admin)
@app.route('/dashboard/admin/create_user', methods=['GET','POST'])
@login_required(role='Admin')
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists!', 'danger')
        else:
            hashed_password = generate_password_hash(form.password.data)
            db.session.add(User(username=form.username.data, password=hashed_password, role=form.role.data))
            db.session.commit()
            add_log(session['username'], f'Created {form.role.data} account: {form.username.data}')
            flash(f'{form.role.data} account created successfully!', 'success')
            return redirect(url_for('dashboard_admin'))
    return render_template('create_user.html', form=form)

# View Instructors (Admin)
@app.route('/dashboard/admin/instructors')
@login_required(role='Admin')
def view_instructors():
    instructors = User.query.filter_by(role='Instructor').all()
    return render_template('instructors.html', instructors=instructors)

# Add/Edit/Delete Instructors
@app.route('/dashboard/admin/instructors/add', methods=['GET','POST'])
@login_required(role='Admin')
def add_instructor():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('add_instructor'))
        hashed_password = generate_password_hash(password)
        db.session.add(User(username=username, password=hashed_password, role='Instructor'))
        db.session.commit()
        add_log(session['username'], f'Added Instructor: {username}')
        flash('Instructor added successfully!', 'success')
        return redirect(url_for('view_instructors'))
    return render_template('add_instructor.html')

@app.route('/dashboard/admin/instructors/edit/<int:id>', methods=['GET','POST'])
@login_required(role='Admin')
def edit_instructor(id):
    instructor = User.query.get_or_404(id)
    if request.method == 'POST':
        old_username = instructor.username
        instructor.username = request.form['username']
        if request.form['password']:
            instructor.password = generate_password_hash(request.form['password'])
        db.session.commit()
        add_log(session['username'], f'Edited Instructor: {old_username} -> {instructor.username}')
        flash('Instructor updated successfully!', 'success')
        return redirect(url_for('view_instructors'))
    return render_template('edit_instructor.html', instructor=instructor)

@app.route('/dashboard/admin/instructors/delete/<int:id>', methods=['POST'])
@login_required(role='Admin')
def delete_instructor(id):
    instructor = User.query.get_or_404(id)
    db.session.delete(instructor)
    db.session.commit()
    add_log(session['username'], f'Deleted Instructor: {instructor.username}')
    flash('Instructor deleted successfully!', 'success')
    return redirect(url_for('view_instructors'))

@app.route('/dashboard/admin/instructors/bulk_delete', methods=['POST'])
@login_required(role='Admin')
def bulk_delete_instructors():
    instructor_ids = request.form.getlist('instructor_ids')
    if instructor_ids:
        deleted_usernames = []
        for iid in instructor_ids:
            instructor = User.query.get(int(iid))
            if instructor and instructor.role == 'Instructor':
                deleted_usernames.append(instructor.username)
                db.session.delete(instructor)
        db.session.commit()
        add_log(session['username'], f'Bulk deleted Instructors: {", ".join(deleted_usernames)}')
        flash(f'{len(instructor_ids)} instructor(s) deleted successfully!', 'success')
    else:
        flash('No instructors selected for deletion.', 'warning')
    return redirect(url_for('view_instructors'))

# ---- Student Grades ----
@app.route('/student/grades/<student_id>')
@login_required(role=['Admin', 'Instructor', 'Student'])
def student_grades(student_id):
    """
    Fetch all records for a given student I number (student_id).
    Display grades as stored in the database (no computation).
    """
    # Ensure student_id is a string and stripped of extra spaces
    student_id = str(student_id).strip()

    # Fetch all student records that match this student_id (I number)
    students = Student.query.filter_by(student_id=student_id).all()

    if not students:
        flash(f"No records found for student ID {student_id}", "warning")
        # Redirect based on user role
        role = session.get('role')
        if role == 'Student':
            return redirect(url_for('dashboard_student'))
        elif role == 'Instructor':
            return redirect(url_for('dashboard_instructor'))
        else:
            return redirect(url_for('dashboard_admin'))

    # Render template with all subjects for this student
    # No computation; display stored quiz, exam, and overall grades
    return render_template(
        'student_grades.html',
        students=students,
        student_name=students[0].name  # Use first record's name
    )

# ---- Subject Performance ----
@app.route('/student/performance/<student_id>/<subject>')
@login_required(role=['Student','Admin','Instructor'])
def subject_performance(student_id, subject):

    subject = unquote(subject)  # decode URL

    student_records = Student.query.filter_by(
        student_id=student_id,
        subject=subject
    ).first_or_404()

    record = student_records

    performance = {
        "subject": record.subject,

        # MIDTERM QUIZZES
        "midterm_quiz1": record.midterm_quiz1,
        "midterm_quiz2": record.midterm_quiz2,
        "midterm_quiz3": record.midterm_quiz3,
        "midterm_quiz4": record.midterm_quiz4,

        # EXERCISE QUIZZES
        "midterm_e_quiz1": record.midterm_e_quiz1,
        "midterm_e_quiz2": record.midterm_e_quiz2,
        "midterm_e_quiz3": record.midterm_e_quiz3,
        "midterm_e_quiz4": record.midterm_e_quiz4,

        # LAB QUIZZES
        "midterm_l_quiz1": record.midterm_l_quiz1,
        "midterm_l_quiz2": record.midterm_l_quiz2,
        "midterm_l_quiz3": record.midterm_l_quiz3,
        "midterm_l_quiz4": record.midterm_l_quiz4,

        # PIT
        "pit": [
            record.midterm_pit1, record.midterm_pit2,
            record.midterm_pit3, record.midterm_pit4,
            record.final_pit1, record.final_pit2,
            record.final_pit3, record.final_pit4
        ],

        # LABORATORY
        "laboratory": [
            record.midterm_laboratory1, record.midterm_laboratory2,
            record.midterm_laboratory3, record.midterm_laboratory4,
            record.final_laboratory1, record.final_laboratory2,
            record.final_laboratory3, record.final_laboratory4
        ],

        # EXERCISES
        "exercises": [
            record.midterm_exercise1, record.midterm_exercise2,
            record.midterm_exercise3, record.midterm_exercise4,
            record.final_exercise1, record.final_exercise2,
            record.final_exercise3, record.final_exercise4
        ],

        # EXAMS
        "exams": {
            "midterm": record.midterm_exam,
            "final": record.final_exam
        },

        # GRADES
        "grades": {
            "midterm": record.midterm_grade,
            "final": record.final_grade
        },

        # REMARKS
        "remarks": {
            "midterm": record.midterm_remarks,
            "final": record.final_remarks
        }
    }

    return render_template(
        "subject_performance.html",
        student=record,
        performance=performance
    )

@app.route('/attendance/<student_id>/<subject>', methods=['GET', 'POST'])
@login_required(role=['Admin','Instructor','Student'])
def attendance_page(student_id, subject):


    subject = unquote(subject)

    student = Student.query.filter_by(
        student_id=student_id,
        subject=subject
    ).first_or_404()

    # 🔥 SAVE DATA (POST)
    if request.method == 'POST':

        # 🚫 BLOCK STUDENTS FROM EDITING
        if session.get('role') not in ['Admin', 'Instructor']:
            flash("Not allowed to edit.", "danger")
            return redirect(request.url)

        # UPDATE ATTENDANCE
        student.midterm_attendance1 = request.form.get('midterm_attendance1')
        student.midterm_attendance2 = request.form.get('midterm_attendance2')
        student.midterm_attendance3 = request.form.get('midterm_attendance3')
        student.midterm_attendance4 = request.form.get('midterm_attendance4')

        student.final_attendance1 = request.form.get('final_attendance1')
        student.final_attendance2 = request.form.get('final_attendance2')
        student.final_attendance3 = request.form.get('final_attendance3')
        student.final_attendance4 = request.form.get('final_attendance4')

        db.session.commit()

        flash("Attendance updated successfully!", "success")

        return redirect(url_for(
            'attendance_page',
            student_id=student.student_id,
            subject=student.subject,
            saved=1
        ))

    # 🔵 GET REQUEST
    saved = request.args.get('saved')

    return render_template(
        "attendance.html",
        student=student,
        saved=saved
    )

@app.route('/quizzes/<student_id>/<subject>', methods=['GET', 'POST'])
@login_required(role=['Student','Admin','Instructor'])
def quizzes_page(student_id, subject):

    subject = unquote(subject)

    student = Student.query.filter_by(
        student_id=student_id,
        subject=subject
    ).first_or_404()

    # 🔥 SAVE CHANGES
    if request.method == 'POST':

        # 🚫 only Admin / Instructor can edit
        if session.get('role') not in ['Admin', 'Instructor']:
            flash("Not allowed to edit quizzes.", "danger")
            return redirect(request.url)

        # MIDTERM QUIZZES
        student.midterm_quiz1 = request.form.get('midterm_quiz1')
        student.midterm_quiz2 = request.form.get('midterm_quiz2')
        student.midterm_quiz3 = request.form.get('midterm_quiz3')
        student.midterm_quiz4 = request.form.get('midterm_quiz4')

        student.midterm_e_quiz1 = request.form.get('midterm_e_quiz1')
        student.midterm_e_quiz2 = request.form.get('midterm_e_quiz2')
        student.midterm_e_quiz3 = request.form.get('midterm_e_quiz3')
        student.midterm_e_quiz4 = request.form.get('midterm_e_quiz4')

        student.midterm_l_quiz1 = request.form.get('midterm_l_quiz1')
        student.midterm_l_quiz2 = request.form.get('midterm_l_quiz2')
        student.midterm_l_quiz3 = request.form.get('midterm_l_quiz3')
        student.midterm_l_quiz4 = request.form.get('midterm_l_quiz4')

        # FINAL QUIZZES
        student.final_quiz1 = request.form.get('final_quiz1')
        student.final_quiz2 = request.form.get('final_quiz2')
        student.final_quiz3 = request.form.get('final_quiz3')
        student.final_quiz4 = request.form.get('final_quiz4')

        student.final_e_quiz1 = request.form.get('final_e_quiz1')
        student.final_e_quiz2 = request.form.get('final_e_quiz2')
        student.final_e_quiz3 = request.form.get('final_e_quiz3')
        student.final_e_quiz4 = request.form.get('final_e_quiz4')

        student.final_l_quiz1 = request.form.get('final_l_quiz1')
        student.final_l_quiz2 = request.form.get('final_l_quiz2')
        student.final_l_quiz3 = request.form.get('final_l_quiz3')
        student.final_l_quiz4 = request.form.get('final_l_quiz4')

        db.session.commit()

        flash("Quizzes updated successfully!", "success")

        return redirect(url_for(
            'quizzes_page',
            student_id=student.student_id,
            subject=student.subject,
            saved=1
        ))

    saved = request.args.get('saved')

    return render_template(
        "quizzes.html",
        student=student,
        saved=saved
    )

@app.route('/pit/<student_id>/<subject>')
def pit_page(student_id, subject):

    subject = unquote(subject)

    student = Student.query.filter_by(
        student_id=student_id,
        subject=subject
    ).first_or_404()

    pit = {
        "midterm": [
            student.midterm_pit1,
            student.midterm_pit2,
            student.midterm_pit3,
            student.midterm_pit4
        ],
        "final": [
            student.final_pit1,
            student.final_pit2,
            student.final_pit3,
            student.final_pit4
        ]
    }

    return render_template(
        "pit.html",
        student=student,
        pit=pit
    )

@app.route('/report/<student_id>/<subject>', methods=['GET', 'POST'])
@login_required(role=['Admin','Instructor','Student'])
def report_page(student_id, subject):

    subject = unquote(subject)

    student = Student.query.filter_by(
        student_id=student_id,
        subject=subject
    ).first_or_404()

    if request.method == 'POST':

        if session.get('role') not in ['Admin', 'Instructor']:
            flash("Not allowed to edit.", "danger")
            return redirect(request.url)

        student.midterm_report1 = request.form.get('midterm_report1')
        student.final_report1 = request.form.get('final_report1')

        db.session.commit()

        return redirect(url_for(
            'report_page',
            student_id=student.student_id,
            subject=student.subject,
            saved=1
        ))

    saved = request.args.get('saved')

    return render_template(
        "report.html",
        student=student,
        saved=saved
    )

@app.route('/laboratory/<student_id>/<subject>')
def laboratory_page(student_id, subject):

    subject = unquote(subject)

    student = Student.query.filter_by(
        student_id=student_id,
        subject=subject
    ).first_or_404()

    labs = {
        "midterm": [
            student.midterm_laboratory1,
            student.midterm_laboratory2,
            student.midterm_laboratory3,
            student.midterm_laboratory4
        ],
        "final": [
            student.final_laboratory1,
            student.final_laboratory2,
            student.final_laboratory3,
            student.final_laboratory4
        ]
    }

    return render_template(
        "laboratory.html",
        student=student,
        labs=labs
    )

@app.route('/exercises/<student_id>/<subject>')
def exercises_page(student_id, subject):

    subject = unquote(subject)

    student = Student.query.filter_by(
        student_id=student_id,
        subject=subject
    ).first_or_404()

    exercises = {
        "midterm": [
            student.midterm_exercise1,
            student.midterm_exercise2,
            student.midterm_exercise3,
            student.midterm_exercise4
        ],
        "final": [
            student.final_exercise1,
            student.final_exercise2,
            student.final_exercise3,
            student.final_exercise4
        ]
    }

    return render_template(
        "exercises.html",
        student=student,
        exercises=exercises
    )

@app.route('/exams/<student_id>/<subject>', methods=['GET', 'POST'])
@login_required(role=['Admin', 'Instructor', 'Student'])
def exams_page(student_id, subject):

    subject = unquote(subject)

    student = Student.query.filter_by(
        student_id=student_id,
        subject=subject
    ).first_or_404()

    if request.method == 'POST':

        if session.get('role') not in ['Admin', 'Instructor']:
            flash("Not allowed to edit exams.", "danger")
            return redirect(request.url)

        student.midterm_exam = request.form.get('midterm_exam')
        student.midterm_laboratory_exam = request.form.get('midterm_laboratory_exam')
        student.midterm_grade = request.form.get('midterm_grade')
        student.midterm_remarks = request.form.get('midterm_remarks')

        student.final_exam = request.form.get('final_exam')
        student.final_laboratory_exam = request.form.get('final_laboratory_exam')
        student.final_grade = request.form.get('final_grade')
        student.final_remarks = request.form.get('final_remarks')

        db.session.commit()

        flash("Exams updated successfully!", "success")

        return redirect(url_for(
            'exams_page',
            student_id=student.student_id,
            subject=student.subject,
            saved=1
        ))

    saved = request.args.get('saved')

    # 🔥 ALWAYS SEND THIS
    exams = {
        "midterm_exam": student.midterm_exam,
        "midterm_laboratory_exam": student.midterm_laboratory_exam,
        "midterm_grade": student.midterm_grade,
        "midterm_remarks": student.midterm_remarks,

        "final_exam": student.final_exam,
        "final_laboratory_exam": student.final_laboratory_exam,
        "final_grade": student.final_grade,
        "final_remarks": student.final_remarks
    }

    return render_template(
        "exams.html",
        student=student,
        exams=exams,
        saved=saved
    )

# View/Add/Edit/Delete Students
@app.route('/dashboard/admin/students')
@app.route('/dashboard/instructor/students')
@login_required(role=['Admin','Instructor'])
def view_students():
    students = Student.query.all()
    return render_template('students.html', students=students)

# --- Student add ---
@app.route('/add_student', methods=['GET', 'POST'])
@login_required(role=['Admin','Instructor'])
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        # No automatic calculation; all fields stored as strings
        student = Student(
            student_id=form.student_id.data,
            name=form.name.data,
            subject=form.subject.data,
            section=form.section.data,
            midterm_quiz1=clean_input(form.midterm_quiz1),
            midterm_quiz2=clean_input(form.midterm_quiz2),
            midterm_quiz3=clean_input(form.midterm_quiz3),
            midterm_quiz4=clean_input(form.midterm_quiz4),
            midterm_e_quiz1=clean_input(form.midterm_e_quiz1),
            midterm_e_quiz2=clean_input(form.midterm_e_quiz2),
            midterm_e_quiz3=clean_input(form.midterm_e_quiz3),
            midterm_e_quiz4=clean_input(form.midterm_e_quiz4),
            midterm_l_quiz1=clean_input(form.midterm_l_quiz1),
            midterm_l_quiz2=clean_input(form.midterm_l_quiz2),
            midterm_l_quiz3=clean_input(form.midterm_l_quiz3),
            midterm_l_quiz4=clean_input(form.midterm_l_quiz4),

            final_quiz1=clean_input(form.final_quiz1),
            final_quiz2=clean_input(form.final_quiz2),
            final_quiz3=clean_input(form.final_quiz3),
            final_quiz4=clean_input(form.final_quiz4),
            final_e_quiz1=clean_input(form.final_e_quiz1),
            final_e_quiz2=clean_input(form.final_e_quiz2),
            final_e_quiz3=clean_input(form.final_e_quiz3),
            final_e_quiz4=clean_input(form.final_e_quiz4),
            final_l_quiz1=clean_input(form.final_l_quiz1),
            final_l_quiz2=clean_input(form.final_l_quiz2),
            final_l_quiz3=clean_input(form.final_l_quiz3),
            final_l_quiz4=clean_input(form.final_l_quiz4),

            # PIT
            midterm_pit1=clean_input(form.midterm_pit1),
            midterm_pit2=clean_input(form.midterm_pit2),
            midterm_pit3=clean_input(form.midterm_pit3),
            midterm_pit4=clean_input(form.midterm_pit4),
            final_pit1=clean_input(form.final_pit1),
            final_pit2=clean_input(form.final_pit2),
            final_pit3=clean_input(form.final_pit3),
            final_pit4=clean_input(form.final_pit4),

            # Exercises
            midterm_exercise1=clean_input(form.midterm_exercise1),
            midterm_exercise2=clean_input(form.midterm_exercise2),
            midterm_exercise3=clean_input(form.midterm_exercise3),
            midterm_exercise4=clean_input(form.midterm_exercise4),
            final_exercise1=clean_input(form.final_exercise1),
            final_exercise2=clean_input(form.final_exercise2),
            final_exercise3=clean_input(form.final_exercise3),
            final_exercise4=clean_input(form.final_exercise4),

            # Laboratory
            midterm_laboratory1=clean_input(form.midterm_laboratory1),
            midterm_laboratory2=clean_input(form.midterm_laboratory2),
            midterm_laboratory3=clean_input(form.midterm_laboratory3),
            midterm_laboratory4=clean_input(form.midterm_laboratory4),
            final_laboratory1=clean_input(form.final_laboratory1),
            final_laboratory2=clean_input(form.final_laboratory2),
            final_laboratory3=clean_input(form.final_laboratory3),
            final_laboratory4=clean_input(form.final_laboratory4),


            midterm_exam=clean_input(form.midterm_exam),
            final_exam=clean_input(form.final_exam),
            midterm_grade=clean_input(form.midterm_grade),
            final_grade=clean_input(form.final_grade),
        )
        db.session.add(student)
        db.session.commit()
        flash(f"Student {student.name} added successfully!", "success")
        return redirect(url_for('view_students'))

    return render_template('add_student.html', form=form)

# --- Student Edit ---
@app.route('/dashboard/admin/students/edit/<student_id>/<subject>', methods=['GET', 'POST'])
@app.route('/dashboard/instructor/students/edit/<student_id>/<subject>', methods=['GET', 'POST'])
@login_required(role=['Admin', 'Instructor'])
def edit_student(student_id, subject):
    student = Student.query.filter_by(student_id=student_id, subject=subject).first_or_404()
    form = StudentForm(obj=student)

    if form.validate_on_submit():
        old_student_id = student.student_id
        new_student_id = form.student_id.data.strip()
        new_subject = form.subject.data.strip() or student.subject

        # Update core info
        student.student_id = new_student_id
        student.name = form.name.data.strip()
        student.section = form.section.data.strip()
        student.subject = new_subject

        # Update quizzes
        student.midterm_quiz1 = clean_input(form.midterm_quiz1.data)
        student.midterm_quiz2 = clean_input(form.midterm_quiz2.data)
        student.midterm_quiz3 = clean_input(form.midterm_quiz3.data)
        student.midterm_quiz4 = clean_input(form.midterm_quiz4.data)
        student.midterm_e_quiz1 = clean_input(form.midterm_e_quiz1.data)
        student.midterm_e_quiz2 = clean_input(form.midterm_e_quiz2.data)
        student.midterm_e_quiz3 = clean_input(form.midterm_e_quiz3.data)
        student.midterm_e_quiz4 = clean_input(form.midterm_e_quiz4.data)
        student.midterm_l_quiz1 = clean_input(form.midterm_l_quiz1.data)
        student.midterm_l_quiz2 = clean_input(form.midterm_l_quiz2.data)
        student.midterm_l_quiz3 = clean_input(form.midterm_l_quiz3.data)
        student.midterm_l_quiz4 = clean_input(form.midterm_l_quiz4.data)

        student.final_quiz1 = clean_input(form.final_quiz1.data)
        student.final_quiz2 = clean_input(form.final_quiz2.data)
        student.final_quiz3 = clean_input(form.final_quiz3.data)
        student.final_quiz4 = clean_input(form.final_quiz4.data)
        student.final_e_quiz1 = clean_input(form.final_e_quiz1.data)
        student.final_e_quiz2 = clean_input(form.final_e_quiz2.data)
        student.final_e_quiz3 = clean_input(form.final_e_quiz3.data)
        student.final_e_quiz4 = clean_input(form.final_e_quiz4.data)
        student.final_l_quiz1 = clean_input(form.final_l_quiz1.data)
        student.final_l_quiz2 = clean_input(form.final_l_quiz2.data)
        student.final_l_quiz3 = clean_input(form.final_l_quiz3.data)
        student.final_l_quiz4 = clean_input(form.final_l_quiz4.data)

        # Update PIT
        student.midterm_pit1 = clean_input(form.midterm_pit1.data)
        student.midterm_pit2 = clean_input(form.midterm_pit2.data)
        student.midterm_pit3 = clean_input(form.midterm_pit3.data)
        student.midterm_pit4 = clean_input(form.midterm_pit4.data)
        student.final_pit1 = clean_input(form.final_pit1.data)
        student.final_pit2 = clean_input(form.final_pit2.data)
        student.final_pit3 = clean_input(form.final_pit3.data)
        student.final_pit4 = clean_input(form.final_pit4.data)

        # Update Exercises
        student.midterm_exercise1 = clean_input(form.midterm_exercise1.data)
        student.midterm_exercise2 = clean_input(form.midterm_exercise2.data)
        student.midterm_exercise3 = clean_input(form.midterm_exercise3.data)
        student.midterm_exercise4 = clean_input(form.midterm_exercise4.data)
        student.final_exercise1 = clean_input(form.final_exercise1.data)
        student.final_exercise2 = clean_input(form.final_exercise2.data)
        student.final_exercise3 = clean_input(form.final_exercise3.data)
        student.final_exercise4 = clean_input(form.final_exercise4.data)

        # Update Laboratories
        student.midterm_laboratory1 = clean_input(form.midterm_laboratory1.data)
        student.midterm_laboratory2 = clean_input(form.midterm_laboratory2.data)
        student.midterm_laboratory3 = clean_input(form.midterm_laboratory3.data)
        student.midterm_laboratory4 = clean_input(form.midterm_laboratory4.data)
        student.final_laboratory1 = clean_input(form.final_laboratory1.data)
        student.final_laboratory2 = clean_input(form.final_laboratory2.data)
        student.final_laboratory3 = clean_input(form.final_laboratory3.data)
        student.final_laboratory4 = clean_input(form.final_laboratory4.data)

        # Update exams and grades (all strings.data)
        student.midterm_exam = clean_input(form.midterm_exam.data)
        student.final_exam = clean_input(form.final_exam.data)
        student.midterm_grade = clean_input(form.midterm_grade.data)
        student.final_grade = clean_input(form.final_grade.data)
        student.midterm_remarks = clean_input(form.midterm_remarks.data)
        student.final_remarks = clean_input(form.final_remarks.data)

        # Update User table if student_id changed
        if old_student_id != new_student_id:
            existing_user = User.query.filter_by(username=new_student_id).first()
            if existing_user:
                flash(f"A user with ID {new_student_id} already exists!", "danger")
                return render_template('edit_student.html', form=form, student=student)

            user = User.query.filter_by(username=old_student_id, role='Student').first()
            if user:
                user.username = new_student_id

            db.session.flush()

        db.session.commit()
        add_log(session.get('username'),
                f'Edited Student: {old_student_id} → {student.student_id} ({new_subject})')
        flash('Student record updated successfully!', 'success')

        return redirect(url_for('dashboard_admin') if session.get('role') == 'Admin'
                            else url_for('dashboard_instructor'))

    # Only pre-fill manually on GET
    if request.method == 'GET':
        form.midterm_quiz1.data = clean_input(student.midterm_quiz1)
        form.midterm_quiz2.data = clean_input(student.midterm_quiz2)
        form.midterm_quiz3.data = clean_input(student.midterm_quiz3)
        form.midterm_quiz4.data = clean_input(student.midterm_quiz4)
        form.midterm_e_quiz1.data = clean_input(student.midterm_e_quiz1)
        form.midterm_e_quiz2.data = clean_input(student.midterm_e_quiz2)
        form.midterm_e_quiz3.data = clean_input(student.midterm_e_quiz3)
        form.midterm_e_quiz4.data = clean_input(student.midterm_e_quiz4)
        form.midterm_l_quiz1.data = clean_input(student.midterm_l_quiz1)
        form.midterm_l_quiz2.data = clean_input(student.midterm_l_quiz2)
        form.midterm_l_quiz3.data = clean_input(student.midterm_l_quiz3)
        form.midterm_l_quiz4.data = clean_input(student.midterm_l_quiz4)

        form.final_quiz1.data = clean_input(student.final_quiz1)
        form.final_quiz2.data = clean_input(student.final_quiz2)
        form.final_quiz3.data = clean_input(student.final_quiz3)
        form.final_quiz4.data = clean_input(student.final_quiz4)
        form.final_e_quiz1.data = clean_input(student.final_e_quiz1)
        form.final_e_quiz2.data = clean_input(student.final_e_quiz2)
        form.final_e_quiz3.data = clean_input(student.final_e_quiz3)
        form.final_e_quiz4.data = clean_input(student.final_e_quiz4)
        form.final_l_quiz1.data = clean_input(student.final_l_quiz1)
        form.final_l_quiz2.data = clean_input(student.final_l_quiz2)
        form.final_l_quiz3.data = clean_input(student.final_l_quiz3)
        form.final_l_quiz4.data = clean_input(student.final_l_quiz4)

        # PIT
        form.midterm_pit1.data = clean_input(student.midterm_pit1)
        form.midterm_pit2.data = clean_input(student.midterm_pit2)
        form.midterm_pit3.data = clean_input(student.midterm_pit3)
        form.midterm_pit4.data = clean_input(student.midterm_pit4)
        form.final_pit1.data = clean_input(student.final_pit1)
        form.final_pit2.data = clean_input(student.final_pit2)
        form.final_pit3.data = clean_input(student.final_pit3)
        form.final_pit4.data = clean_input(student.final_pit4)

        # Exercises
        form.midterm_exercise1.data = clean_input(student.midterm_exercise1)
        form.midterm_exercise2.data = clean_input(student.midterm_exercise2)
        form.midterm_exercise3.data = clean_input(student.midterm_exercise3)
        form.midterm_exercise4.data = clean_input(student.midterm_exercise4)
        form.final_exercise1.data = clean_input(student.final_exercise1)
        form.final_exercise2.data = clean_input(student.final_exercise2)
        form.final_exercise3.data = clean_input(student.final_exercise3)
        form.final_exercise4.data = clean_input(student.final_exercise4)

        # Laboratories
        form.midterm_laboratory1.data = clean_input(student.midterm_laboratory1)
        form.midterm_laboratory2.data = clean_input(student.midterm_laboratory2)
        form.midterm_laboratory3.data = clean_input(student.midterm_laboratory3)
        form.midterm_laboratory4.data = clean_input(student.midterm_laboratory4)
        form.final_laboratory1.data = clean_input(student.final_laboratory1)
        form.final_laboratory2.data = clean_input(student.final_laboratory2)
        form.final_laboratory3.data = clean_input(student.final_laboratory3)
        form.final_laboratory4.data = clean_input(student.final_laboratory4)

        form.midterm_exam.data = clean_input(student.midterm_exam)
        form.final_exam.data = clean_input(student.final_exam)
        form.midterm_grade.data = clean_input(student.midterm_grade)
        form.final_grade.data = clean_input(student.final_grade)
        form.midterm_remarks.data = clean_input(student.midterm_remarks)
        form.final_remarks.data = clean_input(student.final_remarks)

    return render_template('edit_student.html', form=form, student=student)

# --- Student Reset Password ---
@app.route('/admin/reset_password/<student_id>', methods=['POST'])
@login_required(role='Admin')
def reset_password(student_id):
    user = User.query.filter_by(username=student_id, role='Student').first()

    if not user:
        flash("User not found.", "danger")
        return redirect(request.referrer)

    # Reset to default = student_id
    user.password = generate_password_hash(student_id)
    db.session.commit()

    add_log(session['username'], f"Reset password for student {student_id}")
    flash("Password reset to default (Student ID).", "success")
    return redirect(request.referrer)

# --- Student Change Password ---
@app.route('/admin/change_student_password/<student_id>', methods=['POST'])
@login_required(role='Admin')
def change_student_password(student_id):
    new_password = request.form.get('new_password')

    if not new_password:
        flash("Password cannot be empty.", "danger")
        return redirect(request.referrer)

    user = User.query.filter_by(username=student_id, role='Student').first()

    if not user:
        flash("User not found.", "danger")
        return redirect(request.referrer)

    user.password = generate_password_hash(new_password)
    db.session.commit()

    add_log(session['username'], f"Changed password for student {student_id}")
    flash("Password updated successfully.", "success")
    return redirect(request.referrer)

# --- Student delete ---
@app.route('/dashboard/admin/students/delete/<student_id>/<subject>', methods=['POST'])
@app.route('/dashboard/instructor/students/delete/<student_id>/<subject>', methods=['POST'])
@login_required(role=['Admin','Instructor'])
def delete_student(student_id, subject):
    student = Student.query.filter_by(student_id=student_id, subject=subject).first_or_404()
    
    # Delete corresponding User if exists
    user = User.query.filter_by(username=student.student_id, role='Student').first()
    if user:
        db.session.delete(user)

    db.session.delete(student)
    db.session.commit()

    add_log(session['username'], f'Deleted Student: {student.student_id} ({student.subject})')
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('view_students'))

# --- Student bulk delete ---
@app.route('/dashboard/admin/students/bulk_delete', methods=['POST'])
@app.route('/dashboard/instructor/students/bulk_delete', methods=['POST'])
@login_required(role=['Admin','Instructor'])
def bulk_delete_students():
    student_ids = request.form.getlist('student_ids')
    if student_ids:
        deleted_students = []

        for sid in student_ids:
            student = Student.query.get(int(sid))
            if student:
                deleted_students.append(f'{student.student_id} ({student.subject})')

                # Delete corresponding User
                user = User.query.filter_by(username=student.student_id, role='Student').first()
                if user:
                    db.session.delete(user)

                db.session.delete(student)

        db.session.commit()
        add_log(session['username'], f'Bulk deleted Students: {", ".join(deleted_students)}')
        flash(f'{len(student_ids)} student(s) deleted successfully!', 'success')
    else:
        flash('No students selected for deletion.', 'warning')
    return redirect(url_for('view_students'))

# --- CSV upload ---
@app.route('/dashboard/admin/students/upload', methods=['GET', 'POST'])
@app.route('/dashboard/instructor/students/upload', methods=['GET', 'POST'])
@login_required(role=['Admin', 'Instructor'])
def upload_students():
    form = UploadCSVForm()
    summary = None
    errors = []

    def safe_str(value):
        return str(value).strip() if value is not None else ""

    username = session.get('username', 'UnknownUser')

    if form.validate_on_submit():
        file = form.file.data
        if not file or file.filename == '':
            msg = "No file selected."
            errors.append(msg)
            add_log(username, f"CSV upload failed: {msg}")
            return render_template('upload_students.html', form=form, summary=summary, errors=errors)

        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        added_students = []
        updated_students = []
        skipped_students = []

        try:
            with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                required_columns = ['student_id', 'name', 'subject']
                if not reader.fieldnames or not all(col in reader.fieldnames for col in required_columns):
                    msg = f"CSV missing required columns: {required_columns}"
                    errors.append(msg)
                    add_log(username, f"CSV upload failed ({filename}): {msg}")
                    return render_template('upload_students.html', form=form, summary=summary, errors=errors)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        student_id = safe_str(row.get('student_id')).strip()
                        name = safe_str(row.get('name')).strip()
                        section = safe_str(row.get('section')).strip()
                        subject = safe_str(row.get('subject')).strip().title()

                        if not student_id or not subject:
                            msg = f"Row {row_num}: missing required field(s)."
                            errors.append(msg)
                            add_log(username, f"CSV upload warning ({filename}): {msg}")
                            continue

                        # Skip rows where subject accidentally equals the student's name
                        if subject.lower() == name.lower() or subject.lower() in name.lower():
                            msg = f"Row {row_num}: skipped because subject matches student name ({name})."
                            skipped_students.append(f"{student_id} - {name} ({subject})")
                            add_log(username, f"CSV upload skipped ({filename}): {msg}")
                            continue

                        # Prepare grade-related fields
                        field_updates = {

                            # Section
                            'section': section,   # ✅ ADD THIS

                            # Midterm Quizzes
                            'midterm_quiz1': row.get('midterm_quiz1'),
                            'midterm_quiz2': row.get('midterm_quiz2'),
                            'midterm_quiz3': row.get('midterm_quiz3'),
                            'midterm_quiz4': row.get('midterm_quiz4'),
                            'midterm_e_quiz1': row.get('midterm_e_quiz1'),
                            'midterm_e_quiz2': row.get('midterm_e_quiz2'),
                            'midterm_e_quiz3': row.get('midterm_e_quiz3'),
                            'midterm_e_quiz4': row.get('midterm_e_quiz4'),
                            'midterm_l_quiz1': row.get('midterm_l_quiz1'),
                            'midterm_l_quiz2': row.get('midterm_l_quiz2'),
                            'midterm_l_quiz3': row.get('midterm_l_quiz3'),
                            'midterm_l_quiz4': row.get('midterm_l_quiz4'),

                            # Final Quizzes
                            'final_quiz1': row.get('final_quiz1'),
                            'final_quiz2': row.get('final_quiz2'),
                            'final_quiz3': row.get('final_quiz3'),
                            'final_quiz4': row.get('final_quiz4'),
                            'final_e_quiz1': row.get('final_e_quiz1'),
                            'final_e_quiz2': row.get('final_e_quiz2'),
                            'final_e_quiz3': row.get('final_e_quiz3'),
                            'final_e_quiz4': row.get('final_e_quiz4'),
                            'final_l_quiz1': row.get('final_l_quiz1'),
                            'final_l_quiz2': row.get('final_l_quiz2'),
                            'final_l_quiz3': row.get('final_l_quiz3'),
                            'final_l_quiz4': row.get('final_l_quiz4'),

				# PIT
                            'midterm_pit1': row.get('midterm_pit1'),
                            'midterm_pit2': row.get('midterm_pit2'),
                            'midterm_pit3': row.get('midterm_pit3'),
                            'midterm_pit4': row.get('midterm_pit4'),
                            'final_pit1': row.get('final_pit1'),
                            'final_pit2': row.get('final_pit2'),
                            'final_pit3': row.get('final_pit3'),
                            'final_pit4': row.get('final_pit4'),

                            # Exercise
                            'midterm_exercise1': row.get('midterm_exercise1'),
                            'midterm_exercise2': row.get('midterm_exercise2'),
                            'midterm_exercise3': row.get('midterm_exercise3'),
                            'midterm_exercise4': row.get('midterm_exercise4'),
                            'final_exercise1': row.get('final_exercise1'),
                            'final_exercise2': row.get('final_exercise2'),
                            'final_exercise3': row.get('final_exercise3'),
                            'final_exercise4': row.get('final_exercise4'),

                            # Laboratory
                            'midterm_laboratory1': row.get('midterm_laboratory1'),
                            'midterm_laboratory2': row.get('midterm_laboratory2'),
                            'midterm_laboratory3': row.get('midterm_laboratory3'),
                            'midterm_laboratory4': row.get('midterm_laboratory4'),
                            'final_laboratory1': row.get('final_laboratory1'),
                            'final_laboratory2': row.get('final_laboratory2'),
                            'final_laboratory3': row.get('final_laboratory3'),
                            'final_laboratory4': row.get('final_laboratory4'),

                            # Exams
                            'midterm_exam': row.get('midterm_exam'),
                            'final_exam': row.get('final_exam'),
                            'midterm_laboratory_exam': row.get('midterm_laboratory_exam'),
                            'final_laboratory_exam': row.get('final_laboratory_exam'),

                            # Grades
                            'midterm_grade': row.get('midterm_grade'),
                            'final_grade': row.get('final_grade'),

                            # Remarks

                            'midterm_remarks': row.get('midterm_remarks'),
                            'final_remarks': row.get('final_remarks'),
                            }

                        # --- Lookup student by student_id and subject ---
                        student = Student.query.filter(
                            db.func.lower(Student.student_id) == student_id.lower(),
                            db.func.lower(Student.subject) == subject.lower()
                        ).first()
                        if student:
                            # Update existing record
                            patch_update(student, field_updates)
                            if name:
                                student.name = name  # always update name if provided
                            updated_students.append(f"{student_id} - {name} ({subject})")
                        else:
                            # Create new student-subject record
                            create_kwargs = {
                                'student_id': student_id.strip(),
                                'name': name.strip(),
                                'section': section.strip(),
                                'subject': subject.strip().title()
                            }
                            for k, v in field_updates.items():
                                if hasattr(Student, k):
                                    create_kwargs[k] = v
                            new_student = Student(**create_kwargs)
                            db.session.add(new_student)
                            added_students.append(f"{student_id} - {name} ({subject})")

                        # --- Ensure User exists without duplicating ---
                        existing_user = User.query.filter_by(username=student_id).first()
                        if not existing_user:
                            hashed_password = generate_password_hash(student_id)
                            new_user = User(username=student_id, password=hashed_password, role='Student')
                            db.session.add(new_user)
                        else:
                            # Correct role if needed
                            if existing_user.role != 'Student':
                                existing_user.role = 'Student'

                    except Exception as row_error:
                        msg = f"Row {row_num}: {type(row_error).__name__} - {row_error}"
                        errors.append(msg)
                        add_log(username, f"CSV upload error ({filename}): {msg}")

            # Commit once after all rows processed
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                msg = f"Database commit failed: {type(e).__name__} - {e}"
                errors.append(msg)
                add_log(username, f"CSV upload failed ({filename}): {msg}")

        except Exception as file_error:
            msg = f"Error reading file: {type(file_error).__name__} - {file_error}"
            errors.append(msg)
            add_log(username, f"CSV upload failed ({filename}): {msg}")

        # Render summary including errors
        if errors:
            add_log(username, f"CSV upload completed with {len(errors)} error(s) ({filename}).")
            return render_template('upload_students.html', form=form, summary=None, errors=errors)

        add_log(username, f'Uploaded CSV: {filename} ({len(added_students)} added, {len(updated_students)} updated)')
        flash(f'CSV uploaded: {len(added_students)} added, {len(updated_students)} updated', 'success')

        summary = {
            'added': added_students,
            'updated': updated_students,
            'skipped': skipped_students  # currently empty; can populate for duplicates if needed
        }
        return render_template('upload_students.html', form=form, summary=summary, errors=None)

    return render_template('upload_students.html', form=form, summary=summary, errors=None)

# --- CSV download ---
@app.route('/dashboard/admin/download_csv')
@login_required(role=['Admin', 'Instructor'])
def download_csv():
    students = Student.query.all()

    def clean(value):
        return '' if value is None else str(value).strip()

    def generate():
        # FULL HEADER based on your model
        headers = [column.name for column in Student.__table__.columns]
        yield ",".join(headers) + "\n"

        for s in students:
            row = []
            for column in headers:
                value = getattr(s, column)
                value = clean(value).replace('"', '""')
                row.append(f'"{value}"')
            yield ",".join(row) + "\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=students_full.csv"}
    )

# --- database download ---
@app.route('/download_database')
@login_required("Admin")
def download_database():
    db_path = os.path.join(os.getcwd(), 'database.db')

    if not os.path.exists(db_path):
        flash("Database file not found.", "danger")
        return redirect(url_for('dashboard_admin'))

    return send_file(
        db_path,
        as_attachment=True,
        download_name="student_portal_backup.db"
    )

# --- Initialize Database ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist

        # Default users
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('fangnailed'), role='Admin'))
        if not User.query.filter_by(username='student').first():
            db.session.add(User(username='student', password=generate_password_hash('stud123'), role='Student'))

        db.session.commit()

    ENV = os.environ.get('FLASK_ENV', 'development')
    if ENV == 'development':
        app.run(debug=True)
    else:
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000)
