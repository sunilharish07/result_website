import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'student_portal_secret_2024')

    # Use `DATABASE_URL` env var in production (e.g. mysql+pymysql://user:pass@host/db)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'mysql+pymysql://root:1234@localhost/student_portal'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False