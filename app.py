import os
import smtplib
import ssl
import threading
import time
import json
import subprocess
from datetime import date
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
ON_start = 0
ON_end = 0
XPATH = '/home/pi/'  # Path to /data.json
PATH = "https://metacafebliss.com/deep/users/"
PATH_ALT = "https://metacafebliss.com/deep/"
USER_GROUP = "01"  # temp remove for production
USER_NAME = "01_001"  # temp remove for production
ADMIN_EMAIL = "null"
ADMIN_PHONE = "null"
EM_DATA = "analytics@metacafebliss.com"  # temp remove for production
PS_DATA = ""  # temp remove for production
AUTHENTICATION = "null"
UPDATE_GROUP_OR_USER = "null"
GROUP_VERSION = "null"
USER_VERSION = "null"
GIT_GROUP = "null"
GIT_USER = "null"
COMMAND = "null"
SEND_ACTIVE_UPDATES = "null"


# GLOBALS

# if index is refreshed it may keep threads running may want to kill them unless index will never refresh
@app.route('/')
def index():
    global PATH, USER_GROUP, USER_NAME, ADMIN_EMAIL, AUTHENTICATION, UPDATE_GROUP_OR_USER, \
        GROUP_VERSION, USER_VERSION, GIT_GROUP, GIT_USER, COMMAND, EM_DATA, PS_DATA, SEND_ACTIVE_UPDATES, ADMIN_PHONE

    if wifi_check():
        download_variables()
        updateDayAnalytics("IP", str(getPublicIP()))
        if user_authentication():
            # for testing purposes get string variables
            test_string = "Path=" + PATH + " | " + "User Group=" + USER_GROUP + " | " + "Username=" + USER_NAME + " | " \
                          + "Admin email=" + ADMIN_EMAIL + " | " + "Authentication=" + AUTHENTICATION + " | " + \
                          "Group or user=" + UPDATE_GROUP_OR_USER + " | " + "Group version=" + GROUP_VERSION + " | " + \
                          "User version=" + USER_VERSION + " | " + "Git Group=" + GIT_GROUP + " | " + "Git user=" + \
                          GIT_USER + " | " + "Command=" + COMMAND + " | " + "EM=" + EM_DATA + " | " + "PS=" + PS_DATA \
                          + " | " + "active updates=" + SEND_ACTIVE_UPDATES

            # update_check()
            return render_template('index.html', response=test_string)
        else:
            print("authentication failed")  # Start new thread
            restart_15()
            return render_template('payment.html', response=ADMIN_EMAIL)
        # It will cycle so best to turn itself off than restart
    else:
        return render_template('wifi.html')


def system(mode):
    if mode == "ON":
        power_supply_amp_("ON")
        signal_generator_("POWER_ON")
        signal_generator_("LOAD")
        signal_generator_("SIGNAL_ON")
        speaker_protection_("POWER_ON")
    elif mode == "OFF":
        speaker_protection_("POWER_OFF")
        signal_generator_("SIGNAL_OFF")
        signal_generator_("UNLOAD")
        signal_generator_("POWER_OFF")
        power_supply_amp_("OFF")


def power_supply_amp_(mode):
    # Relay HIGH is off LOW is on
    if mode == "ON":
        os.system('gpioset 1 98=0')
    elif mode == "OFF":
        os.system('gpioset 1 98=1')


def signal_generator_(mode):
    # Relay HIGH is off LOW is on
    if mode == "POWER_ON":
        os.system('gpioset 1 98=0')
    elif mode == "POWER_OFF":
        os.system('gpioset 1 98=1')
    elif mode == "SIGNAL_ON":
        pass
        # output
    elif mode == "SIGNAL_OFF":
        pass
        # output off
    elif mode == "LOAD":
        pass
        # load waveform
    elif mode == "UNLOAD":
        pass
        # unload waveform


def speaker_protection_(mode):
    # Relay HIGH is off LOW is on
    if mode == "POWER_ON":
        os.system('gpioset 1 98=0')
    elif mode == "POWER_OFF":
        os.system('gpioset 1 98=1')


@app.route('/turnon')
def turnon():
    global ON_start, ON_end
    ON_start = time.time()
    system("ON")
    return "ON"


@app.route('/turnoff')
def turnoff():
    global ON_start, ON_end
    ON_end = time.time()
    print(ON_end - ON_start)
    system("OFF")
    return "OFF"


@app.route('/settings.html', methods=['GET', 'POST'])
def settings():
    global ADMIN_EMAIL, ADMIN_PHONE
    if request.method == 'GET':
        return render_template("settings.html", response=ADMIN_EMAIL + " " + ADMIN_PHONE)
    if request.method == 'POST':
        data = request.form
        if data["email"] != "":
            email_send(data["email"])
        return data


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
        GIT_GROUP, GIT_USER, XPATH
    if UPDATE_GROUP_OR_USER == "0":  # Group Update
        # Get current version
        current_version = readJsonValueFromKey("GROUP_UPDATE_VERSION")
        if int(current_version) < int(GROUP_VERSION):
            # Compare current version and gathered version
            print("Updating version: group")
            # write all required information to the file
            s_list = GIT_GROUP.split("/")
            prj_name = s_list[4]  # Assuming git URL separated 5 times by "/"
            NEW_PRJ_PATH = XPATH + prj_name + '_' + GROUP_VERSION  # USER_VERSION is a number
            write_update(GIT_GROUP, NEW_PRJ_PATH)
            # update Json file in new path
            updateJsonFile("GROUP_UPDATE_VERSION", GROUP_VERSION, NEW_PRJ_PATH + "/application_data.json")
            restart_15()
            return render_template('system_reboot.html', response='Updated group version to ' + GROUP_VERSION)
    else:  # User Update
        current_version = readJsonValueFromKey("USER_UPDATE_VERSION")
        if int(current_version) < int(USER_VERSION):
            print("Updating version: user")
            # git
            s_list = GIT_USER.split("/")
            prj_name = s_list[4]  # Assuming git URL separated 5 times by "/"
            NEW_PRJ_PATH = XPATH + prj_name + '_' + USER_VERSION  # USER_VERSION is a number
            write_update(GIT_USER, NEW_PRJ_PATH)
            # update Json file in new path
            updateJsonFile("USER_UPDATE_VERSION", USER_VERSION, NEW_PRJ_PATH + "/application_data.json")
            restart_15()
            return render_template('system_reboot.html', response='Updated user version to ' + USER_VERSION)


def write_update(git, NEW_PRJ_PATH):
    os.system('cd')
    os.system('git clone ' + git + ' ' + NEW_PRJ_PATH)
    with open('/lib/systemd/system/webserver.service', 'w') as file:
        content = \
            '''
            [Unit]
            Description=WebServer
            After=multi-user.target

            [Service]
            Environment=DISPLAY=:0.0
            Environment=XAUTHORITY=''' + XPATH + '''.Xauthority
            Type=simple
            ExecStart=/usr/bin/python3''' + ' ' + NEW_PRJ_PATH + '''/app.py
            Restart=on-abort
            User=pi
            Group=pi

            [Install]
            WantedBy=multi-user.target    
            '''
        file.write(content)


def email_send(text):
    global EM_DATA, PS_DATA
    port = 26
    smtp_server = "mail.metacafebliss.com"
    sender_email = EM_DATA
    receiver_email = EM_DATA
    password = PS_DATA
    message = text

    with smtplib.SMTP(smtp_server, port) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, \
                        '''
                        <html>
                        <head></head>
                        <body><h1>test</h1></body>
                        </html>
                        ''' + message)
    print("email sent")
    # generate error id


def download_variables():
    global PATH, USER_GROUP, USER_NAME, ADMIN_EMAIL, AUTHENTICATION, UPDATE_GROUP_OR_USER, \
        GROUP_VERSION, USER_VERSION, GIT_GROUP, GIT_USER, COMMAND, SEND_ACTIVE_UPDATES, ADMIN_PHONE
    usr = requests.get(PATH + USER_NAME + '/user_settings.json')
    gru = requests.get(PATH_ALT + USER_GROUP + '/group.json')
    j_ = usr.json()
    i_ = gru.json()
    ADMIN_EMAIL = j_['ADMIN_EMAIL']
    ADMIN_PHONE = j_['ADMIN_PHONE']
    AUTHENTICATION = j_['AUTHENTICATION']
    UPDATE_GROUP_OR_USER = j_['UPDATE_GROUP_OR_USER']
    SEND_ACTIVE_UPDATES = j_['SEND_ACTIVE_UPDATES']
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
    return render_template('system_reboot.html')


@app.route('/timer_settings', methods=['GET', 'POST'])
def timer_settings():
    if request.method == 'GET':
        return render_template('timer_settings.html')
    if request.method == 'POST':
        data = request.form
        filePath = os.path.dirname(os.path.abspath(__file__)) + "/application_data.json"
        updateJsonFile('USER_TIMER', data['set-time'], filePath)
        return render_template('index.html', response="timer settings set")


@app.route('/alarm_settings', methods=['GET', 'POST'])
def alarm_settings():
    if request.method == 'GET':
        return render_template('alarm_settings.html')
    if request.method == 'POST':
        data = request.form
        filePath = os.path.dirname(os.path.abspath(__file__)) + "/application_data.json"
        updateJsonFile('USER_ALARM', data['set-time'], filePath)
        return render_template('index.html', response="alarm settings set")


# if the program was turned off in the middle of writing to a file?


def get_data():
    global USER_GROUP, USER_NAME, EM_DATA, PS_DATA, XPATH
    f = open(XPATH + 'data.json')
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


def updateDayAnalytics(KEY, Value):  # updates current day and handles resets
    day_num = readJsonValueFromKey("DAY")
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/analytics.json"
    with open(filePath, 'r+') as file:
        file_data = json.load(file)
    if file_data["DATES"]["DAY" + day_num]["date"] == str(date.today()):
        updateAnalyticsByDay("DAY" + day_num, KEY, Value)
    else:
        if int(day_num) + 1 == 8:
            email_weekly_analytics(file_data)
            resetAnalytics()
            updateDayAnalytics(KEY, Value)
        else:
            updateJsonFile("DAY", str(int(day_num) + 1),
                           os.path.dirname(os.path.abspath(__file__)) + "/application_data.json")
            updateAnalyticsByDay("DAY" + str(int(day_num) + 1), "date", str(date.today()))
            updateAnalyticsByDay("DAY" + str(int(day_num) + 1), "IP", str(getPublicIP()))  # use internet
            updateDayAnalytics(KEY, Value)


def updateAnalyticsByDay(DAY, KEY, Value):
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/analytics.json"
    with open(filePath, 'r+') as file:
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["DATES"][DAY][KEY] = Value
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)


def resetAnalytics():
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/analytics.json"
    dictionary = {
        "DATES": {
            "DAY1": {
                "date": "null",
                "IP": "null",
                "total_times_used": "0",
                "minutes": "0",
                "alarms_used": "0",
                "timers_used": "0"
            },
            "DAY2": {
                "date": "null",
                "IP": "null",
                "total_times_used": "0",
                "minutes": "0",
                "alarms_used": "0",
                "timers_used": "0"
            },
            "DAY3": {
                "date": "null",
                "IP": "null",
                "total_times_used": "0",
                "minutes": "0",
                "alarms_used": "0",
                "timers_used": "0"
            },
            "DAY4": {
                "date": "null",
                "IP": "null",
                "total_times_used": "0",
                "minutes": "0",
                "alarms_used": "0",
                "timers_used": "0"
            },
            "DAY5": {
                "date": "null",
                "IP": "null",
                "total_times_used": "0",
                "minutes": "0",
                "alarms_used": "0",
                "timers_used": "0"
            },
            "DAY6": {
                "date": "null",
                "IP": "null",
                "total_times_used": "0",
                "minutes": "0",
                "alarms_used": "0",
                "timers_used": "0"
            },
            "DAY7": {
                "date": "null",
                "IP": "null",
                "total_times_used": "0",
                "minutes": "0",
                "alarms_used": "0",
                "timers_used": "0"
            }
        }
    }
    json_object = json.dumps(dictionary, indent=4)
    with open(filePath, "w") as outfile:
        outfile.write(json_object)
    updateJsonFile("DAY", "1", os.path.dirname(os.path.abspath(__file__)) + "/application_data.json")
    updateAnalyticsByDay("DAY1", "date", str(date.today()))


def readJsonValueFromKey(Key):
    f = open(os.path.dirname(os.path.abspath(__file__)) + "/application_data.json")
    data = json.load(f)
    f.close()
    return data[Key]


def updateJsonFile(Key, Value, filePath):
    jsonFile = open(filePath, "r")
    data = json.load(jsonFile)  # Read the JSON into the buffer
    jsonFile.close()
    # Update Key & Value
    data[Key] = Value
    # Save changes to JSON file
    jsonFile = open(filePath, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()


def getPublicIP():
    endpoint = 'https://ipinfo.io/json'
    response = requests.get(endpoint, verify=True)
    if response.status_code != 200:
        return 'Status:', response.status_code, 'Problem with the request. Exiting.'
    data = response.json()
    return data['ip']


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


def email_weekly_analytics(data):
    global USER_NAME
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "weekly_analytics " + USER_NAME
    msg['From'] = EM_DATA
    msg['To'] = EM_DATA

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi!\nHow are you?\nHere is the link you wanted:\n"
    html = """\
    <html>
      <head>User name: """ + USER_NAME + """</head>
      <body>
        <br><b>DAY1: </b><br> 
        date: """ + data["DATES"]["DAY1"]["date"] + """ <br>
        ip: """ + data["DATES"]["DAY1"]["IP"] + """ <br>
        total_times_used: """ + data["DATES"]["DAY1"]["total_times_used"] + """ <br>
        minutes: """ + data["DATES"]["DAY1"]["minutes"] + """ <br>
        alarms_used: """ + data["DATES"]["DAY1"]["alarms_used"] + """ <br>
        timers_used: """ + data["DATES"]["DAY1"]["timers_used"] + """ <br>
        <br><b>DAY2: </b><br> 
        date: """ + data["DATES"]["DAY2"]["date"] + """ <br>
        ip: """ + data["DATES"]["DAY2"]["IP"] + """ <br>
        total_times_used: """ + data["DATES"]["DAY2"]["total_times_used"] + """ <br>
        minutes: """ + data["DATES"]["DAY2"]["minutes"] + """ <br>
        alarms_used: """ + data["DATES"]["DAY2"]["alarms_used"] + """ <br>
        timers_used: """ + data["DATES"]["DAY2"]["timers_used"] + """ <br>
        <br><b>DAY3: </b><br> 
        date: """ + data["DATES"]["DAY2"]["date"] + """ <br>
        ip: """ + data["DATES"]["DAY2"]["IP"] + """ <br>
        total_times_used: """ + data["DATES"]["DAY2"]["total_times_used"] + """ <br>
        minutes: """ + data["DATES"]["DAY2"]["minutes"] + """ <br>
        alarms_used: """ + data["DATES"]["DAY2"]["alarms_used"] + """ <br>
        timers_used: """ + data["DATES"]["DAY2"]["timers_used"] + """ <br>
        <br><b>DAY4: </b><br> 
        date: """ + data["DATES"]["DAY2"]["date"] + """ <br>
        ip: """ + data["DATES"]["DAY2"]["IP"] + """ <br>
        total_times_used: """ + data["DATES"]["DAY2"]["total_times_used"] + """ <br>
        minutes: """ + data["DATES"]["DAY2"]["minutes"] + """ <br>
        alarms_used: """ + data["DATES"]["DAY2"]["alarms_used"] + """ <br>
        timers_used: """ + data["DATES"]["DAY2"]["timers_used"] + """ <br>
        <br><b>DAY5: </b><br> 
        date: """ + data["DATES"]["DAY2"]["date"] + """ <br>
        ip: """ + data["DATES"]["DAY2"]["IP"] + """ <br>
        total_times_used: """ + data["DATES"]["DAY2"]["total_times_used"] + """ <br>
        minutes: """ + data["DATES"]["DAY2"]["minutes"] + """ <br>
        alarms_used: """ + data["DATES"]["DAY2"]["alarms_used"] + """ <br>
        timers_used: """ + data["DATES"]["DAY2"]["timers_used"] + """ <br>
        <br><b>DAY6: </b><br> 
        date: """ + data["DATES"]["DAY2"]["date"] + """ <br>
        ip: """ + data["DATES"]["DAY2"]["IP"] + """ <br>
        total_times_used: """ + data["DATES"]["DAY2"]["total_times_used"] + """ <br>
        minutes: """ + data["DATES"]["DAY2"]["minutes"] + """ <br>
        alarms_used: """ + data["DATES"]["DAY2"]["alarms_used"] + """ <br>
        timers_used: """ + data["DATES"]["DAY2"]["timers_used"] + """ <br>
        <br><b>DAY7: </b><br> 
        date: """ + data["DATES"]["DAY2"]["date"] + """ <br>
        ip: """ + data["DATES"]["DAY2"]["IP"] + """ <br>
        total_times_used: """ + data["DATES"]["DAY2"]["total_times_used"] + """ <br>
        minutes: """ + data["DATES"]["DAY2"]["minutes"] + """ <br>
        alarms_used: """ + data["DATES"]["DAY2"]["alarms_used"] + """ <br>
        timers_used: """ + data["DATES"]["DAY2"]["timers_used"] + """ <br>
      </body>
    </html>
    """
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP("mail.metacafebliss.com", 26)
    s.sendmail(EM_DATA, EM_DATA, msg.as_string())
    s.quit()


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
    # get_data()
    app.run(debug=True)

# Notes to self:
# check all css/js links for any that need internet and download them
# check for corrupted files?
# try everything so if there is errors
#
