#region IMPORTS
import json
import pyrebase
import logging
import pathlib
from configparser import ConfigParser
from flask import Flask
from flask_restful import Api

from endpoints.ingredients import Ingredients
from endpoints.recipes import Recipes
from endpoints.users import Users
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

# Flask REST API
app = Flask(__name__)
api = Api(app)
api.add_resource(Ingredients, '/RecipesPlusPlus/ingredients/', '/RecipesPlusPlus/ingredients/<int:id>/')
api.add_resource(Recipes, '/RecipesPlusPlus/recipes/', '/RecipesPlusPlus/recipes/<int:id>/')
api.add_resource(Users, '/RecipesPlusPlus/users/', '/RecipesPlusPlus/users/<int:id>/')
app.run(host='0.0.0.0', port=5000)