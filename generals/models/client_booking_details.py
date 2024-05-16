from flask_sqlalchemy import SQLAlchemy
from config import db
from sqlalchemy.orm import validates
from datetime import datetime, date

class ClientBookingDetails(db.Model):
    __tablename__ = 'client_booking_details'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('movers_company.id'), nullable=False)
    current_location = db.Column(db.String, nullable=False)
    new_location = db.Column(db.String, nullable=False)
    moving_date = db.Column(db.String, nullable=False)  # Consider using db.Date for actual date handling
    inventory_type = db.Column(db.String, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default='pending', nullable=False)
   
    @validates('moving_date')
    def validates_moving_date(self, key, moving_date):
        if moving_date is not None:
            try:
                datetime.strptime(moving_date, '%Y-%m-%d')  
            except ValueError:
                raise ValueError('moving_date must be in the format YYYY-MM-DD')
        return moving_date


    def __repr__(self):
        return f"<Client_booking_details user_id={self.user_id}, current_location='{self.current_location}', category='{self.category}', moving_date='{self.moving_date}')>"
