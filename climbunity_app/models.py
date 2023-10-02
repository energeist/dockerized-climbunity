from sqlalchemy_utils import URLType
from climbunity_app.extensions import db
from climbunity_app.utils import FormEnum
from sqlalchemy.orm import backref
from flask_login import UserMixin
import enum

class SendType(FormEnum):
    ONSIGHT = "Onsight send"
    REDPOINT = "Redpoint send"
    SEND = "Fell/hung and finished route"
    ABANDON = "Abandoned ascent"
    FLASH = "Flash"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    has_gear = db.Column(db.Boolean, nullable=False)
    is_admin = db.Column(db.Boolean)
    user_projects = db.relationship('Route',
        secondary='user_project_lists', back_populates='projecting_users'
    ) # User <- N -- N -> Route
    user_appointments = db.relationship('Appointment',
        secondary='appointment_guests', back_populates='appointment_attendants'
    ) # User <- N -- N -> Appointment
    user_does_styles = db.relationship('Style',
        secondary='user_style_lists', back_populates='climber_styles'
    ) # User <- N -- N -> Style

    def __str__(self):
        return f'{self.username}'

    def __repr__(self):
        return f'{self.username}'

class Style(db.Model):
    """ClimberCategory Model to associate route types and climber capabilities / preferences"""
    # using a model because Enums were not working well for many-to-many
    # no CRUD routes for this model because it is meant to be static, could be an admin panel thing?
    id = db.Column(db.Integer, primary_key=True)
    style = db.Column(db.String(8))
    climber_styles = db.relationship('User',
        secondary='user_style_lists', back_populates='user_does_styles'
    ) # User <- N -- N -> Style
    route_styles = db.relationship('Route',
        secondary='route_style_lists', back_populates='possible_route_styles'
    ) # Route <- N -- N -> Style

    def __str__(self):
        return f'{self.style}'

    def __repr__(self):
        return f'{self.style}'
    
user_styles_table = db.Table('user_style_lists',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('style_id', db.Integer, db.ForeignKey('style.id'))
) # User <- N -- N -> Style
    
class Tag(db.Model):
    """RouteTag Model to associate route features to routes for searching"""
    # using a model because Enums were not working well for many-to-many
    # no CRUD routes for this model because it is meant to be static, could be an admin panel thing?
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String)
    tagged_routes = db.relationship('Route',
        secondary='route_tag_lists', back_populates='route_tags'
    ) # Route <- N -- N -> Tag

    def __str__(self):
        return f'{self.tag}'

    def __repr__(self):
        return f'{self.tag}'

class Venue(db.Model):
    """Venue model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    open_hours = db.Column(db.String(500))
    description = db.Column(db.String(500))
    booked_appointments = db.relationship('Appointment', back_populates='appointment_venue') # Venue <-1 -- N-> Appointment

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

class Route(db.Model):
    """Route model"""
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    setter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(80), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    photo_url = db.Column(URLType)
    route_set_date = db.Column(db.Date)
    route_takedown_date = db.Column(db.Date)
    ascents_on_route = db.relationship('Ascent', back_populates='route_ascended') # Route <-1 -- N-> Ascent
    projecting_users = db.relationship('User',
        secondary='user_project_lists', back_populates='user_projects'
    ) # User <- N -- N -> Route
    possible_route_styles = db.relationship('Style',
        secondary='route_style_lists', back_populates='route_styles'
    ) # Route <- N -- N -> Style
    route_tags = db.relationship('Tag',
        secondary='route_tag_lists', back_populates='tagged_routes'
    ) # Route <- N -- N -> Tag

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

project_lists_table = db.Table('user_project_lists',
    db.Column('route_id', db.Integer, db.ForeignKey('route.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
) # User <- N -- N -> Route

route_styles_table = db.Table('route_style_lists',
    db.Column('route_id', db.Integer, db.ForeignKey('route.id')),
    db.Column('style_id', db.Integer, db.ForeignKey('style.id'))
) # Route <- N -- N -> Style

route_styles_table = db.Table('route_tag_lists',
    db.Column('route_id', db.Integer, db.ForeignKey('route.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
) # Route <- N -- N -> Tag

class Ascent(db.Model):
    """Ascent model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    send_date = db.Column(db.Date)
    send_type = db.Column(db.Enum(SendType))
    send_rating = db.Column(db.Integer)
    send_comments = db.Column(db.String(1000))
    route_ascended = db.relationship('Route', back_populates='ascents_on_route')  # Route <-1 -- N-> Ascent

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.name}'

class Appointment(db.Model):
    """Appointment model"""
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    appointment_datetime = db.Column(db.DateTime, nullable=False)
    appointment_venue = db.relationship('Venue', back_populates='booked_appointments') # Venue <-1 -- N-> Appointment
    appointment_attendants = db.relationship('User',
        secondary='appointment_guests', back_populates='user_appointments'
    ) # User <-N -- N -> Appointment

    def __str__(self):
        return f'{self.id}'

    def __repr__(self):
        return f'{self.id}'

appointment_guest_lists = db.Table('appointment_guests',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('appointment_id', db.Integer, db.ForeignKey('appointment.id'))
) # User <-N -- N -> Appointment
