#region IMPORTS
import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from views import views, parentDir, sharedConfig, appConfig, auth, functions
#endregion

# create and configure logger
if not os.path.exists('Logs'):
    os.mkdir('Logs')
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename = parentDir + '/Logs/RecipesPlusPlusWebApp.log', level = logging.INFO, format = LOG_FORMAT)

# sign into service account
user = auth.sign_in_with_email_and_password(sharedConfig['properties']['firebaseAuthEmail'], sharedConfig['properties']['firebaseAuthPassword'])

# create event scheduler for refreshing auth token
def refreshToken():
    global user
    user = auth.refresh(user['refreshToken'])

sched = BackgroundScheduler(daemon=True)
sched.add_job(refreshToken, 'interval', minutes = 30)
sched.start()

app = Flask(__name__)
app.secret_key = appConfig['properties']['secretKey']
app.register_blueprint(views, url_prefix="/RecipesPlusPlus/")
app.add_url_rule('/favicon.ico', view_func = lambda: functions.favicon(parentDir))
app.run(host='0.0.0.0', port=5000)