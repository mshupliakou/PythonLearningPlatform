from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'pylearn'}
    id_user = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(50), index=True, unique=True)
    password_hash = db.Column(db.Text)
    role=db.Column(db.String(50), index=True, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Module(db.Model):
    __tablename__ = 'modules'
    __table_args__ = {'schema': 'pylearn'}
    id_module = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50))

    description = db.Column(db.Text)

    image_path = db.Column(db.Text, default='default_course.jpg')

    def __repr__(self):
        return f'<Course {self.title}>'