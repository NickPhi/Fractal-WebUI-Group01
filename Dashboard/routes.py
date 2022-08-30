import Dashboard.service
from Dashboard import app, threading
from flask import render_template, request
from Dashboard.service import start_index, MODE, run_settings, plug_Wifi, plug_timer, plug_alarm, run_alarm, run_timer


@app.route('/')
def index():
    Status = start_index()
    if Status == "Load_Index":
        return render_template('index.html')
    elif Status == "Authenticated":
        return render_template('index.html')
    elif Status == "Not-Authenticated":
        return render_template('payment.html', response=Dashboard.service.ADMIN_EMAIL)
    elif Status == "Update":
        return render_template('system_reboot.html', response='Updated your version')
    elif Status == "no-Wifi":
        return render_template('wifi.html')


@app.route('/turnon')
def turnon():
    MODE("ON")
    return "Complete"


@app.route('/turnoff')
def turnoff():
    MODE("OFF")
    return "Complete"


@app.route('/alarm')
def alarm():
    run_alarm()
    return "Complete"


@app.route('/timer')
def timer():
    run_timer()
    return "Complete"


@app.route('/settings.html', methods=['GET', 'POST'])
def settings():
    print(threading.active_count())
    if request.method == 'GET':
        return render_template("settings.html", response=Dashboard.service.ADMIN_EMAIL + " " + Dashboard.service.ADMIN_PHONE)
    if request.method == 'POST':
        run_settings(request.form)
        return render_template('index.html')


@app.route('/wifi.html', methods=['GET', 'POST'])
def wifi():
    if request.method == 'GET':
        return render_template('wifi.html')
    if request.method == 'POST':
        plug_Wifi(request.form)
        return render_template('system_reboot.html')


@app.route('/timer_settings', methods=['GET', 'POST'])
def timer_settings():
    if request.method == 'GET':
        return render_template('timer_settings.html')
    if request.method == 'POST':
        plug_timer(request.form)
        return render_template('index.html')


@app.route('/alarm_settings', methods=['GET', 'POST'])
def alarm_settings():
    if request.method == 'GET':
        return render_template('alarm_settings.html')
    if request.method == 'POST':
        plug_alarm(request.form)
        return render_template('index.html')


@app.route('/wifi_back.html', methods=['GET', 'POST'])
def wifi_back():
    if request.method == 'GET':
        return render_template('wifi_back.html')
    if request.method == 'POST':
        plug_Wifi(request.form)
        return render_template('system_reboot.html')
