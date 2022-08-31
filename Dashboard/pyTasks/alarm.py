import Dashboard.service
from Dashboard import datetime, time, re, os
from Dashboard.service import readJsonValueFromKey, MODE, power_supply_amp_, signal_generator_, MODE_RUNNING
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
    filePath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_settings')) + "/application_data.json"
    user_time = readJsonValueFromKey("USER_ALARM", filePath)

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
    if not stop_threads:
        power_supply_amp_("ON")
        signal_generator_("POWER_ON")
        time.sleep(30)
        Dashboard.service.MODE_RUNNING = False
        while MODE_RUNNING:
            time.sleep(0.02)
        MODE("ON")  # for how long
        time.sleep(float(readJsonValueFromKey("USER_TIMER", filePath)) * 60)
        while MODE_RUNNING:
            time.sleep(0.02)
        MODE("OFF")
    print("Alarm stop")
