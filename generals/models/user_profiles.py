from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from config import db
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    additional_info = db.Column(db.String(256))
    user = db.relationship('User', back_populates='profile')


    # Relationship with User
    # user = db.relationship('User', backref='profile')

