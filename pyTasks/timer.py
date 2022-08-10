import time
import datetime
import os

stop_threads = False


def timer_start():
    global stop_threads
    #  try for the path
    if os.path.isfile('user_timer_set.txt'):
        try:
            fp = open('user_timer_set.txt', 'r')
            user_time = fp.read()
            fp.close()
        except FileNotFoundError:
            print("Please check the path")
    else:
        user_time = '5'

    total_seconds = float(user_time) * 60
    while total_seconds > 0:
        if stop_threads:
            break
        timer = datetime.timedelta(seconds=total_seconds)
        print(timer)
        time.sleep(1)
        total_seconds -= 1

    print("Timer Stop")
