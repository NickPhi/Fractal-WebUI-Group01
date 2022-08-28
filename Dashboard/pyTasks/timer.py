from Dashboard import time
from Dashboard.service import readJsonValueFromKey
import datetime
stop_threads = False


def timer_start():
    global stop_threads
    user_time = readJsonValueFromKey("USER_TIMER")
    total_seconds = float(user_time) * 60

    while total_seconds > 0:
        if stop_threads:
            break
        timer = datetime.timedelta(seconds=total_seconds)
        print(timer)
        time.sleep(1)
        total_seconds -= 1

    print("Timer Stop")