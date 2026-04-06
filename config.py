class Config:
    SECRET_KEY = 'student_portal_secret_2024'
 
    # ⚠️ Replace YOUR_PASSWORD with your MySQL root password
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost/student_portal'
 
    SQLALCHEMY_TRACK_MODIFICATIONS = False