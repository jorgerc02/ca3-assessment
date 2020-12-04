"""An alarm clock that can access information about the COVID infection rate
and provide scheduled updates about the weather and the news"""
import time
import json
import sched
import logging
import pyttsx3
import requests
from flask import Flask, request, render_template
from requests import get
from newsapi import NewsApiClient

def get_newcases():
    """ gets the covid information from the url"""
    with open('config.json', 'r') as file:
        x_file = json.load(file)
        nation = x_file["cases"]["nation"]

    def get_data(url):
        response = get(url, timeout=10)

        if response.status_code >= 400:
            raise RuntimeError(f'Request failed: { response.text }')

        return response.json()
    endpoint = (
        'https://api.coronavirus.data.gov.uk/v1/data?'
        'filters=areaType=nation;areaName='+ nation+'&'
        'structure={"date":"date","NewCases":"newCasesByPublishDate","rate":"cumCasesBySpecimenDateRate"}'
    )

    data = get_data(endpoint)
    x_file = data["data"]
    new_cases = str(x_file[0]['NewCases'])
    rate = str(x_file[1]['rate'])
    return 'New cases: '+new_cases+' \nRate of cumulative cases per 100k resident population: '+rate

def nation_identifier():
    """identifies the nation that the user chose in the config.jason file"""
    with open('config.json', 'r') as file:
        x_file = json.load(file)
        nation = x_file["cases"]["nation"]
    return nation


def get_news():
    """this function gets the news from the api"""
    headlines = []
    with open('config.json', 'r') as file:
        news = json.load(file)
        api_key = news["news"]["api_key"]
        country = news["news"]["country"]
        language = news["news"]["language"]

    newsapi = NewsApiClient(api_key=api_key)

    top_headlines = newsapi.get_top_headlines(language=language,
                                              country = country)

    for article in top_headlines['articles']:
        headlines.append(article['title'])
        titles = str(headlines).replace('[','').replace(']','')
    return titles

def get_weather():
    """ gets the weather information from the url"""
    with open('config.json', 'r') as file:
        weather = json.load(file)
        api_key = weather["weather"]["api_key"]
        base_url = weather["weather"]["base_url"]
        place = weather["weather"]["place"]
    complete_url = base_url + "appid=" + api_key + "&q=" + place
    response = requests.get(complete_url)
    weather_response = response.json()

    items = weather_response["main"]
    air_temperature = round(items["temp"]-273.15, 2)
    feels_like = round(items["feels_like"]-273.15, 2)
    weather = weather_response["weather"]
    weather_description = weather[0]["description"]
    weather_name = weather_response["name"]
    first = 'In '+str(weather_name)+ ', '+'on a '+ str(weather_description)+" day it's "
    return first + str(air_temperature)+' degrees but it feels like '+str(feels_like)+' degrees.'


logging.basicConfig(filename= 'sys.log', encoding='utf-8', level=logging.DEBUG)
s = sched.scheduler(time.time, time.sleep)
app = Flask(__name__)
engine = pyttsx3.init()
alarms = {}
all_notifications = [{ 'title': 'Weather', 'content':get_weather() },{ 'title': 'Covid-19 cases in '+ nation_identifier(), 'content':get_newcases() },{'title': 'Today News', 'content': get_news() }]
notifications = []
def new_notifications():
    """this creates a list of notifications that are restored every 6 hours"""
    if all_notifications[0] not in notifications:
        notifications.append(all_notifications[0])
    if all_notifications[1] not in notifications:
        notifications.append(all_notifications[1])
    if all_notifications[2] not in notifications:
        notifications.append(all_notifications[2])
    s.enter(21600,1,new_notifications,())
new_notifications()


@app.route('/index')
@app.route('/')
def controller():
    """
    it is the main function that controlls allthe actions in the program,
    adding and deleting alarms, or adding notifications
    """
    s.run(blocking=False)
    alarm_time = request.args.get("alarm")
    alarm_name = request.args.get("two")
    notif = request.args.get('notif')
    alarm_item = request.args.get('alarm_item')
    news = request.args.get("news")
    weather = request.args.get("weather")

    if notif:
        #if the user presses the 'x' button on the notification
        logging.info(' notification deleted')
        delete(notif,notifications) #  eliminates the selected notifications from the list

    if alarm_time:
        #sets an alarm and introduce it into a dictionary of alarms
        logging.info('alarm set, and added to the alarm list')
        alarm_time_hhmm = alarm_time[-5:-3] + ':' + alarm_time[-2:]
        time1 = conversion_to_time(alarm_time)
        day = alarm_time[0:10]
        if weather and news:
            logging.info('the alarm has the weather and the news')
            action = s.enterabs(time1, 1, announce, (alarm_name,4))
        else:
            if weather:
                logging.info('the alarm has the weather information attached')
                action = s.enterabs(time1, 1, announce, (alarm_name,2))
            else:
                if news:
                    logging.info('the alarm has the news attached')
                    action = s.enterabs(time1, 1, announce, (alarm_name,3))
                else:
                    logging.info('alarm content only')
                    action = s.enterabs(time1, 1, announce, (alarm_name,1))
        form = {'title':'The day '+day+' you have an alarm at: '+alarm_time_hhmm,'content':alarm_name,'event': action}
        alarms[form['title']]= form


    if alarm_item:  #if the user presses the 'x' button on the alarm
        logging.info('the alarm has been deleted')
        deletealarm(alarms,alarm_item) # eliminates the selected alarm from the list

    return render_template('index.html', title='Daily update', notifications=notifications, image='alarm.jpg', alarms=alarms.values())


def announce(announcement,type_alarm):
    """this function announce the content of the alarm"""
    logging.info( 'The alarm has been said')
    if type_alarm == 1:
        engine.say(announcement)
    if type_alarm == 2:
        engine.say(announcement+';the weather ' + get_weather())
    if type_alarm ==3:
        engine.say(announcement+';the  news are;' + get_news())
    if type_alarm == 4:
        engine.say(announcement+'the weather is;'+ get_weather()+'and the news are;'+get_news() )
    engine.runAndWait()



def deletealarm(dictionary,item):
    """this deletes the alarm from the dictionary of alarms"""
    try:
        s.cancel(dictionary[item]['event'])
        del dictionary[item]
    except ValueError:
        logging.warning('The alarms has already been deleted')
        del dictionary[item]


def delete(name,list_notif):
    """this deletes the notification dictionary from the notifications list"""
    i = 0
    for item in list_notif:
        for notification_name in item.values():
            if notification_name == name:
                list_notif.pop(i)
        i += 1
    return list_notif

def conversion_to_time(alarm: str):
    """converts time so that it can be entered into the enterabs"""
    time_alarm = time.strptime(alarm + ":00", "%Y-%m-%dT%H:%M:%S")
    time1 = time.mktime(time_alarm)
    return time1

def tests() -> None:
    """this functions test other functions from the main file"""
    #check that it returns a string with the covid information
    assert isinstance(get_newcases()) == str, "get_newcases: FAILED"
    #check that it returns a string with the nation name
    assert isinstance(nation_identifier()) == str, "nation_identifier: FAILED"
    #check that it returns a string with the news
    assert isinstance(get_news()) == str, "get_news: FAILED"
    #check that it returns a string with the weather information
    assert isinstance(get_weather()) == str, "get_weather: FAILED"


if __name__ == '__main__':
    """It give NameError: name 'open' is not defined every time
    try:
        tests()
    except AssertionError as message:
        print(message)
    """
    app.run(debug=True)
