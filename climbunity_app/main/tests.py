import os
import unittest
import app

from datetime import date, datetime
from climbunity_app.extensions import app, db, bcrypt
from climbunity_app.models import *

"""
Run these tests with the command:
python -m unittest climbunity_app.main.tests
^^^ might not work, use
python3 -m unittest discover instead (or this might just register zero tests because why not lol)
"""

#################################################
# Setup
#################################################

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

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

def create_another_user():
    password_hash = bcrypt.generate_password_hash('password234').decode('utf-8')
    user2 = User(
        username='me2',
        password=password_hash,
        email='test234@test.com',
        first_name='AnotherTest',
        last_name='User',
        address='234 Test. St',
        has_gear=True
        )
    db.session.add(user2)
    db.session.commit()

def create_venue():
    v1 = Venue(
        name = "Rock Oasis",
        address = "Dundas and Carlaw"
    )
    db.session.add(v1)
    db.session.commit()

def create_route():
    venue = Venue.query.first()
    user = User.query.first()
    r1 = Route(
        venue_id = 1,
        setter_id = 1,
        name = "Silence",
        grade = "9c+",
    )
    db.session.add(r1)
    db.session.commit()
    # route = Route.query.first()
    # print(route)

def create_ascent():
    user = User.query.first()
    route = Route.query.first()
    a1 = Ascent(
        user_id = user.id,
        route_id = route.id
    )
    db.session.add(a1)
    db.session.commit()

def create_appointment():
    user = User.query.first()
    venue = Venue.query.first()
    apt1 = Appointment(
        created_by = user.id,
        venue_id = venue.id,
        appointment_datetime = datetime(2024,2,28,12,59)
    )
    db.session.add(apt1)
    db.session.commit()

#################################################
# Tests
#################################################

class MainTests(unittest.TestCase):
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
 
    def test_homepage_logged_out(self):
        """Test that the venues show up on the homepage."""
        # Set up
        create_user()
        create_venue()

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Rock Oasis', response_text)
        self.assertIn('Users', response_text)
        self.assertIn('Dundas and Carlaw', response_text)
        self.assertIn('Log In', response_text)
        self.assertIn('Sign Up', response_text)

        # Check that the page doesn't contain things we don't expect
        # (these should be shown only to logged in users)
        self.assertNotIn('New Venue', response_text)
        self.assertNotIn('New Route', response_text)
        self.assertNotIn('New Appointment', response_text)
 
    def test_homepage_logged_in(self):
        """Test that the venue show up on the homepage."""
        # Set up
        create_user()
        create_venue()
        login(self.app, 'me1', 'password123')

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Rock Oasis', response_text)
        self.assertIn('Users', response_text)
        self.assertIn('Dundas and Carlaw', response_text)
        self.assertIn('New Venue', response_text)
        self.assertIn('New Route', response_text)
        self.assertIn('New Appointment', response_text)
 
        # Check that the page doesn't contain things we don't expect
        # (these should be shown only to logged out users)
        self.assertNotIn('Log In', response_text)
        self.assertNotIn('Sign Up', response_text)

    def test_venue_detail_logged_out(self):
        """Test that the book appears on its detail page."""
        # Set up
        create_user()
        create_venue()
        create_route()

        response = self.app.get('/venue/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        
        # print(response_text)
        self.assertIn("<h1>Venue - Rock Oasis</h1>", response_text)
        self.assertIn("<p><strong>Address / Location:</strong> Dundas and Carlaw</p>", response_text)
        self.assertIn("<p><strong>Silence</strong></p></a>", response_text)

        self.assertNotIn("Project Route!", response_text)
        self.assertNotIn("Log an ascent!", response_text)
        self.assertNotIn("Delete route", response_text)

    def test_venue_detail_logged_in(self):
        """Test that the venue appears on its detail page."""
        create_user()
        login(self.app, 'me1', 'password123')  
        create_venue()
        create_route()

        response = self.app.get('/venue/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        
        # print(response_text)
        self.assertIn("<h1>Venue - Rock Oasis</h1>", response_text)
        self.assertIn("<p><strong>Address / Location:</strong> Dundas and Carlaw</p>", response_text)
        self.assertIn("<p><strong>Silence</strong></p></a>", response_text)
        self.assertIn('<input type="submit" value="Project route!">', response_text)
        self.assertIn('<input type="submit" value="Log an ascent!">', response_text)
        self.assertIn('<form method="POST" action="/delete_route/1">', response_text)
        self.assertIn("<legend>Edit this climbing venue:</legend>", response_text)

    def test_create_venue(self):
        """Test creating a venue."""
        # Set up
        create_user()
        login(self.app, 'me1', 'password123')

        # Make POST request with data
        post_data = {
            'name':'Gravity',
            'address':'Frid St. Hamilton',
        }
        self.app.post('/new_venue', data=post_data)

        # Make sure venue was created as we'd expect
        created_venue = Venue.query.filter_by(name='Gravity').one()
        self.assertIsNotNone(created_venue)
        self.assertEqual(created_venue.address, 'Frid St. Hamilton')

    def test_update_venue(self):
    #     """Test updating a venue."""
        create_user()
        login(self.app, 'me1', 'password123')  
        create_venue()
        create_route()

        response = self.app.get('/venue/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        venue = Venue.query.get(1)
        # Make POST request with data
        post_data = {
            'name':"Rock Oasis",
            'address':"Carlaw and Dundas",
            'open_hours':"9-9 every day",
            'description':"an indoor gym with routes"
        }
        self.app.post('/venue/1', data=post_data)
        
        # Make sure the venue was updated as we'd expect
        venue = Venue.query.get(1)
        self.assertEqual(venue.address, "Carlaw and Dundas")
        self.assertEqual(venue.open_hours, "9-9 every day")
        self.assertEqual(venue.description, "an indoor gym with routes")

    def test_create_route(self):
        """Test creating a book."""
        # Set up
        create_user()
        create_venue()
        login(self.app, 'me1', 'password123')

        # Make POST request with data
        post_data = {
            'venue_id':1,
            'setter_id':1,
            'name':"Return of the Sleepwalker",
            'grade':"V17"
        }
        self.app.post('/new_route', data=post_data, follow_redirects=True)

        # Make sure the route was created properly
        created_route = Route.query.one()
        self.assertIsNotNone(created_route)
        self.assertEqual(created_route.grade, 'V17')

    def test_update_route(self):
    #     """Test updating a route."""
        create_user()
        login(self.app, 'me1', 'password123')  
        create_venue()
        create_route()

        response = self.app.get('/route/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        route = Route.query.get(1)
        # Make POST request with data
        post_data = {
            'venue_id':1,
            'setter_id':1,
            'name':"Sleepwalker",
            'grade':"V16",
        }
        response = self.app.post('/route/1', data=post_data, follow_redirects=True)
        response_text = response.get_data(as_text=True)
        # print(response_text)
        # Make sure the route was updated as we'd expect
        route = Route.query.get(1)
        self.assertEqual(route.name, "Sleepwalker")
        self.assertEqual(route.grade, "V16")

    def test_delete_route(self):
    #     """Test deleting a route."""
        create_user()
        login(self.app, 'me1', 'password123')  
        create_venue()
        create_route()

        response = self.app.get('/route/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        route = Route.query.get(1)

        response = self.app.post('/delete_route/1', follow_redirects=True)
        response_text = response.get_data(as_text=True)
        # Make sure the route was updated as we'd expect
        self.assertIn('<p>Silence deleted!</p>', response_text)

    def test_create_venue_logged_out(self):
        """
        Test that the user is redirected when trying to access the create venue 
        route if not logged in.
        """
        # Set up
        create_user()

        # Make GET request
        response = self.app.get('/new_venue')

        # Make sure that the user was redirecte to the login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login?next=%2Fnew_venue', response.location)

    def test_create_route_logged_out(self):
        """
        Test that the user is redirected when trying to access the create route 
        route if not logged in.
        """
        # Set up
        create_user()

        # Make GET request
        response = self.app.get('/new_route')

        # Make sure that the user was redirecte to the login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login?next=%2Fnew_route', response.location)

    def test_create_appointment_logged_out(self):
        """
        Test that the user is redirected when trying to access the create appointment 
        route if not logged in.
        """
        # Set up
        create_user()

        # Make GET request
        response = self.app.get('/new_appointment')

        # Make sure that the user was redirecte to the login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login?next=%2Fnew_appointment', response.location)
    
    def test_project_route(self):
        """Test selecting a route as a project."""
        # Set up
        create_user()
        create_venue()
        create_route()
        login(self.app, 'me1', 'password123')

        route=Route.query.get(1)

        response = self.app.post(f'/add_to_project_list/{route.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response_text = response.get_data(as_text=True)
        self.assertIn('<p>Silence added to project list</p>', response_text)

    def test_delete_project(self):
        """Test removing route from project list."""
        # Set up
        create_user()
        create_venue()
        create_route()
        login(self.app, 'me1', 'password123')
        route=Route.query.get(1)

        # add route to project list first
        response = self.app.post(f'/add_to_project_list/{route.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response_text = response.get_data(as_text=True)
        self.assertIn('<p>Silence added to project list</p>', response_text)
        
        # remove from project list
        response = self.app.post(f'/remove_from_project_list/{route.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        response_text = response.get_data(as_text=True)
        self.assertIn('<p>Silence removed from project list</p>', response_text)

    def test_create_appointment(self):
        """Test creating an appointment."""
        # Set up
        create_user()
        create_venue()
        create_route()
        login(self.app, 'me1', 'password123')

        route = Route.query.get(1)
        user = User.query.get(1)
        venue = Venue.query.get(1)
        # Make POST request with data'
        current_datetime = datetime.now()
        # print(current_datetime)
        post_data = {
            'created_by':user.id,
            'venue_id':venue.id,
            'appointment_datetime':'2023-02-28T12:59'
        }
        response = self.app.post(f'/new_appointment', data=post_data, follow_redirects=True)
        response_text = response.get_data(as_text=True)
        # Make sure the appointment was created properly
        appointment = Appointment.query.one()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.created_by, 1)
        self.assertEqual(appointment.appointment_datetime, datetime(2023,2,28,12,59))

    def test_delete_appointment(self):
        """Test deleting an appointment."""
        # Set up
        create_user()
        create_venue()
        create_route()
        login(self.app, 'me1', 'password123')

        route = Route.query.get(1)
        user = User.query.get(1)
        venue = Venue.query.get(1)
        # Make POST request with data'
        current_datetime = datetime.now()
        # print(current_datetime)
        post_data = {
            'created_by':user.id,
            'venue_id':venue.id,
            'appointment_datetime':'2023-02-28T12:59'
        }
        self.app.post(f'/new_appointment', data=post_data, follow_redirects=True)
        # Make sure the appointment was created properly
        appointment = Appointment.query.one()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.created_by, 1)
        self.assertEqual(appointment.appointment_datetime, datetime(2023,2,28,12,59))

        response = self.app.post(f'/delete_appointment/{appointment.id}', follow_redirects=True)
        response_text = response.get_data(as_text=True)
        user = User.query.get(1)
        self.assertIn("<p>Appointment deleted!</p>", response_text)
        self.assertEqual(len(user.user_appointments), 0)

    def test_join_appointment(self):
        """Test joining an appointment."""
        # Set up
        create_user()
        create_another_user()
        create_venue()
        create_route()
        create_appointment()
        login(self.app, 'me2', 'password234')

        appointment = Appointment.query.get(1)
        response = self.app.post(f'/join_appointment/{appointment.id}', follow_redirects=True)
        response_text = response.get_data(as_text=True)
        user = User.query.get(2)
        self.assertIn("<p>You&#39;ve joined an appointment!</p>", response_text)
        self.assertEqual(len(user.user_appointments), 1)

    def test_create_ascent(self):
        """Test creating an ascent."""
        # Set up
        create_user()
        create_venue()
        create_route()
        login(self.app, 'me1', 'password123')

        route = Route.query.get(1)
        # Make POST request with data
        post_data = {
            'user_id':1,
            'route_id':route.id,
            'ascent_type':'ONSIGHT',
            'ascent_date':'2022-02-02',
            'rating':5
        }
        response = self.app.post(f'/log_ascent/{route.id}', data=post_data, follow_redirects=True)
        response_text = response.get_data(as_text=True)

        # Make sure the ascent was created properly
        ascent = Ascent.query.one()
        self.assertIsNotNone(ascent)
        self.assertEqual(ascent.send_rating, 5)
        self.assertEqual(ascent.send_date, date(2022,2,2))

    def test_remove_ascent(self):
        """Test removing an ascent."""
        # Set up
        create_user()
        create_venue()
        create_route()
        login(self.app, 'me1', 'password123')

        route = Route.query.get(1)
        # Make POST request with data
        post_data = {
            'user_id':1,
            'route_id':route.id,
            'ascent_type':'ONSIGHT',
            'ascent_date':'2022-02-02',
            'rating':5
        }
        response = self.app.post(f'/log_ascent/{route.id}', data=post_data, follow_redirects=True)
        response_text = response.get_data(as_text=True)
        
        # Make sure the ascent was created properly
        ascent = Ascent.query.one()
        self.assertIsNotNone(ascent)
        self.assertEqual(ascent.send_rating, 5)
        self.assertEqual(ascent.send_date, date(2022,2,2))

        response = self.app.post(f'/delete_ascent/{ascent.id}', data=post_data, follow_redirects=True)
        response_text = response.get_data(as_text=True)
        self.assertIn("<p>Silence removed from ascent list</p>", response_text)


