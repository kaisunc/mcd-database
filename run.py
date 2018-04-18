import os

from app import create_app, socketio

# configuring from files
# linux export YOURAPPLICATION_SETTINGS=/path/to/settings.cfg
# windows set YOURAPPLICATION_SETTINGS=\path\to\settings.cfg
# set FLASK_CONFIG=C:\Users\julio\Dropbox\Projects\mcd_database\config.py
# set FLASK_APP=C:\Users\julio\Dropbox\Projects\mcd_database\run.py
config_path = r"C:\Users\julio\Dropbox\Projects\mcd_database\config.py"

app = create_app(config_path)

if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0', port=80)
    #app.run(host="0.0.0.0", port=80)