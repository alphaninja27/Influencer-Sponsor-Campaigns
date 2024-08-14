from flask.cli import AppGroup
from app import app, db, bcrypt
from models import User

admin_cli = AppGroup('admin')

@admin_cli.command('create')
def create_admin():
    admin_email = 'admin@example.com'
    admin_username = 'admin'
    admin_password = 'adminpassword'
    if not User.query.filter_by(email=admin_email).first():
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        admin = User(username=admin_username, email=admin_email, password=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    else:
        print("Admin user already exists!")

app.cli.add_command(admin_cli)
