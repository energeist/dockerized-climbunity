import os
from os.path import exists
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from climbunity_app.utils import FormEnum
from climbunity_app.models import *
from climbunity_app.auth.forms import *

from climbunity_app.extensions import app, db, bcrypt

auth = Blueprint("auth", __name__)

##########################################
#           Routes                       #
##########################################

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password,
            email = form.email.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            address = form.address.data,
            has_gear = form.has_gear.data,
            is_admin = False
        )
        db.session.add(user)
        db.session.commit()
        for style in form.climber_styles.data:
            user.user_does_styles.append(style)
        db.session.commit()
        flash('Account Created.')
        login_user(user, remember=True)
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('main.homepage'))
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('main.homepage'))
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))