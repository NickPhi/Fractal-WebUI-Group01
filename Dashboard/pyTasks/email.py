from Dashboard import os, json, threading, MIMEMultipart, MIMEText, smtplib


def email_send(EM_DATA, USER_NAME, subject, text):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject + " " + USER_NAME
    msg['From'] = EM_DATA
    msg['To'] = EM_DATA

    part1 = MIMEText(text, 'plain')
    msg.attach(part1)

    s = smtplib.SMTP("mail.metacafebliss.com", 26)
    s.sendmail(EM_DATA, EM_DATA, msg.as_string())
    s.quit()
    print("email sent")


def email_weekly_analytics(EM_DATA, USER_NAME, subject, text):
    print(threading.active_count())
    filePath = os.path.abspath(os.curdir) + "/analytics.json"
    with open(filePath, 'r+') as file:
        data = json.load(file)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject + " " + USER_NAME
    msg['From'] = EM_DATA
    msg['To'] = EM_DATA

    # Create the body of the message (a plain-text and an HTML version).
    text = text
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