from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FloatField, PasswordField, IntegerField, RadioField, SelectMultipleField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, URL, ValidationError, NumberRange
from climbunity_app.utils import FormEnum
from climbunity_app.models import *
from climbunity_app.extensions import app, db, bcrypt
from wtforms.fields.html5 import DateField, TimeField, DateTimeField, DateTimeLocalField
# from flask_login import current_user

# TODO: filter by style when adding users to a route (query route style and validate style, then query users with that style)

class VenueForm(FlaskForm):
    """Form for adding/updating a Venue."""
    name = StringField('Venue Name',
    validators=[
        DataRequired(), 
        Length(min=3, max=80, message="Your venue name needs to be betweeen 3 and 80 chars")
    ])
    address = StringField('Address',
    validators=[
        DataRequired(), 
        Length(min=3, max=80, message="You need to enter a street address or general location, 3 characters min.")
    ])
    open_hours = StringField('Hours of Operation', validators=[
        Length(min=3, max=500, message="Please limit entry to 500 characters")
    ])
    description = StringField('Description', validators=[
        Length(min=3, max=500, message="Please limit entry to 500 characters")
    ])
    submit = SubmitField('Submit')

class RouteForm(FlaskForm):
    """Form for adding/updating a Route."""

    name = StringField('Route Name', 
        validators=[
            DataRequired(), 
            Length(min=1, max=80, message="Your route name needs to be betweeen 1 and 80 characters.")
        ])
    venue_id = QuerySelectField('Gym / Crag',
        query_factory=lambda: Venue.query,
        validators=[DataRequired()]
        )
    setter_id = QuerySelectField('Route Setter',
        query_factory=lambda: User.query)
    grade = StringField('Route Grade', validators=[Length(max=10, message="Please input a simple YDS or V-grade entry, maximum 10 characters.")]) 
    photo_url = StringField('Photo URL')
    route_set_date = DateField('Route Set Date')
    route_takedown_date = DateField('Projected Route Takedown Date')
    route_styles = QuerySelectMultipleField('What type of route is this?',
        query_factory=lambda: Style.query)
    route_tags = QuerySelectMultipleField('Apply tags to this route',
        query_factory=lambda: Tag.query)
    submit = SubmitField('Submit')

class AscentForm(FlaskForm):
    """Form for logging a route ascent"""
    ascent_date = DateField("Date of ascent", validators=[DataRequired()])
    ascent_type = SelectField("Type of ascent", choices=SendType.choices())
    rating = RadioField("Personal route rating", choices=[0,1,2,3,4,5])
    comments = StringField("Comments", validators=[Length(max=1000, message="Please limit comments to 1000 characters.")])
    submit = SubmitField('Submit')

class AppointmentForm(FlaskForm):
    """Form for creating an appointment"""
    appointment_datetime = DateTimeLocalField(
        'Appointment Date and Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    venue_id = QuerySelectField('Venue', 
        query_factory=lambda: Venue.query, 
        validators=[DataRequired()]
    )
    additional_guests = QuerySelectMultipleField('Additional guests',
        query_factory=lambda: User.query
    )

    def validate_appointment_datetime(self, appointment_datetime):
        if appointment_datetime.data <= datetime.now():
            raise ValidationError("The appointment date cannot be in the past!")

    submit = SubmitField('Submit')
