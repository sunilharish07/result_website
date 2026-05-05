from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from models import db, Teacher, Student, Result, SUBJECTS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_cors import CORS


# Initialize Flask app and database
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app)

# ─── Decorators ───────────────────────────────────────────────────
# logged-in teachers or students. If a user tries to access a protected route without the appropriate session variable, they are redirected to the login page with an error message.
def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'teacher_id' not in session:
            flash('Please login as teacher.', 'error')
            return redirect(url_for('teacher_login'))
        return f(*args, **kwargs)
    return decorated

def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'student_id' not in session:
            flash('Please login as student.', 'error')
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated

# ─── Landing Page ─────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

# ─── Teacher Auth ─────────────────────────────────────────────────

@app.route('/teacher/register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        name   = request.form['name'].strip()
        reg_no = request.form['register_number'].strip()
        pwd    = request.form['password']
        if Teacher.query.filter_by(register_number=reg_no).first():
            flash('Register number already exists!', 'error')
            return render_template('teacher/register.html')
        teacher = Teacher(name=name, register_number=reg_no, password=generate_password_hash(pwd))
        db.session.add(teacher)
        db.session.commit()
        flash('Registered successfully! Please login.', 'success')
        return redirect(url_for('teacher_login'))
    return render_template('teacher/register.html')

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        name   = request.form['name'].strip()
        reg_no = request.form['register_number'].strip()
        pwd    = request.form['password']
        teacher = Teacher.query.filter_by(register_number=reg_no).first()
        if teacher and teacher.name.lower() == name.lower() and check_password_hash(teacher.password, pwd):
            session['teacher_id']   = teacher.id
            session['teacher_name'] = teacher.name
            return redirect(url_for('teacher_dashboard'))
        flash('Invalid credentials. Try again.', 'error')
    return render_template('teacher/login.html')

@app.route('/teacher/logout')
def teacher_logout():
    session.pop('teacher_id', None)
    session.pop('teacher_name', None)
    return redirect(url_for('index'))

# ─── Student Auth ─────────────────────────────────────────────────

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        roll = request.form['roll_number'].strip()
        name = request.form['name'].strip()
        student = Student.query.filter_by(roll_number=roll).first()
        if student and student.name.lower() == name.lower():
            session['student_id']   = student.id
            session['student_name'] = student.name
            return redirect(url_for('student_dashboard'))
        flash('Invalid roll number or name.', 'error')
    return render_template('student/login.html')

@app.route('/student/logout')
def student_logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    return redirect(url_for('index'))

# ─── Teacher Dashboard ────────────────────────────────────────────

@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    total_students = Student.query.count()
    total_results  = Result.query.count()
    pass_count = Result.query.filter(Result.marks >= 40).count()
    fail_count = Result.query.filter(Result.marks < 40).count()
    pass_pct   = round((pass_count / total_results * 100), 1) if total_results else 0
    fail_pct   = round((fail_count / total_results * 100), 1) if total_results else 0

    subject_stats = []
    for sub in SUBJECTS:
        sub_results = Result.query.filter_by(subject=sub).all()
        if sub_results:
            avg        = round(sum(r.marks for r in sub_results) / len(sub_results), 1)
            s_pass     = sum(1 for r in sub_results if r.marks >= 40)
            s_pass_pct = round((s_pass / len(sub_results)) * 100, 1)
            subject_stats.append({
                'subject': sub, 'avg': avg,
                'pass_pct': s_pass_pct,
                'fail_pct': round(100 - s_pass_pct, 1)
            })

    return render_template('teacher/dashboard.html',
        total_students=total_students, total_results=total_results,
        pass_pct=pass_pct, fail_pct=fail_pct, subject_stats=subject_stats)

# ─── Manage Students ──────────────────────────────────────────────

@app.route('/teacher/students')
@teacher_required
def manage_students(): # 
    students = Student.query.all()
    return render_template('teacher/manage_students.html', students=students)

@app.route('/teacher/student/add', methods=['GET', 'POST'])
@teacher_required
def add_student():
    if request.method == 'POST':
        name = request.form['name'].strip()
        roll = request.form['roll_number'].strip()
        dept = request.form['department'].strip()
        sem  = int(request.form['semester'])
        if Student.query.filter_by(roll_number=roll).first():
            flash('Roll number already exists!', 'error')
            return render_template('teacher/add_student.html')
        db.session.add(Student(name=name, roll_number=roll, department=dept, semester=sem))
        db.session.commit()
        flash(f'Student {name} added!', 'success')
        return redirect(url_for('manage_students'))
    return render_template('teacher/add_student.html')

@app.route('/teacher/student/edit/<int:sid>', methods=['GET', 'POST'])
@teacher_required
def edit_student(sid):
    student = Student.query.get_or_404(sid)
    if request.method == 'POST':
        student.name        = request.form['name'].strip()
        student.roll_number = request.form['roll_number'].strip()
        student.department  = request.form['department'].strip()
        student.semester    = int(request.form['semester'])
        db.session.commit()
        flash('Student updated!', 'success')
        return redirect(url_for('manage_students'))
    return render_template('teacher/edit_students.html', student=student)

@app.route('/teacher/student/delete/<int:sid>')
@teacher_required
def delete_student(sid):
    student = Student.query.get_or_404(sid)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted.', 'success')
    return redirect(url_for('manage_students'))

# ─── Manage Results ───────────────────────────────────────────────

@app.route('/teacher/results')
@teacher_required
def manage_results():
    results  = Result.query.join(Student).order_by(Student.name).all()
    students = Student.query.all()
    return render_template('teacher/manage_results.html', results=results, students=students)

@app.route('/teacher/result/add', methods=['GET', 'POST'])
@teacher_required
def add_result():
    students = Student.query.all()
    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        subject    = request.form['subject']
        marks      = int(request.form['marks'])
        max_marks  = int(request.form['max_marks'])
        semester   = int(request.form['semester'])
        exam_year  = request.form['exam_year'].strip()
        existing = Result.query.filter_by(
            student_id=student_id, subject=subject,
            semester=semester, exam_year=exam_year).first()
        if existing:
            flash('Result already exists for this subject! Edit instead.', 'error')
            return render_template('teacher/add_result.html', students=students, subjects=SUBJECTS)
        result = Result(student_id=student_id, subject=subject,
                        marks=marks, max_marks=max_marks,
                        semester=semester, exam_year=exam_year)
        result.grade = result.compute_grade()
        db.session.add(result)
        db.session.commit()
        flash('Result added!', 'success')
        return redirect(url_for('manage_results'))
    return render_template('teacher/add_result.html', students=students, subjects=SUBJECTS)

@app.route('/teacher/result/edit/<int:rid>', methods=['GET', 'POST'])
@teacher_required
def edit_result(rid):
    result   = Result.query.get_or_404(rid)
    students = Student.query.all()
    if request.method == 'POST':
        result.student_id = int(request.form['student_id'])
        result.subject    = request.form['subject']
        result.marks      = int(request.form['marks'])
        result.max_marks  = int(request.form['max_marks'])
        result.semester   = int(request.form['semester'])
        result.exam_year  = request.form['exam_year'].strip()
        result.grade      = result.compute_grade()
        db.session.commit()
        flash('Result updated!', 'success')
        return redirect(url_for('manage_results'))
    return render_template('teacher/edit_result.html', result=result, students=students, subjects=SUBJECTS)

@app.route('/teacher/result/delete/<int:rid>')
@teacher_required
def delete_result(rid):
    result = Result.query.get_or_404(rid)
    db.session.delete(result)
    db.session.commit()
    flash('Result deleted.', 'success')
    return redirect(url_for('manage_results'))

# ─── Student Dashboard ────────────────────────────────────────────

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student = Student.query.get(session['student_id'])
    results = Result.query.filter_by(student_id=student.id).all()
    total_marks = sum(r.marks for r in results)
    max_total   = sum(r.max_marks for r in results)
    percentage  = round((total_marks / max_total * 100), 2) if max_total else 0
    overall     = 'PASS' if results and all(r.marks >= 40 for r in results) else 'FAIL'
    return render_template('student/dashboard.html',
        student=student, results=results,
        total_marks=total_marks, max_total=max_total,
        percentage=percentage, overall=overall)

# ─── Run ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Connected to MySQL successfully!")
    app.run(debug=True)