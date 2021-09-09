#region IMPORTS
from configparser import ConfigParser
import json
import pyrebase
import logging
import pathlib
#endregion

# get parent directory
parentDir = str(pathlib.Path(__file__).parent.parent.absolute())
parentDir = parentDir.replace("\\",'/')

# get configuration variables
config = ConfigParser()
config.read('RecipesPlusPlusApi/config.ini')

# initialize firebase and database
firebaseConfig = json.loads(config['properties']['firebaseConfigJson'])
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(config['properties']['firebaseAuthEmail'], config['properties']['firebaseAuthPassword'])
token = user['idToken']

# create and configure logger
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename = parentDir + '/RecipesPlusPlusApi.log', level = logging.INFO, format = LOG_FORMAT)

# start flask API
