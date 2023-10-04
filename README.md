# CLIMBUNITY - DEVOPS EDITION!
### ACS-3220 Final Project
Created by Mark Rattle, 2023

Climbunity is a backend project created in Python using Flask, SQLAlchemy and Jinja.

There is a live version [deployed here, on Render!](https://energeist-climbunity.onrender.com/)
ERD for the application [can be found here](https://github.com/energeist/climbunity/blob/master/climbunity-erd.pdf)

This application features User creation and authentication, CRUD routes for Venue/Route/Ascent/Appointment models and displays relevant data.

## Instructions to run locally: 
- Clone this repository
- Navigate to the cloned repository locally
- With the Docker engine installed:
  - Run `docker compose build && docker compose up -d` in your terminal, or `sudo docker compose build && sudo docker compose up -d` if you require sudo permissions.
- Open the app either by clicking the link in your terminal, or by navigating to `localhost:5002/`
- Create an account, set some routes and add to your tick list!
