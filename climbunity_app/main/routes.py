import os
import time
import random
from os.path import exists
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from climbunity_app.utils import FormEnum
from climbunity_app.models import *
from climbunity_app.main.forms import *
from climbunity_app.auth.forms import *

from climbunity_app.extensions import app, db, bcrypt

main = Blueprint("main", __name__)

##########################################
#           Routes                       #
##########################################

# homepage route 
@main.route('/')
def homepage():
    all_venues = Venue.query.all()
    routes = Route.query.all()
    return render_template('home.html', routes=routes, all_venues=all_venues)

######################
#  venue routes
######################

# create
@main.route('/new_venue', methods=['GET', 'POST'])
@login_required
def new_venue():
    form = VenueForm()
    if form.is_submitted():
        new_venue = Venue(
            name=form.name.data,
            address=form.address.data,
            open_hours=form.open_hours.data,
            description=form.description.data,
        )
        db.session.add(new_venue)
        db.session.commit()
        flash('New venue was created successfully.')
        return redirect(url_for('main.venue_detail', venue_id=new_venue.id))
    return render_template('new_venue.html', form=form)

# read and update
@main.route('/venue/<venue_id>', methods=['GET', 'POST'])
def venue_detail(venue_id):
    venue = Venue.query.get(venue_id)
    routes = Route.query.filter_by(venue_id=venue_id).all()
    form = VenueForm(obj=venue)

    if form.validate_on_submit():
        venue.name = form.name.data
        venue.address = form.address.data
        venue.open_hours = form.open_hours.data
        venue.description = form.description.data
        db.session.commit()
        flash('Venue was edited successfully.')
        return redirect(url_for('main.venue_detail', venue_id=venue.id))

    venue = Venue.query.get(venue_id)
    return render_template('venue_detail.html', form=form, routes=routes, venue=venue)

@main.route('/delete_venue/<venue_id>', methods=['POST'])
@login_required
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    for appointment in venue.booked_appointments:
        db.session.delete(appointment)
        db.session.commit()
    routes = Route.query.filter_by(venue_id=venue.id).all()
    for route in routes:
        for ascent in route.ascents_on_route:
            db.session.delete(ascent)
            db.session.commit()
        db.session.delete(route)
        db.session.commit()
    db.session.delete(venue)
    db.session.commit()
    flash(f"{venue.name} deleted!")
    return redirect(url_for("main.homepage"))

######################
#  climbing route routes
######################

# create
@main.route('/new_route', methods=['GET', 'POST'])
@login_required
def new_route():
    form = RouteForm()
    if form.validate_on_submit():
        image_exists = os.path.exists(f'../static/img/{form.photo_url.data}')
        if image_exists:
            image_url = form.photo_url.data
        else:
            image_url = '/static/img/no_image.jpeg'
        new_route = Route(
            name=form.name.data,
            venue_id = form.venue_id.data.id,
            setter_id = form.setter_id.data.id,
            grade=form.grade.data,
            photo_url=image_url,
            route_set_date=form.route_set_date.data,
            route_takedown_date=form.route_takedown_date.data,
        )
        db.session.add(new_route)
        db.session.commit()
        for style in form.route_styles.data:
            new_route.possible_route_styles.append(style)
        for tag in form.route_tags.data:
            new_route.route_tags.append(tag)
        db.session.commit()
        flash('New route was created successfully.')
        return redirect(url_for('main.route_detail', route_id=new_route.id))
    return render_template('new_route.html', form=form)

# read and update
@main.route('/route/<route_id>', methods=['GET', 'POST'])
def route_detail(route_id):
    route = Route.query.get(route_id)
    route_venue = Venue.query.get(route.venue_id)
    setter = User.query.get(route.setter_id)
    ratings = 0
    rating = 0
    if route.ascents_on_route:
        for ascent in route.ascents_on_route:
            ratings += ascent.send_rating
        rating = ratings/len(route.ascents_on_route)
    form = RouteForm(obj=route)
    if form.validate_on_submit():
        image_exists = os.path.exists(f'/static/img/{form.photo_url.data}')
        if image_exists:
            image_url = form.photo_url.data
        else:
            image_url = '/static/img/no_image.jpeg'
        route.name = form.name.data
        route.venue_id = form.venue_id.data.id
        route.grade = form.grade.data
        route.photo_url = image_url
        route.route_set_date = form.route_set_date.data
        route.route_takedown_date = form.route_takedown_date.data
        route.possible_route_styles.extend(form.route_styles.data)
        route.route_tags.extend(form.route_tags.data)
        db.session.commit()
        flash('Route was edited successfully.')
        return redirect(url_for('main.route_detail', route_id=route.id, route_venue=route_venue, setter=setter, rating=rating))
    item = Route.query.get(route_id)
    return render_template('route_detail.html', form=form, route=route, route_venue=route_venue, setter=setter, rating=rating)

# delete
@main.route('/delete_route/<route_id>', methods=['POST'])
@login_required
def delete_route(route_id):
    route = Route.query.get(route_id)
    for ascent in route.ascents_on_route:
        db.session.delete(ascent)
        db.session.commit()
    db.session.delete(route)
    db.session.commit()
    flash(f"{route.name} deleted!")
    return redirect(url_for("main.venue_detail", venue_id=route.venue_id))

######################
#  project list routes
######################

# read on user profile pages
# create
@main.route('/add_to_project_list/<route_id>', methods=['POST'])
@login_required
def add_to_project_list(route_id):
    route = Route.query.get(route_id)
    current_user.user_projects.append(route)
    db.session.commit()
    flash(f"{route.name} added to project list")
    return redirect(url_for("main.route_detail", route_id = route.id, user_id=current_user.id))

# update / delete
@main.route('/remove_from_project_list/<route_id>', methods=['POST'])
@login_required
def remove_from_project_list(route_id):
    route = Route.query.get(route_id)
    current_user.user_projects.remove(route)
    db.session.commit()
    flash(f"{route.name} removed from project list")
    return redirect(url_for("main.user_detail", user_id=current_user.id))

######################
#  ascent routes
######################

# create
@main.route('/log_ascent/<route_id>', methods=['GET', 'POST'])
@login_required
def log_ascent(route_id):
    route = Route.query.get(route_id)
    venue = Venue.query.get(route.venue_id)
    form = AscentForm()
    if form.validate_on_submit():
        new_ascent = Ascent(
            user_id = current_user.id,
            route_id = route.id,
            send_date = form.ascent_date.data,
            send_type = form.ascent_type.data,
            send_rating = form.rating.data,
            send_comments = form.comments.data
        )
        route.ascents_on_route.append(new_ascent)
        db.session.add(new_ascent)
        db.session.commit()
        flash('New ascent was logged successfully.')
        return redirect(url_for('main.route_detail', route_id=route.id, venue=venue))
    return render_template('new_ascent.html', route_id=route.id, route=route, venue=venue, form=form)

# delete (no update)
@main.route('/delete_ascent/<ascent_id>', methods=['POST'])
@login_required
def delete_ascent(ascent_id):
    ascent = Ascent.query.get(ascent_id)
    route = Route.query.get(ascent.route_id)
    route.ascents_on_route.remove(ascent)
    db.session.delete(ascent)
    db.session.commit()
    flash(f"{route.name} removed from ascent list")
    return redirect(url_for("main.user_detail", user_id=current_user.id))

######################
#  profile routes
######################

# user creation route is in auth routes
# display all profiles
@main.route('/users', methods=['GET', 'POST'])
def all_users():
    users = User.query.all()
    return render_template('all_users.html', users=users)  
  
# read specific profile
@main.route('/profile/<user_id>', methods=['GET', 'POST'])
def user_detail(user_id):
    routes = Route.query.all()
    venues = Venue.query.all()
    user = User.query.get(user_id)
    ascents = Ascent.query.filter_by(user_id=user_id).all() # fine for small data but should be built out to display only 3-5 results + option to see all on different page
    if current_user == user:
        form = SignUpForm(obj=user)
        return render_template('user_detail.html', routes=routes, ascents=ascents, venues=venues, user=user, form=form)  
    else:
        user = User.query.get(user_id)
    return render_template('user_detail.html', routes=routes, ascents=ascents, venues=venues, user=user)

# update profile
    
@main.route('/edit_profile/<user_id>', methods=['GET', 'POST'])
def edit_user_detail(user_id):
    routes = Route.query.all()
    user = User.query.get(user_id)
    ascents = Ascent.query.filter_by(user_id=user_id).limit(5).all()
    form = EditProfileForm(obj=user)
    if current_user == user:
        if form.validate_on_submit():
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.address = form.address.data
            user.has_gear = form.has_gear.data
            user.user_does_styles.clear()
            user.user_does_styles.extend(form.climber_styles.data)
            flash('User profile was edited successfully.')
            db.session.commit()
        user = user.query.get(current_user.id)
        response = redirect(url_for("main.user_detail", user_id=user.id, form=form, follow_redirects=True))
        response_text = response.get_data(as_text=True)
    else:
        user = User.query.get(user_id)
    return render_template('user_detail.html', routes=routes, ascents=ascents, user=user, form=form)

######################
#  appointment routes
######################

# create 
@main.route('/new_appointment', methods=['GET', 'POST'])
@login_required
def new_appointment():
    form = AppointmentForm()
    if form.validate_on_submit():
        new_appointment = Appointment(
            created_by=current_user.id,
            venue_id=form.venue_id.data.id,
            appointment_datetime=form.appointment_datetime.data
        )
        current_user.user_appointments.append(new_appointment) # append to creator event list
        if form.additional_guests.data:
            for guest in form.additional_guests.data:
                guest.user_appointments.append(new_appointment)
        venue = Venue.query.filter_by(id=new_appointment.venue_id).one()
        venue.booked_appointments.append(new_appointment)
        db.session.add(new_appointment)
        db.session.commit()
        flash('New appointment was created successfully.')
        return redirect(url_for("main.user_detail", user_id=current_user.id))
    return render_template('new_appointment.html', form=form)

# join (update with new user)
@main.route('/join_appointment/<appointment_id>', methods=['POST'])
@login_required
def join_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    current_user.user_appointments.append(appointment)
    db.session.commit()
    flash(f"You've joined an appointment!")
    return redirect(url_for("main.user_detail", user_id=current_user.id))

# delete
@main.route('/delete_appointment/<appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    appointment.appointment_attendants.clear()
    appointment.appointment_venues.clear()
    db.session.delete(appointment)
    db.session.commit()
    flash(f"Appointment deleted!")
    return redirect(url_for("main.user_detail", user_id=current_user.id))