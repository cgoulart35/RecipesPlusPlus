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
sched.add_job(refreshToken, 'interval', minutes = 30)
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

        try:
            errorMsg = "Invalid JSON"
            value = json.loads(value)

            # validate there is a field for name (str) (optional: image_url (str))
            isInvalid = False
            errorMsg = "Please fix the following values: "

            if "name" not in value or value["name"] == None or value["name"] == "" or type(value["name"]) != str:
                isInvalid = True
                errorMsg += "name (str) "
            if "image_url" in value:
                image_url = value["image_url"]
                if type(image_url) != str:
                    isInvalid = True
                    errorMsg += "image_url (str) "
            else:
                image_url = ""
            errorMsg += "(optional: image_url (str))"

            if isInvalid:
                raise Exception
            errorMsg = "No ingredient added."
            queries.addIngredient(db, user['idToken'], value["name"], image_url)
            return True
        except:
            abort(400, errorMsg)
        finally:
            apiQueryLock.release()

    def put(self, id):
        apiQueryLock.acquire()
        value = request.get_data()

        try:
            errorMsg = "Invalid JSON"
            value = json.loads(value)

            # validate there is a field for name (str) (optional: image_url (str))
            isInvalid = False
            errorMsg = "Please fix the following values: "

            if "name" not in value or value["name"] == None or value["name"] == "" or type(value["name"]) != str:
                isInvalid = True
                errorMsg += "name (str) "
            if "image_url" in value:
                image_url = value["image_url"]
                if type(image_url) != str:
                    isInvalid = True
                    errorMsg += "image_url (str) "
            else:
                image_url = ""
            errorMsg += "(optional: image_url (str))"

            if isInvalid:
                raise Exception
            errorMsg = "No ingredient updated."
            queries.updateIngredient(db, user['idToken'], id, value["name"], image_url)
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

        try:
            errorMsg = "Invalid JSON"
            value = json.loads(value)

            # validate there are fields for ingredients (list), instructions (list), name (str) (optional: calories (int) image_url (str) time (int))
            isInvalid = False
            errorMsg = "Please fix the following values: "

            if "ingredients" not in value or value["ingredients"] == None or not value["ingredients"] or type(value["ingredients"]) != list:
                isInvalid = True
                errorMsg += "ingredients (list of dict { ingredientId (int), unitId (int), quantity (int) }) "
            else:
                existingIngredients = queries.getAllIngredients(db, user['idToken'])
                existingIngredientIds = [ingredient["id"] for ingredient in existingIngredients]
                existingUnits = queries.getAllUnits(db, user['idToken'])
                existingUnitIds = [unit["id"] for unit in existingUnits]

                for ingredient in value["ingredients"]:
                    if type(ingredient) != dict:
                        isInvalid = True
                        errorMsg += "ingredients (list of dict { ingredientId (int), unitId (int), quantity (int) }) "
                        break
                    # validate list of objects each given an ingredientId, unitId, and quantity
                    else:
                        isInvalidIngredient = False
                        isNonExistientIngredient = False
                        isInvalidUnit = False
                        isNonExistientUnit = False
                        isInvalidQuantity = False

                        if "ingredientId" not in ingredient or ingredient["ingredientId"] == None or type(ingredient["ingredientId"]) != int:
                            isInvalid = True
                            isInvalidIngredient = True
                        # validate all given ingredients exist
                        elif ingredient["ingredientId"] not in existingIngredientIds:
                            isInvalid = True
                            isNonExistientIngredient = True
                        if "unitId" not in ingredient or ingredient["unitId"] == None or type(ingredient["unitId"]) != int:
                            isInvalid = True
                            isInvalidUnit = True
                        # validate all given units exist
                        elif ingredient["unitId"] not in existingUnitIds:
                            isInvalid = True
                            isNonExistientUnit = True
                        if "quantity" not in ingredient or ingredient["quantity"] == None or type(ingredient["quantity"]) != int:
                            isInvalid = True
                            isInvalidQuantity = True
                        if isInvalid:
                            errorMsg += "ingredients (list of dict { "
                            if isInvalidIngredient:
                                errorMsg += "ingredientId (int) "
                            elif isNonExistientIngredient:
                                errorMsg += "ingredientId (ID not valid) "
                            if isInvalidUnit:
                                errorMsg += "unitId (int) "
                            elif isNonExistientUnit:
                                errorMsg += "unitId (ID not valid) "
                            if isInvalidQuantity:
                                errorMsg += "quantity (int) "
                            errorMsg += "}) "
                            break
            if "instructions" not in value or value["instructions"] == None or type(value["instructions"]) != list:
                isInvalid = True
                errorMsg += "instructions (list) "
            else:
                for instruction in value["instructions"]:
                    if type(instruction) != str:
                        isInvalid = True
                        errorMsg += "instructions (list of str) "
                        break
            if "name" not in value or value["name"] == None or value["name"] == "" or type(value["name"]) != str:
                isInvalid = True
                errorMsg += "name (str) "
            if "calories" in value:
                calories = value["calories"]
                if type(calories) != int:
                    isInvalid = True
                    errorMsg += "calories (int) "
            else:
                calories = -1
            if "image_url" in value:
                image_url = value["image_url"]
                if type(image_url) != str:
                    isInvalid = True
                    errorMsg += "image_url (str) "
            else:
                image_url = ""
            if "time" in value:
                time = value["time"]
                if type(time) != int:
                    isInvalid = True
                    errorMsg += "time (int) "
            else:
                time = -1
            errorMsg += "(optional: calories (int) image_url (str) time (int))"

            if isInvalid:
                raise Exception
            errorMsg = "No recipe added."
            queries.addRecipe(db, user['idToken'], calories, image_url, value["ingredients"], value["instructions"], value["name"], time)
            return True
        except:
            abort(400, errorMsg)
        finally:
            apiQueryLock.release()

    def put(self, id):
        apiQueryLock.acquire()
        value = request.get_data()

        try:
            errorMsg = "Invalid JSON"
            value = json.loads(value)

            # validate there are fields for ingredients (list), instructions (list), name (str) (optional: calories (int) image_url (str) time (int))
            isInvalid = False
            errorMsg = "Please fix the following values: "

            if "ingredients" not in value or value["ingredients"] == None or not value["ingredients"] or type(value["ingredients"]) != list:
                isInvalid = True
                errorMsg += "ingredients (list of dict { ingredientId (int), unitId (int), quantity (int) }) "
            else:
                existingIngredients = queries.getAllIngredients(db, user['idToken'])
                existingIngredientIds = [ingredient["id"] for ingredient in existingIngredients]
                existingUnits = queries.getAllUnits(db, user['idToken'])
                existingUnitIds = [unit["id"] for unit in existingUnits]

                for ingredient in value["ingredients"]:
                    if type(ingredient) != dict:
                        isInvalid = True
                        errorMsg += "ingredients (list of dict { ingredientId (int), unitId (int), quantity (int) }) "
                        break
                    # validate list of objects each given an ingredientId, unitId, and quantity
                    else:
                        isInvalidIngredient = False
                        isNonExistientIngredient = False
                        isInvalidUnit = False
                        isNonExistientUnit = False
                        isInvalidQuantity = False

                        if "ingredientId" not in ingredient or ingredient["ingredientId"] == None or type(ingredient["ingredientId"]) != int:
                            isInvalid = True
                            isInvalidIngredient = True
                        # validate all given ingredients exist
                        elif ingredient["ingredientId"] not in existingIngredientIds:
                            isInvalid = True
                            isNonExistientIngredient = True
                        if "unitId" not in ingredient or ingredient["unitId"] == None or type(ingredient["unitId"]) != int:
                            isInvalid = True
                            isInvalidUnit = True
                        # validate all given units exist
                        elif ingredient["unitId"] not in existingUnitIds:
                            isInvalid = True
                            isNonExistientUnit = True
                        if "quantity" not in ingredient or ingredient["quantity"] == None or type(ingredient["quantity"]) != int:
                            isInvalid = True
                            isInvalidQuantity = True
                        if isInvalid:
                            errorMsg += "ingredients (list of dict { "
                            if isInvalidIngredient:
                                errorMsg += "ingredientId (int) "
                            elif isNonExistientIngredient:
                                errorMsg += "ingredientId (ID not valid) "
                            if isInvalidUnit:
                                errorMsg += "unitId (int) "
                            elif isNonExistientUnit:
                                errorMsg += "unitId (ID not valid) "
                            if isInvalidQuantity:
                                errorMsg += "quantity (int) "
                            errorMsg += "}) "
                            break
            if "instructions" not in value or value["instructions"] == None or type(value["instructions"]) != list:
                isInvalid = True
                errorMsg += "instructions (list) "
            else:
                for instruction in value["instructions"]:
                    if type(instruction) != str:
                        isInvalid = True
                        errorMsg += "instructions (list of str) "
                        break
            if "name" not in value or value["name"] == None or value["name"] == "" or type(value["name"]) != str:
                isInvalid = True
                errorMsg += "name (str) "
            if "calories" in value:
                calories = value["calories"]
                if type(calories) != int:
                    isInvalid = True
                    errorMsg += "calories (int) "
            else:
                calories = -1
            if "image_url" in value:
                image_url = value["image_url"]
                if type(image_url) != str:
                    isInvalid = True
                    errorMsg += "image_url (str) "
            else:
                image_url = ""
            if "time" in value:
                time = value["time"]
                if type(time) != int:
                    isInvalid = True
                    errorMsg += "time (int) "
            else:
                time = -1
            errorMsg += "(optional: calories (int) image_url (str) time (int))"

            if isInvalid:
                raise Exception
            errorMsg = "No recipe updated."
            queries.updateRecipe(db, user['idToken'], id, calories, image_url, value["ingredients"], value["instructions"], value["name"], time)
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

        try:
            errorMsg = "Invalid JSON"
            value = json.loads(value)

            # validate there is a field for email (str) name (str) (optional: recipes (list))
            isInvalid = False
            errorMsg = "Please fix the following values: "

            if "email" not in value or value["email"] == None or value["email"] == "" or type(value["email"]) != str:
                isInvalid = True
                errorMsg += "email (str) "
            if "name" not in value or value["name"] == None or value["name"] == "" or type(value["name"]) != str:
                isInvalid = True
                errorMsg += "name (str) "
            if "recipes" in value:
                recipes = value["recipes"]
                if type(recipes) != list:
                    isInvalid = True
                    errorMsg += "recipes (list) "
                else:
                    # validate given recipes exist
                    existingRecipes = queries.getAllRecipes(db, user['idToken'])
                    existingRecipeIds = [recipe["id"] for recipe in existingRecipes]
                    for recipeId in recipes:
                        if type(recipeId) != int:
                            isInvalid = True
                            errorMsg += "recipes (list of int) "
                            break
                        if recipeId not in existingRecipeIds:
                            isInvalid = True
                            errorMsg += "recipes (recipe ID not valid) "
                            break
            else:
                recipes = []
            errorMsg += "(optional: recipes (list))"

            if isInvalid:
                raise Exception
            errorMsg = "No user added."
            queries.addUser(db, user['idToken'], value["email"], value["name"], recipes)
            return True
        except:
            abort(400, errorMsg)
        finally:
            apiQueryLock.release()

    def put(self, id):
        apiQueryLock.acquire()
        value = request.get_data()

        try:
            errorMsg = "Invalid JSON"
            value = json.loads(value)

            # validate there is a field for email (str) name (str) (optional: recipes (list))
            isInvalid = False
            errorMsg = "Please fix the following values: "

            if "email" not in value or value["email"] == None or value["email"] == "" or type(value["email"]) != str:
                isInvalid = True
                errorMsg += "email (str) "
            if "name" not in value or value["name"] == None or value["name"] == "" or type(value["name"]) != str:
                isInvalid = True
                errorMsg += "name (str) "
            if "recipes" in value:
                recipes = value["recipes"]
                if type(recipes) != list:
                    isInvalid = True
                    errorMsg += "recipes (list) "
                else:
                    # validate given recipes exist
                    existingRecipes = queries.getAllRecipes(db, user['idToken'])
                    existingRecipeIds = [recipe["id"] for recipe in existingRecipes]
                    for recipeId in recipes:
                        if type(recipeId) != int:
                            isInvalid = True
                            errorMsg += "recipes (list of int) "
                            break
                        if recipeId not in existingRecipeIds:
                            isInvalid = True
                            errorMsg += "recipes (recipe ID not valid) "
                            break
            else:
                recipes = []
            errorMsg += "(optional: recipes (list))"

            if isInvalid:
                raise Exception
            errorMsg = "No user updated."
            queries.updateUser(db, user['idToken'], id, value["email"], value["name"], recipes)
            return True
        except:
            abort(400, errorMsg)
        finally:
            apiQueryLock.release()

class Units(Resource):
    def get(self, id=None):
        apiQueryLock.acquire()
        try:
            if id == None:
                # get all unit
                return queries.getAllUnits(db, user['idToken'])
            else:
                # get specific unit
                return queries.getUnit(db, user['idToken'], id)          
        except:
            abort(400, "No unit exists.")
        finally:
            apiQueryLock.release()

class Grocery(Resource):
    def get(self, id):
        apiQueryLock.acquire()
        try:
            # get specific user's grocery list
            return queries.getUserGroceryList(db, user['idToken'], id)            
        except:
            abort(400, "No user exists.")
        finally:
            apiQueryLock.release()

api.add_resource(Ingredients, '/RecipesPlusPlus/ingredients/', '/RecipesPlusPlus/ingredients/<int:id>/')
api.add_resource(Recipes, '/RecipesPlusPlus/recipes/', '/RecipesPlusPlus/recipes/<int:id>/')
api.add_resource(Users, '/RecipesPlusPlus/users/', '/RecipesPlusPlus/users/<int:id>/')
api.add_resource(Units, '/RecipesPlusPlus/units/', '/RecipesPlusPlus/units/<int:id>/')
api.add_resource(Grocery, '/RecipesPlusPlus/users/<int:id>/grocery')
app.add_url_rule('/favicon.ico', view_func = lambda: functions.favicon(parentDir))
app.run(host='0.0.0.0', port=5001)