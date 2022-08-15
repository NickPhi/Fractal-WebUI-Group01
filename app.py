import os
import smtplib
import ssl
import threading
import time

import requests
from flask import Flask, render_template, request

import pyTasks.alarm
import pyTasks.timer

app = Flask(__name__)

#  GLOBALS
t1 = threading.Thread  # alarm thread
t2 = threading.Thread  # timer thread
timer_state = "null"  # Global Variable
alarm_state = "null"  # Global Variable


# GLOBALS


@app.route('/')
def index():
    if wifi_connected():
        if user_authentication():
            return render_template('index.html')
        else:
            print("u outta luck")
            os.system('sudo reboot now')
    else:
        return render_template('wifi.html')


def user_authentication():
    print("User Authentication check")
    username = "myPI1"
    req = requests.get('http://metacafebliss.com/deep/users.html')
    approve1 = req.text
    if approve1.__contains__(username):
        print("Pass")
        return True
    else:
        print("FAIL")
        return False


@app.route('/turnon')
def turnon():
    return "works"


@app.route('/turnoff')
def turnoff():
    return "works"


@app.route('/settings.html')
def settings():
    return render_template("settings.html")


@app.route('/timer_settings', methods=['GET', 'POST'])
def timer_settings():
    if request.method == 'GET':
        return render_template('timer_settings.html')
    if request.method == 'POST':
        data = request.form
        fp = open('user_timer_set.txt', 'w')
        fp.write(data['set-time'])
        fp.close()
        return render_template('index.html')


@app.route('/alarm_settings', methods=['GET', 'POST'])
def alarm_settings():
    if request.method == 'GET':
        return render_template('alarm_settings.html')
    if request.method == 'POST':
        data = request.form
        fp = open('user_alarm_set.txt', 'w')
        fp.write(data['set-time'])
        fp.close()
        return render_template('index.html')


def wifi_connected():
    print("internet check")
    req = requests.get('http://clients3.google.com/generate_204')
    if req.status_code != 204:
        req = requests.get('http://google.com/')
        if req != 200:
            return False
        else:  # double check
            return True
    else:
        return True


@app.route('/wifi', methods=['GET', 'POST'])
def wifi():
    if request.method == 'GET':
        return render_template('wifi.html')
    if request.method == 'POST':
        data = request.form
        ssid = data['wifi_ssid']
        password = data['wifi_pass']
        with open('/etc/network/interfaces', 'w') as file:
            content = \
                'source-directory /etc/network/interfaces.d\n\n' + \
                'auto lo\n\n' + \
                'iface lo inet loopback\n' + \
                "iface eth0 inet dhcp\n" + \
                'allow-hotplug wlan0\n' + \
                'auto wlan0\n' + \
                'auto wlan0\n' + \
                'iface wlan0 inet dhcp\n' + \
                'wpa-ssid "' + ssid + '"\n' + \
                'wpa-psk "' + password + '"\n'
            file.write(content)
    print("Write successful. Rebooting now.")
    time.sleep(2)
    os.system('sudo reboot now')


def update_check():
    req = requests.get('http://clients3.google.com/generate_204')
    revision_number = req.text
    fp = open('user_alarm_set.txt', 'r')
    current_revision = fp.read()
    fp.close()
    # compare the revision number
    # if new revision number
    # git clone PyApp
    # rename PyApp to PyApp-1
    # edit service file..
    # sudo reboot
    return


def git_clone():
    # git clone ..
    # rename
    return


def edit_service_file(version):
    # cd /lib/systemd/system/
    # sudo nano webserver.service
    return


# if the program was turned off in the middle of writing to a file?


def send_email():
    try:
        port = 587  # For starttls
        smtp_server = "smtp.gmail.com"
        sender_email = "my@gmail.com"
        receiver_email = "your@gmail.com"
        password = input("Type your password and press enter:")
        message = """\
        Subject: Hi there
    
        This message is sent from Python."""

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
    except:
        abc = 1


@app.route('/alarm')
def alarm():
    global alarm_state
    if alarm_state == "ON":
        alarm_thread("stop")
        alarm_state = "OFF"
    elif alarm_state == "OFF":
        alarm_thread("start")
        alarm_state = "ON"
    else:  # Initialization
        alarm_thread("start")
        alarm_state = "ON"
    return "works"


@app.route('/timer')
def timer():
    global timer_state
    if timer_state == "ON":
        timer_thread("stop")
        timer_state = "OFF"
    elif timer_state == "OFF":
        timer_thread("start")
        timer_state = "ON"
    else:  # Initialization
        timer_thread("start")
        timer_state = "ON"
    return "works"


def timer_thread(mode):
    global t2
    if mode == "start":
        pyTasks.timer.stop_threads = False
        t2 = threading.Thread(target=pyTasks.timer.timer_start)
        t2.start()
    if mode == "stop":
        time.sleep(0.1)
        pyTasks.timer.stop_threads = True
        t2.join()


def alarm_thread(mode):
    global t1
    if mode == "start":
        pyTasks.alarm.stop_threads = False
        t1 = threading.Thread(target=pyTasks.alarm.alarm_start)
        t1.start()
    if mode == "stop":
        time.sleep(0.1)
        pyTasks.alarm.stop_threads = True
        t1.join()


if __name__ == "__main__":
    app.run(debug=True)

# Notes to self:
# check all css/js links for any that need internet and download them
# check for corrupted files?
#
#
