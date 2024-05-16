from werkzeug.security import generate_password_hash
from models.user_profiles import UserProfile
from models.user import User
from models.company_offers import CompanyOffers
from models.movers_company import MoversCompany
from models.client_booking_details import ClientBookingDetails
from config import app, db

with app.app_context():
    # Delete existing records
    UserProfile.query.delete()
    MoversCompany.query.delete()
    CompanyOffers.query.delete()
    ClientBookingDetails.query.delete()

    # Create and add user profiles
    users_data = [
        {'username': 'Eliab karan', 'email': 'eliab.karan@example.com', 'password': generate_password_hash('password')},
        {'username': 'Emmanuel nyaanga', 'email': 'immanuel.nyaanga@example.com', 'password': generate_password_hash('password')},
        {'username': 'Emmanuel rono', 'email': 'emmanuel.rono@example.com', 'password': generate_password_hash('password')}
    ]
    users = [User(**data) for data in users_data]
    db.session.bulk_save_objects(users)

    # Create and add mover companies
    movers_data = [
        {'name': 'Best Movers', 'email': 'info@bestmovers.com', 'address': '123 Main St', 'phone': '555-1234', 'location': 'City A', 'working_days': 'Monday-Friday', 'working_hours': '9:00AM - 5:00PM', 'password': generate_password_hash('password')},
        {'name': 'Speedy Movers', 'email': 'info@speedymovers.com', 'address': '456 Oak St', 'phone': '555-5678', 'location': 'City B', 'working_days': 'Monday-Saturday', 'working_hours': '8:00AM - 6:00PM', 'password': generate_password_hash('password')}
        # More movers can be added similarly
    ]
    movers = [MoversCompany(**data) for data in movers_data]
    db.session.bulk_save_objects(movers)

    # Ensure users and movers are flushed to assign IDs
    db.session.flush()
    print("home")
    # Create and add offers
    offers_data = [
        {'company_id': movers[0].id, 'inventory_type': 'One Bedroom', 'price': 15000},
        {'company_id': movers[0].id, 'inventory_type': 'Studio', 'price': 20000}
        # More offers can be added similarly
    ]
    offers = [CompanyOffers(**data) for data in offers_data]
    db.session.bulk_save_objects(offers)

    # Add client bookings
    bookings_data = [
        {'user_id': users[0].id, 'company_id': movers[0].id, 'current_location': 'Eldoret', 'new_location': 'Nakuru', 'moving_date': '2024-12-31', 'inventory_type': 'One Bedroom', 'total_price': 15000, 'status': 'pending'}
        # More bookings can be added similarly
    ]
    bookings = [ClientBookingDetails(**data) for data in bookings_data]
    db.session.bulk_save_objects(bookings)

    # Commit all changes to the database
    db.session.commit()

    print("Database seeded successfully!")