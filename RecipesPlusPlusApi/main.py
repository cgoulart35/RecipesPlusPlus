#region IMPORTS
import json
import pyrebase
import logging
import importlib.util
import pathlib
import threading
from configparser import ConfigParser
from apscheduler.schedulers.background import BackgroundScheduler
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

# create and configure logger
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename = parentDir + '/RecipesPlusPlusApi.log', level = logging.INFO, format = LOG_FORMAT)

# initialize firebase and database
firebaseConfig = json.loads(sharedConfig['properties']['firebaseConfigJson'])
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(sharedConfig['properties']['firebaseAuthEmail'], sharedConfig['properties']['firebaseAuthPassword'])

# create event scheduler for refreshing auth token
def refreshToken():
    global user
    user = auth.refresh(user['refreshToken'])

sched = BackgroundScheduler(daemon=True)
sched.add_job(refreshToken, 'interval', minutes = 1)
sched.start()

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
                return queries.getAllIngredients(db, user['idToken'])
            else:
                # get specific ingredient
                return queries.getIngredient(db, user['idToken'], id)               
        except:
            abort(400, "No ingredient exists.")
        finally:
            apiQueryLock.release()

    def delete(self, id):
        apiQueryLock.acquire()
        try: 
            queries.removeIngredient(db, user['idToken'], id)
            return True
        except:
            abort(400, "No ingredient deleted.")
        finally:
            apiQueryLock.release()

    def post(self):
        apiQueryLock.acquire()
        value = request.get_data()
        value = json.loads(value)

        # validate there is a field for name (str) (optional: image_url (str))
        isInvalid = False
        errorMsg = "Please fix the following values: "

        if value["name"] == None or value["name"] == "" or type(value["name"]) != str:
            isInvalid = True
            errorMsg += "name (str) "
        if type(value["image_url"]) != str:
            isInvalid = True
            errorMsg += "image_url (str) "
        errorMsg += "(optional: image_url (str))"

        try:
            if isInvalid:
                raise Exception
            errorMsg = "No ingredient added."
            queries.addIngredient(db, user['idToken'], value["name"], value["image_url"])
            return True
        except:
            abort(400, errorMsg)
        finally:
            apiQueryLock.release()

class Recipes(Resource):
    def get(self, id=None):
        apiQueryLock.acquire()
        try:
            if id == None:
                # get all recipes
                return queries.getAllRecipes(db, user['idToken'])
            else:
                # get specific recipe
                return queries.getRecipe(db, user['idToken'], id) 
        except:
            abort(400, "No recipe exists.")
        finally:
            apiQueryLock.release()
    
    def delete(self, id):
        apiQueryLock.acquire()
        try:
            queries.removeRecipe(db, user['idToken'], id)
            return True
        except:
            abort(400, "No recipe deleted.")
        finally:
            apiQueryLock.release()
    
    def post(self):
        apiQueryLock.acquire()
        value = request.get_data()
        value = json.loads(value)

        # validate there are fields for ingredients (list), instructions (list), name (str) (optional: calories (int) image_url (str) time (int))
        isInvalid = False
        errorMsg = "Please fix the following values: "

        if value["ingredients"] == None or not value["ingredients"] or type(value["ingredients"]) != list:
            isInvalid = True
            errorMsg += "ingredients (list) "
        if value["instructions"] == None or not value["instructions"] or type(value["instructions"]) != list:
            isInvalid = True
            errorMsg += "instructions (list) "
        if value["name"] == None or value["name"] == "" or type(value["name"]) != str:
            isInvalid = True
            errorMsg += "name (str) "
        if type(value["calories"]) != int:
            isInvalid = True
            errorMsg += "calories (int) "
        if type(value["image_url"]) != str:
            isInvalid = True
            errorMsg += "image_url (str) "
        if type(value["time"]) != int:
            isInvalid = True
            errorMsg += "time (int) "
        errorMsg += "(optional: calories (int) image_url (str) time (int))"

        try:
            if isInvalid:
                raise Exception
            errorMsg = "No recipe added."
            queries.addRecipe(db, user['idToken'], value["calories"], value["image_url"], value["ingredients"], value["instructions"], value["name"], value["time"])
            return True
        except:
            abort(400, errorMsg)
        finally:
            apiQueryLock.release()

class Users(Resource):
    def get(self, id=None):
        apiQueryLock.acquire()
        try:
            if id == None:
                # get all users
                return queries.getAllUsers(db, user['idToken'])
            else:
                # get specific user
                return queries.getUser(db, user['idToken'], id)            
        except:
            abort(400, "No user exists.")
        finally:
            apiQueryLock.release()
    
    def delete(self, id):
        apiQueryLock.acquire()
        try:
            queries.removeUser(db, user['idToken'], id)
            return True
        except:
            abort(400, "No user deleted.")
        finally:
            apiQueryLock.release()
    
    def post(self):
        apiQueryLock.acquire()
        value = request.get_data()
        value = json.loads(value)

        # validate there is a field for email (str) name (str) (optional: recipes (list))
        isInvalid = False
        errorMsg = "Please fix the following values: "

        if value["email"] == None or value["email"] == "" or type(value["email"]) != str:
            isInvalid = True
            errorMsg += "email (str) "
        if value["name"] == None or value["name"] == "" or type(value["name"]) != str:
            isInvalid = True
            errorMsg += "name (str) "
        if type(value["recipes"]) != list:
            isInvalid = True
            errorMsg += "recipes (list) "
        errorMsg += "(optional: recipes (list))"

        try:
            if isInvalid:
                raise Exception
            errorMsg = "No user added."
            queries.addUser(db, user['idToken'], value["email"], value["name"], value["recipes"])
            return True
        except:
            abort(400, errorMsg)
        finally:
            apiQueryLock.release()

api.add_resource(Ingredients, '/RecipesPlusPlus/ingredients/', '/RecipesPlusPlus/ingredients/<int:id>/')
api.add_resource(Recipes, '/RecipesPlusPlus/recipes/', '/RecipesPlusPlus/recipes/<int:id>/')
api.add_resource(Users, '/RecipesPlusPlus/users/', '/RecipesPlusPlus/users/<int:id>/')
app.add_url_rule('/favicon.ico', view_func = lambda: functions.favicon(parentDir))
app.run(host='0.0.0.0', port=5000)