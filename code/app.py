from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from celery import Celery
import redis

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'
jwt = JWTManager(app)
csrf = CSRFProtect(app)

redis_store = redis.StrictRedis.from_url(app.config['CELERY_BROKER_URL'])

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

from models import User  # Ensure models are imported after db initialization
from routes import main

app.register_blueprint(main)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.cli.command("create_admin")
def create_admin():
    admin_email = "admin@example.com"
    admin_password = "adminpassword"
    if not User.query.filter_by(email=admin_email).first():
        admin = User(username="admin", email=admin_email, password=bcrypt.generate_password_hash(admin_password).decode('utf-8'), role="admin")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")
    else:
        print("Admin user already exists")


if __name__ == '__main__':
    app.run(debug=True)
