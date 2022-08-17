import os
import smtplib
import ssl
import threading
import time
import json

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
PATH = "https://metacafebliss.com/deep/users/"
PATH_ALT = "https://metacafebliss.com/deep/"
USER_GROUP = "01"
USER_NAME = "01_001"
ADMIN_EMAIL = "null"
EM_DATA = "null"
PS_DATA = "null"
AUTHENTICATION = "null"
UPDATE_GROUP_OR_USER = "null"
GROUP_VERSION = "null"
USER_VERSION = "null"
GIT_GROUP = "null"
GIT_USER = "null"
COMMAND = "null"


# GLOBALS


@app.route('/')
def index():
    get_data()
    if wifi_check():
        download_variables()
        if user_authentication():
            return render_template('index.html')
        else:
            print("authentication failed")  # Start new thread
            t3 = threading.Thread(target=restart_15)
            t3.start()
            return render_template('payment.html')
    else:
        return render_template('wifi.html')


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


def wifi_check():
    print("internet check")
    try:
        req = requests.get('http://clients3.google.com/generate_204')
        if req.status_code != 204:
            req = requests.get('http://google.com/')
            if req != 200:
                return False
            else:  # double check
                return True
        else:
            return True
    except:
        print("internet issue")
        return False


def download_variables():
    global PATH, USER_GROUP, USER_NAME, ADMIN_EMAIL, AUTHENTICATION, UPDATE_GROUP_OR_USER, \
        GROUP_VERSION, USER_VERSION, GIT_GROUP, GIT_USER, COMMAND
    req = requests.get(PATH + USER_NAME + '/user_settings.json')
    gru = requests.get(PATH_ALT + USER_GROUP + '/group.json')
    j_ = req.json()
    i_ = gru.json()
    ADMIN_EMAIL = j_['ADMIN_EMAIL']
    AUTHENTICATION = j_['AUTHENTICATION']
    UPDATE_GROUP_OR_USER = j_['UPDATE_GROUP_OR_USER']
    GROUP_VERSION = i_['GROUP_VERSION']
    USER_VERSION = j_['USER_VERSION']
    GIT_GROUP = i_['GIT_GROUP']
    GIT_USER = j_['GIT_USER']
    COMMAND = j_['COMMAND']


def user_authentication():
    print("User Authentication check")
    global AUTHENTICATION
    if AUTHENTICATION == '1':
        print("Pass")
        return True
    else:
        print("FAIL")
        return False


@app.route('/wifi.html', methods=['GET', 'POST'])
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
                'auto lo\n' + \
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
    restart_15()
    return render_template('system_reboot.html')


def update_check():
    print("Update Start")
    global UPDATE_GROUP_OR_USER, GROUP_VERSION, USER_VERSION, \
        GIT_GROUP, GIT_USER
    if UPDATE_GROUP_OR_USER == "0":  # Group Update
        # Get current version
        fp = open('version_group.txt', 'r')
        current_version = fp.read()
        fp.close()
        if int(current_version) < int(GROUP_VERSION):
            # Compare current version and gathered version
            print("Updating version: group")
            # write all required information to the file
            write_update(GIT_GROUP, GROUP_VERSION)
            # lastly update version number
            fp = open('version_group.txt', 'w')
            fp.write(GROUP_VERSION)
            fp.close()
            restart_15()
            return render_template('system_reboot.html')
    else:  # User Update
        fp = open('version_user.txt', 'r')
        current_version = fp.read()
        fp.close()
        if int(current_version) < int(USER_VERSION):
            print("Updating version: user")
            # write all required information to the file
            write_update(GIT_USER, GROUP_VERSION)
            # lastly update version number
            fp = open('version_group.txt', 'w')
            fp.write(GROUP_VERSION)
            fp.close()
            restart_15()
            return render_template('system_reboot.html')


def write_update(git, version_num):
    os.system('cd')
    os.system('git clone ' + git)
    s_list = git.split("/")
    prj_name = s_list[4]  # Assuming git URL separated 5 times by "/"
    with open('/lib/systemd/system/webserver.service', 'w') as file:
        content = \
            '''
            [Unit]
            Description=WebServer
            After=multi-user.target

            [Service]
            Environment=DISPLAY=:0.0
            Environment=XAUTHORITY=/home/pi/.Xauthority
            Type=simple
            ExecStart=/usr/bin/python3 /home/pi/''' + prj_name + version_num + '''/app.py
            Restart=on-abort
            User=pi
            Group=pi

            [Install]
            WantedBy=multi-user.target    
            '''
        file.write(content)


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


# if the program was turned off in the middle of writing to a file?

def restart_15():
    time.sleep(15)
    os.system('sudo reboot now')


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


def get_data():
    global USER_GROUP, USER_NAME, EM_DATA, PS_DATA
    f = open('home/pi/data.json')
    data = json.load(f)
    f.close()
    # Load Main User Data
    USER_GROUP = data['USER_GROUP']
    USER_NAME = data['USER_NAME']
    EM_DATA = data['EM_DATA']
    PS_DATA = data['PS_DATA']


def run_this_command():
    global COMMAND
    if COMMAND != 0:
        os.system(COMMAND)


if __name__ == "__main__":
    app.run(debug=True)

# Notes to self:
# check all css/js links for any that need internet and download them
# check for corrupted files?
# try everything so if there is errors
#
