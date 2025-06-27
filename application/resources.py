from flask_restful import Resource, Api, reqparse
from application.models import Subject, User, db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

api = Api(prefix='/api')

class SubjectResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, help='Name is a string', required=True, trim=True, location='json')
    parser.add_argument('description', type=str, help='Description is a string', required=True, trim=True, location='json')

    def get(self):
        subjects = Subject.query.all()
        return [{"id": s.id, "name": s.name, "description": s.description, "created_by": s.created_by} for s in subjects], 200

    def post(self):
        try:
            args = self.parser.parse_args()
            subject = Subject(
                name=args['name'],
                description=args['description'],
                created_by=1,  # Hardcoded admin ID; replace with auth later
                created_at=datetime.utcnow()
            )
            db.session.add(subject)
            db.session.commit()
            return {"message": "Subject is created"}, 201
        except IntegrityError:
            db.session.rollback()
            return {"message": "Subject with this name already exists"}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error: {str(e)}"}, 500

class RegisterResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=str, help='Username is required', required=True, trim=True, location='json')
    parser.add_argument('email_id', type=str, help='Email is required', required=True, trim=True, location='json')
    parser.add_argument('name', type=str, help='Full name is required', required=True, trim=True, location='json')
    parser.add_argument('qualification', type=str, help='Qualification is required', required=True, trim=True, location='json')
    parser.add_argument('dob', type=str, help='Date of birth is required', required=True, trim=True, location='json')
    parser.add_argument('password', type=str, help='Password is required', required=True, location='json')

    def post(self):
        try:
            args = self.parser.parse_args()
            if '@' not in args['email_id']:
                return {"message": "Invalid email format"}, 400
            dob = datetime.strptime(args['dob'], '%Y-%m-%d').date()
            user = User(
                user_id=args['user_id'],
                email_id=args['email_id'],
                name=args['name'],
                qualification=args['qualification'],
                dob=dob,
                password=generate_password_hash(args['password']),
                role='user'
            )
            db.session.add(user)
            db.session.commit()
            return {"message": "User registered successfully"}, 201
        except IntegrityError:
            db.session.rollback()
            return {"message": "Username or email already exists"}, 400
        except ValueError:
            return {"message": "Invalid date format. Use YYYY-MM-DD"}, 400
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error: {str(e)}"}, 500

api.add_resource(SubjectResource, '/subjects')
api.add_resource(RegisterResource, '/register')