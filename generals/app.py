from config import app, db, migrate, api, bcrypt, CORS
from flask_restful import Resource,reqparse
from flask import request,session,jsonify,make_response
from models.user_profiles import UserProfile
from models.user import User
from models.company_offers import CompanyOffers
# from models.company_offer_items import CompanyOfferingPricesItems
from models.client_booking_details import ClientBookingDetails
from models.movers_company import MoversCompany
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import datetime
from sqlalchemy.exc import IntegrityError

# Define routes or additional configurations here
class SignUp(Resource):
    def post(self):
        data = request.get_json()

        # Check if required fields are present
        required_fields = ['username', 'user_type', 'email', 'password']
        if not all(field in data for field in required_fields):
            return {'message': 'Missing required fields'}, 400

        # Extract data from JSON
        username = data['username']
        user_type = data['user_type']
        email = data['email']
        password = data['password']
       

#         # Check if username or email already exists
        if UserProfile.query.filter_by(username=username).first():
            return {'message': 'Username already exists'}, 409
        if UserProfile.query.filter_by(email=email).first():
            return {'message': 'Email already exists'}, 409

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create a new user instance
        new_user = UserProfile(username=username, user_type=user_type, email=email, password_hash=password_hash)

        # Add user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'User registered successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error registering user: {}'.format(str(e))}, 500

class Index(Resource):
    def get(self):
        return "<h1>Tuzidi project</h1>"

class UserProfileResource(Resource):
    def get(self):
        users = UserProfile.query.all()
        if users:
            user_profiles = []
            for user in users:
                user_profile = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
                user_profiles.append(user_profile)
            return make_response(jsonify(user_profiles), 200)
        else:
            return make_response(jsonify({'error': 'No user profiles found'}), 404)


class UserProfileById(Resource):
    def get(self, user_id):
        user_profile = UserProfile.query.get_or_404(user_id)
        return make_response(jsonify({
            'id': user_profile.id,
            'username': user_profile.username,
            
            'email': user_profile.email,
        }), 200)
    
    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)
        args = parser.parse_args()

        user = UserProfile.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        if args['username']:
            user.username = args['username']
        # if args['user_type']:
        #     user.user_type = args['user_type']
        if args['email']:
            user.email = args['email']
        if args['password']:
            # Set the password using the set_password method
            user.set_password(args['password'])

        db.session.commit()
        return {'message': 'User profile updated successfully'}, 200

    
    def delete(self, user_id):
        user_profile = UserProfile.query.filter_by(id=user_id).first()
        if user_profile:
            db.session.delete(user_profile)
            db.session.commit()
            return {'message': 'User profile deleted successfully'}, 204
        else:
            return {'error': 'User profile not found'}, 404

class ClientBookings(Resource):
    def get(self, user_id):
        # Retrieve user's bookings along with their names
        user_bookings = ClientBookingDetails.query.filter_by(user_id=user_id).all()
        if user_bookings:
            booking_details_list = []
            for booking in user_bookings:
                user_name = booking.user.username  # Access the user's username through the relationship
                booking_details = {
                    'id': booking.id,
                    'user_id': booking.user_id,
                    'user_name': user_name,
                    'current_location': booking.current_location,
                    'new_location': booking.new_location,
                    'moving_date': booking.moving_date,
                    'inventory_type': booking.inventory_type,
                    'total_price': booking.total_price,
                    'status': booking.status
                }
                booking_details_list.append(booking_details)
            return make_response(jsonify(booking_details_list), 200)
        else:
            return make_response(jsonify({'error': 'No client booking details found for this user'}), 404)
    
class ClientBookingPutDelete(Resource):
    def put(self, booking_id):
        data = request.get_json()
        booking = ClientBookingDetails.query.get(booking_id)
        if not booking:
            return make_response(jsonify({'error': 'Booking not found'}), 404)
        try:
            booking.current_location = data.get('current_location', booking.current_location)
            booking.new_location = data.get('new_location', booking.new_location)
            booking.moving_date = data.get('moving_date', booking.moving_date)
            booking.inventory_type = data.get('inventory_type', booking.inventory_type)
            booking.total_price = data.get('total_price', booking.total_price)
            booking.status = data.get('status', booking.status)
            db.session.commit()
            return make_response(jsonify({'message': 'Booking updated successfully'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': 'Failed to update booking', 'details': str(e)}), 500)

    def delete(self, booking_id):
        booking = ClientBookingDetails.query.get(booking_id)
        if not booking:
            return make_response(jsonify({'error': 'Booking not found'}), 404)
        try:
            db.session.delete(booking)
            db.session.commit()
            return make_response(jsonify({'message': 'Booking deleted successfully'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': 'Failed to delete booking', 'details': str(e)}), 500)
   
 
class GeneralClientBookings(Resource):
    def get(self):
        # Retrieve all client bookings
        bookings = ClientBookingDetails.query.all()
        if bookings:
            booking_details_list = []
            for booking in bookings:
                user_name = booking.user.username  # Access the user's username through the relationship
                booking_details = {
                    'id': booking.id,
                    'user_id': booking.user_id,
                    'user_name': user_name,
                    'current_location': booking.current_location,
                    'new_location': booking.new_location,
                    'moving_date': booking.moving_date,
                    'inventory_type': booking.inventory_type,
                    'total_price': booking.total_price,
                    'status': booking.status
                }
                booking_details_list.append(booking_details)
            return make_response( jsonify(booking_details_list), 200)
        else:
            return {'error': 'No client booking details found'}, 404
    def post(self):
        data = request.get_json()
        try:
            # Extract data from the request
            user_id = data.get('user_id')
            company_id = data.get('company_id')
            current_location = data.get('current_location')
            new_location = data.get('new_location')
            moving_date = data.get('moving_date')
            inventory_type = data.get('inventory_type')
            total_price = data.get('total_price')
            
            if total_price is None:
                return make_response(jsonify({"error": "Missing total_price field"}), 400)

# Attempt to convert total_price to an integer
            try:
                total_price = int(total_price)
            except ValueError:
                return make_response(jsonify({"error": "total_price must be an integer"}), 400)
            # Check if any required field is missing
            if None in (user_id, company_id, current_location, new_location, moving_date, inventory_type):
                return make_response(jsonify({"error": "Missing required fields"}), 400)

            # Check for duplicate bookings
            existing_booking = ClientBookingDetails.query.filter_by(
                user_id=user_id,
                company_id=company_id,
                new_location=new_location,
                moving_date=moving_date
            ).first()

            if existing_booking:
                return make_response(jsonify({"error": "Duplicate booking"}), 409)

            # Create a new client booking
            client_booking = ClientBookingDetails(
                user_id=user_id,
                company_id=company_id,
                current_location=current_location,
                new_location=new_location,
                moving_date=moving_date,
                inventory_type=inventory_type,
                total_price=total_price
            )
            db.session.add(client_booking)
            db.session.commit()
            return make_response(jsonify({"message": "Client booking successfully created"}), 201)

        except IntegrityError as e:
            db.session.rollback()
            print(e)  # Print the exception details for debugging
            return make_response(jsonify({"error": "Database integrity error"}), 500)

        except Exception as e:
            db.session.rollback()
            print(e)  # Print the exception details for debugging
            return make_response(jsonify({"error": "Failed to create a new client booking", "details": str(e)}), 500)

# class ClientBookingById(Resource):
#     def delete_client_booking(self, booking_id):  # Rename one of the delete methods
#         booking = ClientBookingDetails.query.get(booking_id)
#         if not booking:
#             return make_response(jsonify({'error': 'Client booking not found'}), 404)
#         try:
#             db.session.delete(booking)
#             db.session.commit()
#             return make_response(jsonify({'message': 'Client booking deleted successfully'}), 200)
#         except Exception as e:
#             return make_response(jsonify({'error': str(e)}), 500)

#     def delete(self, booking_id):  # Keep the other delete method with its original name
#         booking = ClientBookingDetails.query.get(booking_id)
#         if not booking:
#             return make_response(jsonify({'error': 'Client booking not found'}), 404)
#         try:
#             db.session.delete(booking)
#             db.session.commit()
#             return make_response(jsonify({'message': 'Client booking deleted successfully'}), 200)
#         except Exception as e:
#             return make_response(jsonify({'error': str(e)}), 500)


class Moving_Company(Resource):
    def get(self):
        companies = MoversCompany.query.all()
        company_list = []
        for company in companies:
            company_data = {
                'id': company.id,
                'name': company.name,
                'address': company.address,
                'phone': company.phone,
                'email': company.email,
                'location': company.location,
                'working_days': company.working_days,
                'working_hours': company.working_hours
            }
            company_list.append(company_data)
        return make_response(jsonify(company_list), 200)

    def post(self):
        data = request.get_json()
        try:
            name = data['name']
            address = data['address']
            phone = data['phone']
            email = data['email']
            location = data['location']
            working_days = data['working_days']
            working_hours = data['working_hours']
            password = data['password']
        except KeyError:
            return make_response(jsonify({"error": "Missing required fields"}), 400)

        # Check if the company exists
        existing_phone = MoversCompany.query.filter_by(phone=phone).first()
        if existing_phone:
            return make_response(jsonify({"error": "Another company is already using this phone number"}), 409)

        # Optionally, check if the exact name and phone combination exists
        existing_company = MoversCompany.query.filter_by(name=name, phone=phone).first()
        if existing_company:
            return make_response(jsonify({"error": "A company with the same name and phone number already exists"}), 409)

        try:
            moving = MoversCompany(
                name=name,
                address=address,
                phone=phone,
                email=email,
                location=location,
                working_days=working_days,
                working_hours=working_hours,
                password=password
            )
            db.session.add(moving)
            db.session.commit()
            return make_response(jsonify({"message": "Moving company created successfully"}), 201)
        except IntegrityError as e:
            db.session.rollback()
            print(e)  # Print the exception details for debugging
            return make_response(jsonify({"error": "Database integrity error"}), 500)
        except Exception as e:
            db.session.rollback()
            print(e)  # Print the exception details for debugging
            return make_response(jsonify({"error": "Failed to create a new moving company"}), 500)
    

class MovingCompanyById(Resource):
    def get(self, company_id):
        company = MoversCompany.query.get_or_404(company_id)
        return make_response(jsonify({
            'id': company.id,
            'name': company.name,
            'address': company.address,
            'phone': company.phone
        }), 200)
    
    def put(self, company_id):

        data = request.get_json()
        try:
            company = MoversCompany.query.get(company_id)
            if not company:
                return {'message': 'Company not found'}, 404

            for key, value in data.items():
                setattr(company, key, value)

            db.session.commit()
            return {'message': 'Company updated successfully'}, 200
        except KeyError:
            return make_response(jsonify({"error": "Missing required fields"}), 400)
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to update company', 'error': str(e)}, 500


    
    def delete(self, company_id):
        company = MoversCompany.query.get(company_id)
        if not company:
            return make_response(jsonify({'error': 'Movers company not found'}), 404)
        try:
            db.session.delete(company)
            db.session.commit()
            return make_response(jsonify({'message': 'Movers company deleted successfully'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'error': 'Failed to delete movers company'}), 500)


class CompanyOffersResource(Resource):
    def get(self):
        offers = CompanyOffers.query.all()
        offers_list = []
        for offer in offers:
            company_name = offer.company.name if offer.company else None
            offer_data = {
                'id': offer.id,
                'company_id': offer.company_id,
                'company_name': company_name,
                'inventory_type': offer.inventory_type,
                'price': offer.price
            }
            offers_list.append(offer_data)
        return make_response(jsonify(offers_list), 200)

    def post(self):
        data = request.get_json()
        try:
            company_id = data.get('company_id')
            inventory_type = data.get('inventory_type')
            price = data.get('price')
        except KeyError:
            return make_response(jsonify({"error": "Missing required fields"}), 400)

        try:
            new_offer = CompanyOffers(
                company_id=company_id,
                inventory_type=inventory_type,
                price=price
            )
            db.session.add(new_offer)
            db.session.commit()
            return make_response(jsonify({"message": "Company offer created successfully"}), 201)
        except IntegrityError as e:
            db.session.rollback()
            return make_response(jsonify({"error": "Database integrity error"}), 500)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": "Failed to create company offer"}), 500)

   

class CompanyOfferById(Resource):
    def get(self, offer_id):
        offer = CompanyOffers.query.get_or_404(offer_id)
        company_name = offer.company.name if offer.company else None
        return make_response(jsonify({
            'id': offer.id,
            'company_id': offer.company_id,
            'company_name': company_name,
            'inventory_type': offer.inventory_type,
            'price': offer.price
        }), 200)

    def put(self, offer_id):
        data = request.get_json()
        try:
            company_id = data.get('company_id')
            inventory_type = data.get('inventory_type')
            price = data.get('price')
        except KeyError:
            return make_response(jsonify({"error": "Missing required fields"}), 400)

        offer = CompanyOffers.query.get(offer_id)
        if not offer:
            return {'message': 'Offer not found'}, 404

        # Update fields if provided
        if company_id:
            offer.company_id = company_id
        if inventory_type:
            offer.inventory_type = inventory_type
        if price:
            offer.price = price

        try:
            db.session.commit()
            return {'message': 'Offer updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to update offer', 'error': str(e)}, 500

    def delete(self, offer_id):
        offer = CompanyOffers.query.get(offer_id)
        if not offer:
            return make_response(jsonify({'error': 'Company offer not found'}), 404)

        try:
            db.session.delete(offer)
            db.session.commit()
            return make_response(jsonify({'message': 'Company offer deleted successfully'}), 200)
        except Exception as e:
            db.session.rollback()
            return {'message': 'Failed to delete company offer', 'error': str(e)}, 500
  
class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password_hash = data.get('password_hash')   # Assuming password directly

        if not email or not password_hash:
            return make_response(jsonify({'message': 'Missing email or password'}), 400)

        # Check if the email exists in UserProfile
        user_profile = UserProfile.query.filter_by(email=email).first()
        if user_profile and user_profile.check_password(password_hash):
            # Generate JWT token for user
            token = jwt.encode({'user_id': user_profile.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')
            return make_response(jsonify({'token': token}), 200)

        # Check if the email exists in MoversCompany
        movers_company = MoversCompany.query.filter_by(email=email).first()
        if movers_company and movers_company.check_password(password_hash):
            # Generate JWT token for company
            token = jwt.encode({'company_id': movers_company.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')
            return make_response(jsonify({'token': token}), 200)

        # If email and password do not match any user or company
        return make_response(jsonify({'message': 'Invalid email or password'}), 401)

# # Define fields for marshalling the response
#         booking_fields = {
#             'client_name': fields.String(attribute=lambda x: x.user.username),
#             'status': fields.String,
#             'moving_date': fields.String,
#             'current_location': fields.String,
#             'new_location': fields.String,
#             'inventory_type': fields.String
#         }
# # company_id = session.get('company_id')
# class CompanyDashboard(Resource):
#     # Decorate the get method to marshal the response with the specified fields
#     @marshal_with({'bookings': fields.List(fields.Nested(booking_fields))})
#     def get(self):
#         # Retrieve the company ID from the current session
        
#         company_id = session.get('company_id')
        
#         if not company_id:
#             return {'message': 'Company ID not found in session'}, 400

#         # Retrieve the company's bookings from the database
#         company_bookings = db.session.query(ClientBookingDetails, UserProfile)\
#             .join(UserProfile, ClientBookingDetails.user_id == UserProfile.id)\
#             .filter(UserProfile.user_type == 'client', ClientBookingDetails.company_id == company_id)\
#             .all()

#         if not company_bookings:
#             return {'message': 'No bookings found for the company'}, 404

#         # Extract relevant fields for marshalling
#         formatted_bookings = []
#         for booking, user_profile in company_bookings:
#             formatted_booking = {
#                 'client_name': user_profile.username,
#                 'status': booking.status,
#                 'moving_date': booking.moving_date,
#                 'current_location': booking.current_location,
#                 'new_location': booking.new_location,
#                 'inventory_type': booking.inventory_type
#             }
#             formatted_bookings.append(formatted_booking)

#         return {'bookings': formatted_bookings}, 200
class Logout(Resource):
    def delete(self):
        # Check if a user is in session
        if 'user_id' in session:
            session.pop('user_id', None)
        # Check if a company is in session
        if 'company_id' in session:
            session.pop('company_id', None)
        return {}, 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        company_id = session.get('company_id')
        
        if user_id:
            user = UserProfile.query.filter_by(id=user_id).first()
            if user:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
                return user_data, 200

        elif company_id:
            company = MoversCompany.query.filter_by(id=company_id).first()
            if company:
                company_data = {
                    'id': company.id,
                    'name': company.name,
                    'address': company.address,
                    'phone': company.phone,
                    'email': company.email,
                    'location': company.location,
                    'working_days': company.working_days,
                    'working_hours': company.working_hours
                }
                return company_data, 200
        
        return {}, 204
    
class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password_hash = data.get('password_hash')   # Assuming password directly

        if not email or not password_hash:
            return make_response(jsonify({'message': 'Missing email or password'}), 400)

        user_profile = UserProfile.query.filter_by(email=email).first()

        if not user_profile or not user_profile.check_password(password_hash):
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)

        # Determine the user_type
        user_type = user_profile.user_type

        # Generate JWT token
        token = jwt.encode({'user_id': user_profile.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')

        print("Generated token:", token)  

        # Include user_type in the response
        return make_response(jsonify({'token': token, 'user_type': user_type}), 200)
#
# # Add the resource to the API
# api.add_resource(CompanyDashboard, '/company_dashboard')
api.add_resource(UserProfileResource, '/user_profiles')
api.add_resource(UserProfileById, '/user_profiles/<int:user_id>')

api.add_resource(CompanyOffersResource, '/company_offers')
api.add_resource(CompanyOfferById, '/company_offers/<int:offer_id>')
api.add_resource(ClientBookings, '/client_bookings/<int:user_id>')
api.add_resource(ClientBookingPutDelete, '/clientbookings/<booking_id>')
api.add_resource(GeneralClientBookings, '/client_bookings')

api.add_resource(Moving_Company, '/moving_company')
api.add_resource(SignUp, '/sign-up')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(MovingCompanyById, '/moving_company/<int:company_id>')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')


if __name__ == "__main__":
    app.run(debug=True, port=5055)
