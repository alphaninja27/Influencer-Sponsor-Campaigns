import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    MAIL_SERVER = 'smtp.example.com'  # Update with your SMTP server
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = '21f3001318@ds.study.iitm.ac.in'  # Update with your email
    MAIL_PASSWORD = 'b4ju6dgv'  # Update with your email password
    MAIL_DEFAULT_SENDER = '21f3001318@ds.study.iitm.ac.in'  # Update with your email
