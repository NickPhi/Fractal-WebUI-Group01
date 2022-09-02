from Dashboard import app, os

if __name__ == "__main__":
    # get_data()
    os.system("sudo /usr/bin/systemctl restart screensaver.service")
    app.run(debug=True)
