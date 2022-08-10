from flask import Flask, render_template, request
import pyTasks.alarm
import pyTasks.timer
import threading
import time
import requests
import os

app = Flask(__name__)
t1 = threading.Thread
t2 = threading.Thread
t1_declared = False
t2_declared = False


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if if_wifi_connection():
            return render_template('index.html', Timer_State="Timer_on", Alarm_State="Alarm_on")
        else:
            return render_template('wifi.html')
    if request.method == 'POST':
        data = request.form
        match data['command']:
            case 'ON':
                return render_template("index.html")
            # don't want to kill alarm or timer?
            # try catch the Alarm and Timer to not overload the relay
            case 'OFF':
                return render_template("index.html")
            case 'Alarm_on':
                global t1, t1_declared
                end_threads_t1_t2()
                pyTasks.alarm.stop_threads = False
                t1 = threading.Thread(target=pyTasks.alarm.alarm_start)
                t1.start()
                t1_declared = True
                return render_template('index.html', Timer_State="Timer_on", Alarm_State="Alarm_off")
            case 'Timer_on':
                global t2, t2_declared
                end_threads_t1_t2()  # Prevents t1 Alarm from running same time
                pyTasks.timer.stop_threads = False
                t2 = threading.Thread(target=pyTasks.timer.timer_start)
                t2.start()
                t2_declared = True
                return render_template('index.html', Timer_State="Timer_off", Alarm_State="Alarm_on", divme='''Hello<a 
                href="https://www.planet.com">world</a>''')
            case 'Alarm_off':
                end_threads_t1_t2()
                # Can Guarantee both are off...
                return render_template('index.html', Timer_State="Timer_on", Alarm_State="Alarm_on")
            case 'Timer_off':
                end_threads_t1_t2()
                return render_template('index.html', Timer_State="Timer_on", Alarm_State="Alarm_on")
            case 'Settings':
                return render_template("index.html")
            case _:
                return render_template("index.html")


@app.route('/timer_settings', methods=['GET', 'POST'])
def timer_settings():
    if request.method == 'GET':
        return render_template('timer_settings.html')
    if request.method == 'POST':
        end_threads_t1_t2()  # End either threads
        data = request.form
        fp = open('user_timer_set.txt', 'w')
        fp.write(data['set-time'])
        fp.close()
        return render_template('index.html', Timer_State="Timer_on", Alarm_State="Alarm_on")


@app.route('/alarm_settings', methods=['GET', 'POST'])
def alarm_settings():
    if request.method == 'GET':
        return render_template('alarm_settings.html')
    if request.method == 'POST':
        end_threads_t1_t2()
        data = request.form
        fp = open('user_alarm_set.txt', 'w')
        fp.write(data['set-time'])
        fp.close()
        return render_template('index.html', Timer_State="Timer_on", Alarm_State="Alarm_on")


def end_threads_t1_t2():
    global t1, t2, t1_declared, t2_declared
    if t1_declared:
        time.sleep(0.1)
        pyTasks.alarm.stop_threads = True
        t1.join()
        t1_declared = False
    if t2_declared:
        time.sleep(0.1)
        pyTasks.timer.stop_threads = True
        t2.join()
        t2_declared = False


def if_wifi_connection():
    req = requests.get('http://clients3.google.com/generate_204')
    #req = requests.get('http://google.com/')
    if req.status_code != 204:
        return False
    else:
        return True


@app.route('/wifi', methods=['GET', 'POST'])
def wifi():
    if request.method == 'GET':
        return render_template('wifi.html')
    if request.method == 'POST':
        end_threads_t1_t2()
        data = request.form
        ssid = data['wifi_ssid']
        password = data['wifi_pass']
        with open('/etc/network/interfaces', 'w') as file:
            content = \
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


if __name__ == "__main__":
    app.run(debug=True)
