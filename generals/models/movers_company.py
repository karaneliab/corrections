from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import db
from werkzeug.security import generate_password_hash, check_password_hash


class MoversCompany(db.Model):
    __tablename__ = 'movers_company'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), unique=True, nullable=False)
    working_days = db.Column(db.String(128), nullable=False)
    working_hours = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Change the backref name to avoid conflict
    company_offers = db.relationship('CompanyOffers', backref='movers_company')
   
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<MoversCompany(name='{self.name}', address='{self.address}', phone='{self.phone}')>"
