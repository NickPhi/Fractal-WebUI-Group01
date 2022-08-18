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
USER_GROUP = "01"  # temp remove for production
USER_NAME = "01_001"  # temp remove for production
ADMIN_EMAIL = "null"
EM_DATA = "pos.device.email.1@gmail.com"  # temp remove for production
PS_DATA = "inqtysziizuofirt"  # temp remove for production
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
    global PATH, USER_GROUP, USER_NAME, ADMIN_EMAIL, AUTHENTICATION, UPDATE_GROUP_OR_USER, \
        GROUP_VERSION, USER_VERSION, GIT_GROUP, GIT_USER, COMMAND, EM_DATA, PS_DATA

    # get_data() aasdf
    if wifi_check():
        download_variables()
        if user_authentication():
            # for testing purposes get string variables
            test_string = "Path=" + PATH + " | " + "User Group=" + USER_GROUP + " | " + "Username=" + USER_NAME + " | " \
                          + "Admin email=" + ADMIN_EMAIL + " | " + "Authentication=" + AUTHENTICATION + " | " + \
                          "Group or user=" + UPDATE_GROUP_OR_USER + " | " + "Group version=" + GROUP_VERSION + " | " + \
                          "User version=" + USER_VERSION + " | " + "Git Group=" + GIT_GROUP + " | " + "Git user=" + \
                          GIT_USER + " | " + "Command=" + COMMAND + " | " + "EM=" + EM_DATA + " | " + "PS=" + PS_DATA
            # update_check()
            return render_template('index.html', response=test_string)
        else:
            print("authentication failed")  # Start new thread
            restart_15()
            return render_template('payment.html')
        # It will cycle so best to turn itself off than restart
    else:
        return render_template('wifi.html', response="failed index wifi check")


@app.route('/turnon')
def turnon():
    return "works"


@app.route('/turnoff')
def turnoff():
    return "works"


@app.route('/settings.html')
def settings():
    return render_template("settings.html")


def user_authentication():
    print("User Authentication check")
    global AUTHENTICATION
    if AUTHENTICATION == '1':
        print("Pass")
        return True
    else:
        print("FAIL")
        return False


def update_check():
    print("Update Start")
    global UPDATE_GROUP_OR_USER, GROUP_VERSION, USER_VERSION, \
        GIT_GROUP, GIT_USER
    if UPDATE_GROUP_OR_USER == "0":  # Group Update
        # Get current version
        current_version = readJsonValueFromKey("GROUP_UPDATE_VERSION")
        if int(current_version) < int(GROUP_VERSION):
            # Compare current version and gathered version
            print("Updating version: group")
            # write all required information to the file
            write_update(GIT_GROUP, GROUP_VERSION)
            # update version number
            updateJsonFile("GROUP_UPDATE_VERSION", GROUP_VERSION)
            # restart_15()
            return render_template('system_reboot.html', response='Updated group version to ' + GROUP_VERSION)
    else:  # User Update
        current_version = readJsonValueFromKey("USER_UPDATE_VERSION")
        if int(current_version) < int(USER_VERSION):
            print("Updating version: user")
            # write all required information to the file
            write_update(GIT_USER, USER_VERSION)
            # lastly update version number
            updateJsonFile("GROUP_UPDATE_VERSION", USER_VERSION)
            # restart_15()
            return render_template('system_reboot.html', response='Updated user version to ' + USER_VERSION)


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


def email_send(text):
    global EM_DATA, PS_DATA
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = EM_DATA
    receiver_email = EM_DATA
    password = PS_DATA
    message = text

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    print("email sent")
    # generate error id


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


def wifi_check():
    print("internet check")
    try:
        req = requests.get('http://clients3.google.com/generate_204')
        if req.status_code != 204:
            req = requests.get('ghttp://google.com/')
            if req != 200:
                return False
            else:  # double check
                return True
        else:
            return True
    except:
        print("internet issue")
        # render error message
        return False


@app.route('/wifi.html', methods=['GET', 'POST'])
def wifi():
    if request.method == 'GET':
        return render_template('wifi.html', response="simple GET command")
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
    return render_template('system_reboot.html', response="wifi entered now rebooting")


@app.route('/timer_settings', methods=['GET', 'POST'])
def timer_settings():
    if request.method == 'GET':
        return render_template('timer_settings.html')
    if request.method == 'POST':
        data = request.form
        updateJsonFile('USER_TIMER', data['set-time'])
        return render_template('index.html', response="timer settings set")


@app.route('/alarm_settings', methods=['GET', 'POST'])
def alarm_settings():
    if request.method == 'GET':
        return render_template('alarm_settings.html')
    if request.method == 'POST':
        data = request.form
        updateJsonFile('USER_ALARM', data['set-time'])
        return render_template('index.html', response="alarm settings set")


# if the program was turned off in the middle of writing to a file?


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


def restart_15():
    t3 = threading.Thread(target=restart)
    t3.start()


def restart():
    time.sleep(15)
    os.system('sudo reboot now')
    # try, catch, kill thread, display error


def run_this_command():  # works
    print("running command")
    global COMMAND
    if COMMAND != '0':
        print("command ran")
        os.system(COMMAND)


def updateJsonFile(Key, Value):
    jsonFile = open(os.path.dirname(os.path.abspath(__file__)) + "/application_data.json", "r")
    data = json.load(jsonFile)  # Read the JSON into the buffer
    jsonFile.close()
    # Update Key & Value a
    data[Key] = Value
    # Save changes to JSON file
    jsonFile = open(os.path.dirname(os.path.abspath(__file__)) + "/application_data.json", "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()


def readJsonValueFromKey(Key):
    f = open(os.path.dirname(os.path.abspath(__file__)) + "/application_data.json")
    data = json.load(f)
    f.close()
    return data[Key]


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
# try everything so if there is errors
#
