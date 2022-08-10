from datetime import datetime  # To set date and time
import time
import os
import re

stop_threads = False


def isValidTime(time):
    regex = "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
    p = re.compile(regex)
    if time == "":
        return False
    m = re.search(p, time)

    if m is None:
        return False
    else:
        return True


def alarm_start():
    #  try for the path
    if os.path.isfile('user_alarm_set.txt'):
        try:
            fp = open('user_alarm_set.txt', 'r')
            user_time = fp.read()
            fp.close()
        except FileNotFoundError:
            print("Please check the path")
    else:
        user_time = '10:10'

    #  check for correct format
    if isValidTime(user_time):
        t = time.strptime(user_time, "%H:%M")
        alarm_time = time.strftime("%I:%M:%S %p", t)
        print(f"Setting alarm for {alarm_time}...")
    else:
        alarm_time = '10:10:10 AM'
        print(f"Setting alarm for {alarm_time}...")

    alarm_hour = alarm_time[0:2]
    alarm_min = alarm_time[3:5]
    alarm_sec = alarm_time[6:8]
    alarm_period = alarm_time[9:].upper()
    print(datetime.now())
    while True:
        if stop_threads:
            break
        now = datetime.now()

        current_hour = now.strftime("%I")
        current_min = now.strftime("%M")
        current_sec = now.strftime("%S")
        current_period = now.strftime("%p")

        if alarm_period == current_period:
            if alarm_hour == current_hour:
                if alarm_min == current_min:
                    if alarm_sec == current_sec:
                        print("Wake Up!")
                        break
    print("Stop!")
