from Dashboard import time, os
from Dashboard.service import readJsonValueFromKey, MODE
import datetime
stop_threads = False


def timer_start():
    global stop_threads
    filePath = os.path.abspath(os.curdir) + "/Dashboard/_settings/application_data.json"
    user_time = readJsonValueFromKey("USER_TIMER", filePath)
    total_seconds = float(user_time) * 60
    MODE("ON")

    while total_seconds > 0:
        if stop_threads:
            break
        timer = datetime.timedelta(seconds=total_seconds)
        print(timer)
        time.sleep(1)
        total_seconds -= 1

    MODE("OFF")
    print("Timer Stop")