# CLIMBUNITY - DEVOPS EDITION!
### ACS-3220 Final Project
Created by Mark Rattle, 2023

Climbunity is a backend project created in Python using Flask, SQLAlchemy and Jinja.
Containerized and [hosted on Docker Hub.](https://hub.docker.com/repository/docker/energeist/climbunity/general)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/energeist/climbunity)

There is a live version [deployed here, on Caprover!](https://caprover-climbunity.dev.greatwith.tech/)

Uptime Status of the Climbunity deployment is [monitored by UptimeRobot](https://stats.uptimerobot.com/4jmZ3HYloO)
![Uptime Robot status](https://img.shields.io/uptimerobot/status/m795415683-c484a4881d311338f5cb1c0d)

ERD for the application [can be found here](https://github.com/energeist/climbunity/blob/master/climbunity-erd.pdf)

This application features User creation and authentication, CRUD routes for Venue/Route/Ascent/Appointment models and displays relevant data.

## Instructions to run locally: 
- Clone this repository
- Navigate to the cloned repository locally
- With the Docker engine installed:
  - Run `docker compose up -d` in your terminal, or `sudo docker compose up -d` if you require sudo permissions.
- Open the app either by clicking the link in your terminal, or by navigating to `localhost:5002/`
- Create an account, set some routes and add to your tick list!


