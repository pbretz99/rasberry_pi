'''Biking notification script

This is a script that sends me an email remind me to 
bike if the weather forecast is good and my schedule 
is open.
'''

# Libraries
import json
import requests
import time
from datetime import datetime

import Emails      # Code containing functions for sending emails
import Secure_Data # Code containing my personal information

# Set parameters for when I might want to bike
max_forecast = 24        # Only look at forecasts less than 12 hours away
min_temp = 55            # Temperatures higher than 55 degrees F
max_wind_speed = 15      # Wind speeds below 15 mph
# Available times, by day
available_times = {
    "Monday": [],
    "Tuesday": ["12:30-17:00"],
    "Wednesday": ["09:30-11:30", "15:00-17:00"],
    "Thursday": ["11:00-14:00"],
    "Friday": ["08:00-17:00"],
    "Saturday": ["08:00-17:00"],
    "Sunday": ["08:00-17:00"]
}
# Codes for inclement weather (from Open Weather Map)
bad_weather_codes = ["Drizzle", "Rain", "Snow", "Thunderstorm"]

# Get forecast data
# Note: uses variables from Secure_Data
api_key = Secure_Data.APIKEY    # string: API key for Open Weather Map
lat = Secure_Data.LAT           # string: latitude of desired location
lon = Secure_Data.LON           # string: longitude of desired location
url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=imperial" % (lat, lon, api_key)
response = requests.get(url)
forecast_data = json.loads(response.text)

# Utility function, determines if time is in interval of the form "HR:MN-HR:MN"
def time_in_interval(time, interval):
     in_interval = False
     interval = interval.split("-")
     start_time = time.replace(hour=int(interval[0].split(":")[0]),
                               minute=int(interval[0].split(":")[1]),
                               second=0)
     end_time = time.replace(hour=int(interval[1].split(":")[0]),
                             minute=int(interval[1].split(":")[1]),
                             second=0)
     if time >= start_time and time <= end_time:
          in_interval = True
     return in_interval        

# Returns True if time and forecast fit my conditions
def is_good_time(time_stamp, temp, wind_speed, weather):
     time = datetime.fromtimestamp(time_stamp)
     week_day = time.strftime("%A")
     time_intervals = available_times[week_day]
     good_time = True
     any_availability = False
     for interval in time_intervals:
          if time_in_interval(time, interval):
               any_availability = True
     if not any_availability:
          good_time = False
     if temp <= min_temp:
          good_time = False
     if wind_speed >= max_wind_speed:
          good_time = False
     if weather in bad_weather_codes:
          good_time = False
     return good_time

# Get current timestamp
current_time = int(time.time())
# Loop through hourly forecasts to find and save good times for biking
biking_times = []
forecast_temps, forecast_wind_speeds = [], []
for entry in forecast_data["hourly"]:
     forecast_time = entry["dt"]
     time_til = round((forecast_time - current_time) / (60 * 60), 1)
     if time_til >= 0 and time_til <= max_forecast:
          temp = entry["temp"]
          wind_speed = entry["wind_speed"]
          weather = entry["weather"][0]["main"]
          if is_good_time(forecast_time, temp, wind_speed, weather):
               biking_times.append(forecast_time)
               # Save temperature and wind speed
               forecast_temps.append(temp)
               forecast_wind_speeds.append(wind_speed)

# Utility function, makes time interval into a string
def make_interval_string(start, end):
     start_time = datetime.fromtimestamp(start).strftime("%H")
     start_time += ":" + datetime.fromtimestamp(start).strftime("%M")
     end_time = datetime.fromtimestamp(end).strftime("%H")
     end_time += ":" + datetime.fromtimestamp(end).strftime("%M")
     return start_time + " to " + end_time

# If there are any time intervals that work for biking, record them and send via email
if biking_times and len(biking_times) > 1:
     # Get a list of all the time intervals that work
     biking_time_intervals = []
     start = biking_times[0]
     for i in range(1, len(biking_times)):
          if biking_times[i] - biking_times[i-1] == 60*60:
               # Keep extending interval
               end = biking_times[i]
          else:
               # Record interval, start new one
               biking_time_intervals.append(make_interval_string(start, end))
               start = biking_times[i]
     if start < end:
          # Save last interval, if applicable
          biking_time_intervals.append(make_interval_string(start, end))
     # Send an email with all the good time intervals, the coldest temp, and highest wind speed
     temp, wind_speed = round(min(forecast_temps)), round(max(forecast_wind_speeds))
     Emails.send_biking_email(biking_time_intervals, temp, wind_speed)
