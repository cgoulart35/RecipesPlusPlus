#region IMPORTS
import json
import pyrebase
import logging
import importlib.util
import pathlib
import threading
from configparser import ConfigParser
from flask import Flask, abort, request
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
apiQueryLock = threading.Lock()

class Ingredients(Resource):
    def get(self, id=None):
        apiQueryLock.acquire()
        try:
            if id == None:
                # get all ingredients
                return queries.getAllIngredients(db, token)
            else:
                # get specific ingredient
                return queries.getIngredient(db, token, id)               
        except:
            abort(400, f"No ingredient exists.")
        finally:
            apiQueryLock.release()

    def delete(self, id):
        apiQueryLock.acquire()
        try: 
            queries.removeIngredient(db, token, id)
            return True
        except:
            abort(400, f"No ingredient deleted.")
        finally:
            apiQueryLock.release()

    def post(self):
        apiQueryLock.acquire()
        value = request.get_data()
        value = json.loads(value)
        apiQueryLock.release()
        return

class Recipes(Resource):
    def get(self, id=None):
        apiQueryLock.acquire()
        try:
            if id == None:
                # get all recipes
                return queries.getAllRecipes(db, token)
            else:
                # get specific recipe
                return queries.getRecipe(db, token, id) 
        except:
            abort(400, f"No recipe exists.")
        finally:
            apiQueryLock.release()
    
    def delete(self, id):
        apiQueryLock.acquire()
        try:
            queries.removeRecipe(db, token, id)
            return True
        except:
            abort(400, f"No recipe deleted.")
        finally:
            apiQueryLock.release()
    
    def post(self):
        apiQueryLock.acquire()
        value = request.get_data()
        value = json.loads(value)
        apiQueryLock.release()
        return

class Users(Resource):
    def get(self, id=None):
        apiQueryLock.acquire()
        try:
            if id == None:
                # get all users
                return queries.getAllUsers(db, token)
            else:
                # get specific user
                return queries.getUser(db, token, id)            
        except:
            abort(400, f"No user exists.")
        finally:
            apiQueryLock.release()
    
    def delete(self, id):
        apiQueryLock.acquire()
        try:
            queries.removeUser(db, token, id)
            return True
        except:
            abort(400, f"No user deleted.")
        finally:
            apiQueryLock.release()
    
    def post(self):
        apiQueryLock.acquire()
        value = request.get_data()
        value = json.loads(value)
        apiQueryLock.release()
        return

api.add_resource(Ingredients, '/RecipesPlusPlus/ingredients/', '/RecipesPlusPlus/ingredients/<int:id>/')
api.add_resource(Recipes, '/RecipesPlusPlus/recipes/', '/RecipesPlusPlus/recipes/<int:id>/')
api.add_resource(Users, '/RecipesPlusPlus/users/', '/RecipesPlusPlus/users/<int:id>/')
app.run(host='0.0.0.0', port=5000)