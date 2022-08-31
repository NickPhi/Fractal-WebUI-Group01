from Dashboard import time, os
from Dashboard.service import readJsonValueFromKey, MODE, MODE_RUNNING
import datetime
stop_threads = False


def timer_start():
    while MODE_RUNNING:
        time.sleep(0.02)
    MODE("ON")
    global stop_threads
    stop_threads = False
    filePath = os.path.abspath(os.curdir) + "/Fractal-WebUI-Group01/Dashboard/_settings/application_data.json"
    user_time = readJsonValueFromKey("USER_TIMER", filePath)
    total_seconds = float(user_time) * 60

    while total_seconds > 0:
        if stop_threads:
            break
        timer = datetime.timedelta(seconds=total_seconds)
        print(timer)
        time.sleep(1)
        total_seconds -= 1
    if not stop_threads:
        while MODE_RUNNING:
            time.sleep(0.02)
        MODE("OFF")
        print("worked")
    print("Timer Stop")
