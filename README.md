NAME
    Continuous Assessment 3

PREREQUISITES
    The user should input the api-keys into the config.json file ('insert api-keys here')
    Have pyhton 3.0 or above
    For this module, you should install:
    - import time
    - import json
    - import sched
    - import logging
    - import pyttsx3
    - import requests
    - from flask 
    - from requests
    - from newsapi import NewsApiClient

GETING STARTED TUTORIAL
    Introduce the api-keys in the json.file, choose the UK country for the covid cases function and select the place or city where you
    would like to know the weather infromation. Go to the assessment.py file and run it, enter the website from the sys.log file

DESCRIPTION
    An alarm clock that can access information about the COVID infection rate
    and provide scheduled updates about the weather and the news

FUNCTIONS
    announce(announcement, type_alarm)
        this function announce the content of the alarm

    controller()
        it is the main function that controlls allthe actions in the program,
        adding and deleting alarms, or adding notifications

    conversion_to_time(alarm: str)
        converts time so that it can be entered into the enterabs

    delete(name, list_notif)
        this deletes the notification dictionary from the notifications list

    deletealarm(dictionary, item)
        this deletes the alarm from the dictionary of alarms

    get_newcases()
        gets the covid information from the url

    get_news()
        this function gets the news from the api

    get_weather()
        gets the weather information from the url

    nation_identifier()
        identifies the nation that the user chose in the config.jason file

    new_notifications()
        this creates a list of notifications that are restored every 6 hours

    tests() -> None
        this functions test other functions from the main file

DATA
    alarms = {}
    all_notifications = [{'content': "In Exeter, on a scattered clouds day...
    app = <Flask 'assessment'>
    engine = <pyttsx3.engine.Engine object>
    notifications = [{'content': "In Exeter, on a scattered clouds day it'...
    request = <LocalProxy unbound>
    s = <sched.scheduler object>
