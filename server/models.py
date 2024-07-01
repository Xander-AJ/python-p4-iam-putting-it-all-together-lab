from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = relationship('Recipe', back_populates='user')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('password_hash is not a readable attribute')

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='recipes')

@event.listens_for(User.__table__, 'after_create')
def receive_after_create(target, connection, **kw):
    connection.execute('CREATE UNIQUE INDEX ix_users_username ON users (username)')

@event.listens_for(Recipe.__table__, 'after_create')
def receive_after_create(target, connection, **kw):
    connection.execute('CREATE INDEX ix_recipes_title ON recipes (title)')
