#region IMPORTS
import json
import pyrebase
import logging
import importlib.util
import pathlib
from configparser import ConfigParser
from flask import Flask, request
from flask_restful import Api, Resource
#endregion

# get parent directory and dependencies
parentDir = str(pathlib.Path(__file__).parent.parent.absolute())
parentDir = parentDir.replace("\\",'/')

spec = importlib.util.spec_from_file_location('shared', parentDir + '/Shared/functions.py')
functions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(functions)

spec = importlib.util.spec_from_file_location('shared', parentDir + '/Shared/queries.py')
queries = importlib.util.module_from_spec(spec)
spec.loader.exec_module(queries)

# get configuration variables
apiConfig = ConfigParser()
apiConfig.read('RecipesPlusPlusApi/api.ini')
sharedConfig = functions.buildSharedConfig(parentDir)

# initialize firebase and database
firebaseConfig = json.loads(sharedConfig['properties']['firebaseConfigJson'])
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(sharedConfig['properties']['firebaseAuthEmail'], sharedConfig['properties']['firebaseAuthPassword'])
token = user['idToken']

# create and configure logger
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename = parentDir + '/RecipesPlusPlusApi.log', level = logging.INFO, format = LOG_FORMAT)

# Flask REST API
app = Flask(__name__)
api = Api(app)

class Ingredients(Resource):
    def get(self, id=None):
        if not id:
            # get all ingredients
            return 1
        else:
            # get specific ingredient
            return id
    def post(self):
        return
    def delete(self, id):
        return

class Recipes(Resource):
    def get(self, id=None):
        if not id:
            # get all recipes
            return 1
        else:
            # get specific recipe
            return id
    def post(self):
        return
    def delete(self, id):
        return

class Users(Resource):
    def get(self, id=None):
        if not id:
            # get all users
            return 1
        else:
            # get specific user
            return id
    def post(self):
        return
    def delete(self, id):
        return

api.add_resource(Ingredients, '/RecipesPlusPlus/ingredients/', '/RecipesPlusPlus/ingredients/<int:id>/')
api.add_resource(Recipes, '/RecipesPlusPlus/recipes/', '/RecipesPlusPlus/recipes/<int:id>/')
api.add_resource(Users, '/RecipesPlusPlus/users/', '/RecipesPlusPlus/users/<int:id>/')
app.run(host='0.0.0.0', port=5000)