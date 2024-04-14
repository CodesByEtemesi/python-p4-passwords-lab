# #!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource

from config import app, db, api
from models import User

class Signup(Resource):
    
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        
        # Check if username and password are provided
        if not username or not password:
            return {'message': 'Username and password are required.'}, 400
        
        # Check if the username is already taken
        if User.query.filter_by(username=username).first():
            return {'message': 'Username already exists. Please choose another one.'}, 400
        
        # Create a new user
        user = User(username=username)
        user.password_hash = password
        
        # Add user to the database
        db.session.add(user)
        db.session.commit()
        
        # Save user ID in session
        session['user_id'] = user.id
        
        # Return the user object in the JSON response
        return user.to_dict(), 201

class CheckSession(Resource):
    
    def get(self):
        user_id = session.get('user_id')
        
        # If user is authenticated
        if user_id:
            user = User.query.get(user_id)
            return user.to_dict()
        else:
            return {}, 204

class Login(Resource):
    
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        
        # Find the user by username
        user = User.query.filter_by(username=username).first()
        
        # If user not found or password is incorrect
        if not user or not user.authenticate(password):
            return {'message': 'Invalid username or password'}, 401
        
        # Save user ID in session
        session['user_id'] = user.id
        
        # Return the user object in the JSON response
        return user.to_dict()

class Logout(Resource):
    
    def delete(self):
        # Clear the session
        session.clear()
        return {}, 204

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
