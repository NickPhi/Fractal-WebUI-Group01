from Dashboard import datetime, time, re
from Dashboard.service import readJsonValueFromKey
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
    user_time = readJsonValueFromKey("USER_ALARM")

    #  check for correct format
    if isValidTime(user_time):
        t = time.strptime(user_time, "%H:%M")
        alarm_time = time.strftime("%I:%M:%S %p", t)
        print("Setting alarm for " + alarm_time)
    else:
        alarm_time = '10:10:10 AM'
        print("Setting alarm for " + alarm_time)

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
    print("Alarm stop")