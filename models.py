from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

SUBJECTS = [
    'Maths', 'Physics', 'Chemistry',
    'Botany', 'Zoology', 'Kannada',
    'Tamil', 'Hindi', 'English'
]

class Teacher(db.Model):
    __tablename__ = 'teacher'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    register_number = db.Column(db.String(20), unique=True, nullable=False)
    password        = db.Column(db.String(200), nullable=False)

class Student(db.Model):
    __tablename__ = 'student'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    department  = db.Column(db.String(50), nullable=False)
    semester    = db.Column(db.Integer, nullable=False)
    results     = db.relationship('Result', backref='student', lazy=True, cascade='all, delete-orphan')

class Result(db.Model):
    __tablename__ = 'result'
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject    = db.Column(db.String(50), nullable=False)
    marks      = db.Column(db.Integer, nullable=False)
    max_marks  = db.Column(db.Integer, default=100)
    grade      = db.Column(db.String(5))
    semester   = db.Column(db.Integer, nullable=False)
    exam_year  = db.Column(db.String(10), nullable=False)

    def compute_grade(self):
        pct = (self.marks / self.max_marks) * 100
        if pct >= 90: return 'O'
        elif pct >= 80: return 'A+'
        elif pct >= 70: return 'A'
        elif pct >= 60: return 'B+'
        elif pct >= 50: return 'B'
        elif pct >= 40: return 'C'
        else: return 'F'