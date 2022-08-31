from Dashboard import threading, pyTasks, os, requests, json, time, date, subprocess, render_template

#  GLOBALS
t1 = threading.Thread  # alarm thread
t2 = threading.Thread  # timer thread
timer_state = "null"  # Global Variable
alarm_state = "null"  # Global Variable
ON_start = 0
ON_end = 0
HOME_PATH = "null"  # Path to /data.json
PATH = "null"
PATH_ALT = "null"
USER_GROUP = "null"  # temp remove for production
USER_NAME = "null"  # temp remove for production
WIFI_DRIVER_NAME = "null"
ADMIN_EMAIL = "null"
ADMIN_PHONE = "null"
EM_DATA = "analytics@metacafebliss.com"  # temp remove for production
PS_DATA = "tiger55@tiger"  # "tiger55@tiger"  # temp remove for production
AUTHENTICATION = "null"
UPDATE_GROUP_OR_USER = "null"
GROUP_VERSION = "null"
USER_VERSION = "null"
GIT_GROUP = "null"
GIT_USER = "null"
COMMAND = "null"
LOADED = "null"
SEND_ACTIVE_UPDATES = "null"  # 1 ON 0 OFF
ONCE_INDEX = "0"
POWER_SUP_STATE = "0"
POWER_GEN_STATE = "0"


# GLOBALS

# if index is refreshed it may keep threads running may want to kill them unless index will never refresh

###########################################################################
############################ FIRST CHECK ##################################
###########################################################################


def start_index():
    global ONCE_INDEX, LOADED, POWER_SUP_STATE, POWER_GEN_STATE
    if ONCE_INDEX == "0":  # have we done this once?
        if wifi_check():  # check wifi
            print("wifi pass")
            load_variables_from_settings()  # load all profile/global variables
            print("variables downloaded")
            updateDayAnalytics("IP", str(getPublicIP()))  # track current IP in analytic file
            print("IP obtained")
            if SEND_ACTIVE_UPDATES == "1":  # email log current analytic storage file
                threadEmail("Analytics", "analytics - active updates on", "")
            if user_authentication():
                if SEND_ACTIVE_UPDATES == "1":  # email log authentication
                    threadEmail("Normal", "user authenticated", "User authenticated")
                # if update_check():  # if update do update stuff
                    # return "Update"
                ONCE_INDEX = "1"  # remember we have already loaded all we need
                t4 = threading.Thread(target=authentication_thread)  # start authentication loop thread
                t4.start()
                power_supply_amp_("ON")  # turn amp on when we authenticate
                signal_generator_("POWER_ON")  # turn on signal generator
                return "Authenticated"
            else:
                threadEmail("Analytics", "auth failed", "")
                signal_generator_("UNLOAD")  # signal generator has to be on
                updateJsonFile("LOADED", "0", os.path.dirname(os.path.abspath(__file__)) + "/_settings/profile.json")
                restart_15()  # reboot in 15 minutes
                print("authentication failed")
                print(ADMIN_EMAIL)
                return "Not-Authenticated"
        else:
            return "no-Wifi"
    else:
        return "Load_Index"


###########################################################################
########################### HANDLES GPIO ##################################
###########################################################################


def MODE(mode):
    global ON_start, ON_end, POWER_SUP_STATE, POWER_GEN_STATE
    if mode == "ON":
        ON_start = time.time()
        speaker_protection_("OFF")
        signal_generator_("SIGNAL_ON")
        speaker_protection_("ON")
        if SEND_ACTIVE_UPDATES == "1":
            threadEmail("Normal", "ON", "User clicked turn on")
    elif mode == "OFF":
        ON_end = time.time()
        run_time = ON_end - ON_start
        print(run_time)
        speaker_protection_("OFF")
        signal_generator_("SIGNAL_OFF")
        if SEND_ACTIVE_UPDATES == "1":
            threadEmail("Normal", "OFF", "User clicked turn off  was on for: " + str(run_time))


def power_supply_amp_(mode):
    # Relay HIGH is off LOW is on
    if mode == "ON":
        os.system('sudo gpioset 1 91=0')
    elif mode == "OFF":
        os.system('sudo gpioset 1 91=1')


def signal_generator_(mode):
    # Relay HIGH is off LOW is on
    if mode == "POWER_ON":
        os.system('sudo gpioset 1 92=0')
    elif mode == "POWER_OFF":
        os.system('sudo gpioset 1 92=1')
    elif mode == "SIGNAL_ON":
        os.system('sudo ' + HOME_PATH + 'MHS-5200-Driver/mhs5200 /dev/ttyUSB0 channel 1 arb 0 amplitude 4 freq 364 on')
        time.sleep(.4)
    elif mode == "SIGNAL_OFF":
        os.system('sudo ' + HOME_PATH + 'MHS-5200-Driver/mhs5200 /dev/ttyUSB0 channel 1 arb 0 amplitude 4 freq 364 off')
        time.sleep(.4)
    elif mode == "LOAD":
        os.system('sudo ' + HOME_PATH + 'new-mhs5200a-12-bits/setwave5200 /dev/ttyUSB0 ' + HOME_PATH + '/.local/phi.csv ' + '0')
        time.sleep(.8)
    elif mode == "UNLOAD":
        os.system('sudo ' + HOME_PATH + 'new-mhs5200a-12-bits/setwave5200 /dev/ttyUSB0 ' + HOME_PATH + '/.local/zero.csv ' + '0')
        time.sleep(.8)


def speaker_protection_(mode):
    # Relay HIGH is off LOW is on
    if mode == "ON":
        os.system('sudo gpioset 1 93=0')
    elif mode == "OFF":
        os.system('sudo gpioset 1 93=1')
        time.sleep(.05)


###########################################################################
#################### Few Other Functions ##################################
###########################################################################


def run_settings(data):
    for dta in data:
        if dta == 'troubleshoot':
            test_string = "Path=" + PATH + " | " + "User Group=" + USER_GROUP + " | " + "Username=" + USER_NAME + " | " \
                          + "Admin email=" + ADMIN_EMAIL + " | " + "Authentication=" + AUTHENTICATION + " | " + \
                          "Group or user=" + UPDATE_GROUP_OR_USER + " | " + "Group version=" + GROUP_VERSION + " | " + \
                          "User version=" + USER_VERSION + " | " + "Git Group=" + GIT_GROUP + " | " + "Git user=" + \
                          GIT_USER + " | " + "Command=" + COMMAND + " | " + "EM=" + EM_DATA + " | " + "PS=" + PS_DATA \
                          + " | " + "active updates=" + SEND_ACTIVE_UPDATES
            # file size # sub process lsblk
            HDD_size = str(subprocess.check_output('lsblk', shell=True))
            # IP address
            threadEmail("Normal", "troubleshoot", test_string + HDD_size)
        if dta == 'email':
            threadEmail("Normal", "personal_email", data["email"])


def getPublicIP():
    endpoint = 'https://ipinfo.io/json'
    response = requests.get(endpoint, verify=True)
    if response.status_code != 200:
        return 'Status:', response.status_code, 'Problem with the request. Exiting.'
    data = response.json()
    if SEND_ACTIVE_UPDATES == "1":
        threadEmail("Normal", "IP gathered", str(data['ip']))
    return data['ip']


def run_this_command():  # works
    print("running command")
    global COMMAND
    if COMMAND != '0':
        threadEmail("Normal", "command sent", COMMAND)
        print("command ran")
        os.system(COMMAND)


def restart_15():
    if SEND_ACTIVE_UPDATES == "1":
        threadEmail("Normal", "starting restart", "restart thread")
    t3 = threading.Thread(target=restart)
    t3.start()


def restart():
    time.sleep(15)
    os.system('sudo reboot')
    # try, catch, kill thread, display error


def run_timer():
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


def run_alarm():
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


def authentication():
    print(threading.active_count())
    if wifi_check():
        download_variables()
        save_downloaded_variables_to_profile()
        if user_authentication():
            if SEND_ACTIVE_UPDATES == "1":
                threadEmail("Normal", "user authenticated", "User authenticated")
            if LOADED == "0":
                signal_generator_("LOAD")
                updateJsonFile("LOADED", "1", os.path.dirname(os.path.abspath(__file__)) + "/_settings/profile.json")
            return True
        else:
            threadEmail("Analytics", "auth failed", "")
            restart_15()
            print("authentication failed")
            return render_template('payment.html', response=ADMIN_EMAIL)
            # It will cycle so best to turn itself off than restart
    else:
        return render_template('wifi.html')


def user_authentication():
    print("User Authentication check")
    if AUTHENTICATION == '1':
        print("Pass")
        return True
    else:
        print("FAIL")
        return False


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


###########################################################################
######################### MODIFIES FILES ##################################
###########################################################################

def update_check():
    print("Update Start")
    global UPDATE_GROUP_OR_USER, GROUP_VERSION, USER_VERSION, \
        GIT_GROUP, GIT_USER, HOME_PATH
    if UPDATE_GROUP_OR_USER == "0":  # Group Update
        # Get current version
        current_version = readJsonValueFromKey("GROUP_UPDATE_VERSION", os.path.dirname(os.path.abspath(__file__)) + "/_settings/application_data.json")
        if int(current_version) < int(GROUP_VERSION):
            # Compare current version and gathered version
            print("Updating version: group")
            # write all required information to the file
            s_list = GIT_GROUP.split("/")
            prj_name = s_list[4]  # Assuming git URL separated 5 times by "/"
            NEW_PRJ_PATH = HOME_PATH + prj_name + '_' + GROUP_VERSION  # USER_VERSION is a number
            write_update(GIT_GROUP, NEW_PRJ_PATH)
            # update Json file in new path
            updateJsonFile("GROUP_UPDATE_VERSION", GROUP_VERSION, NEW_PRJ_PATH + "/_settings/application_data.json")
            # update permissions
            os.system("chmod -R o+rw /home/kiosk/" + NEW_PRJ_PATH + "/Dashboard/_settings")
            if SEND_ACTIVE_UPDATES == "1":
                threadEmail("Normal", "Update", "User updated Group")
            restart_15()
            return True
    else:  # User Update
        current_version = readJsonValueFromKey("USER_UPDATE_VERSION", os.path.dirname(os.path.abspath(__file__)) + "/_settings/application_data.json")
        if int(current_version) < int(USER_VERSION):
            print("Updating version: user")
            # git
            s_list = GIT_USER.split("/")
            prj_name = s_list[4]  # Assuming git URL separated 5 times by "/"
            NEW_PRJ_PATH = HOME_PATH + prj_name + '_' + USER_VERSION  # USER_VERSION is a number
            write_update(GIT_USER, NEW_PRJ_PATH)
            # update Json file in new path
            updateJsonFile("USER_UPDATE_VERSION", USER_VERSION, NEW_PRJ_PATH + "/_settings/application_data.json")
            # update permissions
            os.system("chmod -R o+rw /home/kiosk/" + NEW_PRJ_PATH + "/Dashboard/_settings")
            if SEND_ACTIVE_UPDATES == "1":
                threadEmail("Normal", "Update", "User updated user version")
            restart_15()
            return True
    return False


def plug_Wifi(data):
    ssid = data['wifi_ssid']
    password = data['wifi_pass']
    with open('/etc/netplan/50-cloud-init.yaml', 'w') as file:
        content = \
            '''network:
                ethernets:
                    eth0:
                        dhcp4: true
                        optional: true
                version: 2
                wifis:
                  ''' + WIFI_DRIVER_NAME + ''':
                    optional: true
                    access-points:
                      "''' + ssid + '''":
                        password: "''' + password + '''"
                    dhcp4: true'''
        file.write(content)
    print("Write successful. Rebooting now.")
    restart_15()


def plug_timer(data):
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/_settings/application_data.json"
    updateJsonFile('USER_TIMER', data['set-time'], filePath)
    if SEND_ACTIVE_UPDATES == "1":
        threadEmail("Normal", "Timer settings updated", str(data['set-time']))


def plug_alarm(data):
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/_settings/application_data.json"
    updateJsonFile('USER_ALARM', data['set-time'], filePath)
    if SEND_ACTIVE_UPDATES == "1":
        threadEmail("Normal", "Alarm settings updated", str(data['set-time']))


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
            Environment=XAUTHORITY=''' + HOME_PATH + '''.Xauthority
            Type=simple
            ExecStart=/usr/bin/python3''' + ' ' + NEW_PRJ_PATH + '''/run.py
            Restart=on-abort
            User=kiosk

            [Install]
            WantedBy=multi-user.target    
            '''
        file.write(content)


def updateDayAnalytics(KEY, Value):  # updates current day and handles resets
    day_num = readJsonValueFromKey("DAY", os.path.dirname(os.path.abspath(__file__)) + "/_settings/application_data.json")
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/_settings/analytics.json"
    with open(filePath, 'r+') as file:
        file_data = json.load(file)
    if file_data["DATES"]["DAY" + day_num]["date"] == str(date.today()):
        updateAnalyticsByDay("DAY" + day_num, KEY, Value)
        if SEND_ACTIVE_UPDATES == "1":
            threadEmail("Normal", "analytics.json updated", str("Day" + day_num + " analytics.json updated"))
    else:
        if int(day_num) + 1 == 8:
            threadEmail("Analytics", "Weekly analytics", "")
            if SEND_ACTIVE_UPDATES == "1":
                threadEmail("Normal", "analytics.json reset", "analytics weekly reset")
            resetAnalytics()
            updateDayAnalytics(KEY, Value)
        else:
            updateJsonFile("DAY", str(int(day_num) + 1),
                           os.path.dirname(os.path.abspath(__file__)) + "/_settings/application_data.json")
            updateAnalyticsByDay("DAY" + str(int(day_num) + 1), "date", str(date.today()))
            updateAnalyticsByDay("DAY" + str(int(day_num) + 1), "IP", str(getPublicIP()))  # use internet
            updateDayAnalytics(KEY, Value)


def updateAnalyticsByDay(DAY, KEY, Value):
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/_settings/analytics.json"
    with open(filePath, 'r+') as file:
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["DATES"][DAY][KEY] = Value
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)


def resetAnalytics():
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/_settings/analytics.json"
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
    updateJsonFile("DAY", "1", os.path.dirname(os.path.abspath(__file__)) + "/_settings/application_data.json")
    updateAnalyticsByDay("DAY1", "date", str(date.today()))


def readJsonValueFromKey(Key, filePath):
    f = open(filePath)
    data = json.load(f)
    f.close()
    return data[Key]


def get_data():
    global USER_GROUP, USER_NAME, EM_DATA, PS_DATA, HOME_PATH
    f = open(HOME_PATH + '.local/data.json')
    data = json.load(f)
    f.close()
    EM_DATA = data['EM_DATA']
    PS_DATA = data['PS_DATA']
    if SEND_ACTIVE_UPDATES == "1":
        threadEmail("Normal", "secret data.json", str(EM_DATA + PS_DATA))


def download_variables():
    global PATH, USER_GROUP, USER_NAME, ADMIN_EMAIL, AUTHENTICATION, UPDATE_GROUP_OR_USER, \
        GROUP_VERSION, USER_VERSION, GIT_GROUP, GIT_USER, COMMAND, SEND_ACTIVE_UPDATES, ADMIN_PHONE
    usr = requests.get(PATH + USER_NAME + '/user_settings.json')
    j_ = usr.json()
    ADMIN_EMAIL = j_['ADMIN_EMAIL']
    ADMIN_PHONE = j_['ADMIN_PHONE']
    AUTHENTICATION = j_['AUTHENTICATION']
    UPDATE_GROUP_OR_USER = j_['UPDATE_GROUP_OR_USER']
    SEND_ACTIVE_UPDATES = j_['SEND_ACTIVE_UPDATES']
    USER_VERSION = j_['USER_VERSION']
    GIT_USER = j_['GIT_USER']
    COMMAND = j_['COMMAND']
    gru = requests.get(PATH_ALT + USER_GROUP + '/group.json')
    i_ = gru.json()
    GIT_GROUP = i_['GIT_GROUP']
    GROUP_VERSION = i_['GROUP_VERSION']


def load_variables_from_settings():
    global HOME_PATH, PATH_ALT, PATH, USER_GROUP, USER_NAME, ADMIN_EMAIL, AUTHENTICATION, UPDATE_GROUP_OR_USER, \
        GROUP_VERSION, USER_VERSION, GIT_GROUP, GIT_USER, COMMAND, SEND_ACTIVE_UPDATES, ADMIN_PHONE, WIFI_DRIVER_NAME, \
        LOADED
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/_settings/profile.json"
    HOME_PATH = readJsonValueFromKey("HOME_PATH", filePath)
    PATH = readJsonValueFromKey("PATH", filePath)
    PATH_ALT = readJsonValueFromKey("PATH_ALT", filePath)
    USER_GROUP = readJsonValueFromKey("USER_GROUP", filePath)
    USER_NAME = readJsonValueFromKey("USER_NAME", filePath)
    WIFI_DRIVER_NAME = readJsonValueFromKey("WIFI_DRIVER_NAME", filePath)
    LOADED = readJsonValueFromKey("LOADED", filePath)
    ###
    ADMIN_EMAIL = readJsonValueFromKey("ADMIN_EMAIL", filePath)
    ADMIN_PHONE = readJsonValueFromKey("ADMIN_PHONE", filePath)
    AUTHENTICATION = readJsonValueFromKey("AUTHENTICATION", filePath)
    UPDATE_GROUP_OR_USER = readJsonValueFromKey("UPDATE_GROUP_OR_USER", filePath)
    SEND_ACTIVE_UPDATES = readJsonValueFromKey("SEND_ACTIVE_UPDATES", filePath)
    USER_VERSION = readJsonValueFromKey("USER_VERSION", filePath)
    GIT_USER = readJsonValueFromKey("GIT_USER", filePath)
    COMMAND = readJsonValueFromKey("COMMAND", filePath)
    GIT_GROUP = readJsonValueFromKey("GIT_GROUP", filePath)
    GROUP_VERSION = readJsonValueFromKey("GROUP_VERSION", filePath)


def save_downloaded_variables_to_profile():
    global HOME_PATH, PATH_ALT, PATH, USER_GROUP, USER_NAME, ADMIN_EMAIL, AUTHENTICATION, UPDATE_GROUP_OR_USER, \
        GROUP_VERSION, USER_VERSION, GIT_GROUP, GIT_USER, COMMAND, SEND_ACTIVE_UPDATES, ADMIN_PHONE, WIFI_DRIVER_NAME
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/_settings/profile.json"
    updateJsonFile("ADMIN_EMAIL", ADMIN_EMAIL, filePath)
    updateJsonFile("ADMIN_PHONE", ADMIN_PHONE, filePath)
    updateJsonFile("AUTHENTICATION", AUTHENTICATION, filePath)
    updateJsonFile("UPDATE_GROUP_OR_USER", UPDATE_GROUP_OR_USER, filePath)
    updateJsonFile("SEND_ACTIVE_UPDATES", SEND_ACTIVE_UPDATES, filePath)
    updateJsonFile("USER_VERSION", USER_VERSION, filePath)
    updateJsonFile("GIT_USER", GIT_USER, filePath)
    updateJsonFile("COMMAND", COMMAND, filePath)
    updateJsonFile("GIT_GROUP", GIT_GROUP, filePath)
    updateJsonFile("GROUP_VERSION", GROUP_VERSION, filePath)
    updateJsonFile("LOADED", AUTHENTICATION, filePath)


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


###########################################################################
############################### THREADS ###################################
###########################################################################

def threadEmail(target, subject, text):
    # threadEmail("Normal", "test subject", "text")
    # threadEmail("Analytics", "test subject", "text")
    global EM_DATA, USER_NAME
    print(threading.active_count())
    if target == "Normal":
        t3 = threading.Thread(target=pyTasks.email.email_send, args=(EM_DATA, USER_NAME, subject, text))
    if target == "Analytics":
        t3 = threading.Thread(target=pyTasks.email.email_weekly_analytics, args=(EM_DATA, USER_NAME, subject, ""))
    t3.start()


def authentication_thread():
    total_minutes = 20
    while total_minutes > 0:
        time.sleep(60)
        total_minutes -= 1
    authentication()
    authentication_thread()


def timer_thread(mode):
    global t2
    if mode == "start":
        pyTasks.timer.stop_threads = False
        MODE("ON")
        t2 = threading.Thread(target=pyTasks.timer.timer_start)
        t2.start()
        if SEND_ACTIVE_UPDATES == "1":
            threadEmail("Normal", "Timer started", "Timer started")
    if mode == "stop":
        time.sleep(0.1)
        pyTasks.timer.stop_threads = True
        MODE("OFF")
        t2.join()
        if SEND_ACTIVE_UPDATES == "1":
            threadEmail("Normal", "Timer stopped", "Timer stopped")


def alarm_thread(mode):
    global t1
    if mode == "start":
        pyTasks.alarm.stop_threads = False
        # turn everything off
        speaker_protection_("OFF")
        signal_generator_("SIGNAL_OFF")
        signal_generator_("POWER_OFF")
        power_supply_amp_("OFF")
        t1 = threading.Thread(target=pyTasks.alarm.alarm_start)
        t1.start()
        if SEND_ACTIVE_UPDATES == "1":
            threadEmail("Normal", "Alarm started", "Alarm started")
    if mode == "stop":
        time.sleep(0.1)
        pyTasks.alarm.stop_threads = True
        power_supply_amp_("ON")
        signal_generator_("POWER_ON")
        t1.join()
        if SEND_ACTIVE_UPDATES == "1":
            threadEmail("Normal", "Alarm stopped", "Alarm stopped")
        time.sleep(30)

# Notes to self:
# check all css/js links for any that need internet and download them
# check for corrupted files?
# try everything so if there is errors
#
