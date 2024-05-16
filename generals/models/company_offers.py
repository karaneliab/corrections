from flask_sqlalchemy import SQLAlchemy

from config import db 

class CompanyOffers(db.Model):
    __tablename__ = 'company_offers'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('movers_company.id', ondelete='CASCADE'), nullable=False)
    inventory_type = db.Column(db.String(50))
    price = db.Column(db.Integer, nullable=False)

    # Change the backref name to avoid conflict
    movers_company = db.relationship('MoversCompany', backref='offers')


    

    def __repr__(self):
        # Use f-string for cleaner string formatting
        return f"<CompanyOffers id={self.id}, company_id={self.company_id}, inventory_type='{self.inventory_type}', price='{self.price}')>"