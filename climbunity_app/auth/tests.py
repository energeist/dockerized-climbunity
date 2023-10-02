import os
from unittest import TestCase
# import unittest
import app
from datetime import date
 
from climbunity_app.extensions import app, db, bcrypt
from climbunity_app.models import SendType, User, Style, Tag, Venue, Route, Ascent, Appointment 

"""
Run these tests with the command:
python -m unittest climbunity_app.auth.tests
^^^ might not work, use
python3 -m unittest discover instead (or this might just register zero tests because why not lol)
"""

#################################################
# Setup
#################################################

def create_user():
    password_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
    user = User(
        username='me1',
        password=password_hash,
        email='test123@test.com',
        first_name='Test',
        last_name='User',
        address='123 Test. St',
        has_gear=True
        )
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        # TODO: Write a test for the signup route. It should:
        # - Make a POST request to /signup, sending a username & password
        # - Check that the user now exists in the database
        password_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
        post_data = {
            "username": "me1",
            "password": password_hash,
            "email": "test1243@test.com",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test. St.",
            "has_gear": True
        }
        self.app.post('/signup', data=post_data)
        new_user = User.query.filter_by(username="me1").one()
        self.assertEqual(new_user.username, "me1")

    def test_signup_existing_user(self):
        create_user()
        password_hash = bcrypt.generate_password_hash('password123').decode('utf-8')        
        post_data = {
            "username": "me1",
            "password": password_hash,
            "email": "test1243@test.com",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test. St.",
            "has_gear": True
        }
        new_user = User.query.filter_by(username="me1").one()
        self.assertEqual(new_user.username, "me1")
        response = self.app.post('/signup', data=post_data)
        response_text = response.get_data(as_text=True)
        self.assertIn("That username is taken", response_text)

    def test_login_correct_password(self):
        # TODO: Write a test for the login route. It should:
        # - Create a user
        # - Make a POST request to /login, sending the created username & password
        # - Check that the "login" button is not displayed on the homepage
        create_user()
        post_data = {
            "username": "me1",
            "password": "password123"
        }
        new_user = User.query.filter_by(username="me1").one()
        self.assertEqual(new_user.username, "me1")
        response = (self.app.post('/login', data=post_data, follow_redirects=True))
        response_text = response.get_data(as_text=True)
        self.assertIn("You are logged in as me1", response_text)

    def test_login_nonexistent_user(self):
        # TODO: Write a test for the login route. It should:
        # - Make a POST request to /login, sending a username & password
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        post_data = {
            "username": "me1",
            "password": "totallylegit"
        }
        response = (self.app.post('/login', data=post_data, follow_redirects=True))
        response_text = response.get_data(as_text=True)
        self.assertIn("No user with that username", response_text)

    def test_login_incorrect_password(self):
        # TODO: Write a test for the login route. It should:
        # - Create a user
        # - Make a POST request to /login, sending the created username &
        #   an incorrect password
        # - Check that the login form is displayed again, with an appropriate
        #   error message
        create_user()
        post_data = {
            "username": "me1",
            "password": "totallylegit"
        }
        response = (self.app.post('/login', data=post_data, follow_redirects=True))
        response_text = response.get_data(as_text=True)
        self.assertIn("Password doesn&#39;t match", response_text)

    def test_logout(self):
        # TODO: Write a test for the logout route. It should:
        # - Create a user
        # - Log the user in (make a POST request to /login)
        # - Make a GET request to /logout
        # - Check that the "login" button appears on the homepage
        create_user()
        post_data = {
            "username": "me1",
            "password": "password123"
        }
        response = (self.app.post('/login', data=post_data, follow_redirects=True))
        response_text = response.get_data(as_text=True)
        self.assertIn("You are logged in as me1", response_text)
        # self.app.post('/signup', data=post_data)
        new_user = User.query.filter_by(username="me1").one()
        self.assertEqual(new_user.username, "me1")
        response = (self.app.get('/logout', follow_redirects=True))
        response_text = response.get_data(as_text=True)
        response.get_data(as_text=True)
        self.assertIn('<a href="/login">Log In</a>', response_text)
        