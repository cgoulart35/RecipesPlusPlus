def getAllIngredients(db, token):
    result = db.child("ingredients").get(token)
    if result.val() == None:
        raise Exception
    ingredients = result.val()
    if isinstance(ingredients, dict):
        return sorted(ingredients.values(), key=lambda ingredient: ingredient["id"])
    else:
        return sorted(ingredients, key=lambda ingredient: ingredient["id"])

def getNextIngredientId(db, token):
    try:
        ingredients = getAllIngredients(db, token)
        ids = [ingredient["id"] for ingredient in ingredients]
        return min(set(range(0, max(ids) + 2)) - set(ids))
    except:
        return 0

def getIngredient(db, token, ingredientId):
    result = db.child("ingredients").order_by_child("id").equal_to(ingredientId).get(token)
    if not result.val():
        raise Exception
    return result[0].val()

def removeIngredient(db, token, ingredientId):
    # if ingredient doesn't exist throw an exception
    result = db.child("ingredients").order_by_child("id").equal_to(ingredientId).get(token)
    if not result.val():
        raise Exception

    # get database table list index of the ingredient
    index = result[0].item[0]

    # attempt delete on existing ingredient
    db.child("ingredients").child(index).remove(token)
    
    # if ingredient still exists then throw exception
    try:
        getIngredient(db, token, ingredientId)
        raise Exception
    #if ingredient doesn't exist then successfully deleted
    except:
        return

def addIngredient(db, token, name, image_url):
    id = getNextIngredientId(db, token)
    ingredient = {"id": id, "image_url": image_url, "name": name}
    db.child("ingredients").push(ingredient)

    # if ingredient doesn't exist throw an exception
    getIngredient(db, token, id)

def updateIngredient(db, token, ingredientId, name, image_url):
    result = db.child("ingredients").order_by_child("id").equal_to(ingredientId).get(token)
    if not result.val():
        raise Exception

    db.child("ingredients").child(result[0].key()).update({"image_url": image_url, "name": name})

    # if ingredient doesn't exist throw an exception
    getIngredient(db, token, ingredientId)

def isIngredientBeingUsed(db, token, ingredientId):
    recipes = getAllRecipes(db, token)
    for recipe in recipes:
        ingredientIds = [ingredient["ingredientId"] for ingredient in recipe["ingredients"]]
        if ingredientId in ingredientIds:
            return True
    return False

def getAllRecipes(db, token):
    result = db.child("recipes").get(token)
    if result.val() == None:
        raise Exception
    recipes = result.val()
    if isinstance(recipes, dict):
        return sorted(recipes.values(), key=lambda recipe: recipe["id"])
    else:
        return sorted(recipes, key=lambda recipe: recipe["id"])

def getNextRecipeId(db, token):
    try:
        recipes = getAllRecipes(db, token)
        ids = [recipe["id"] for recipe in recipes]
        return min(set(range(0, max(ids) + 2)) - set(ids))
    except:
        return 0

def getRecipe(db, token, recipeId):
    result = db.child("recipes").order_by_child("id").equal_to(recipeId).get(token)
    if not result.val():
        raise Exception
    return result[0].val()

def removeRecipe(db, token, recipeId):
    # if recipe doesn't exist throw an exception
    result = db.child("recipes").order_by_child("id").equal_to(recipeId).get(token)
    if not result.val():
        raise Exception

    # get database table list index of the recipe
    index = result[0].item[0]

    # attempt delete on existing recipe
    db.child("recipes").child(index).remove(token)
    
    # if recipe still exists then throw exception
    try:
        getRecipe(db, token, recipeId)
        raise Exception
    #if recipe doesn't exist then successfully deleted
    except:
        return

def addRecipe(db, token, calories, image_url, ingredients, instructions, name, time):
    id = getNextRecipeId(db, token)
    recipe = {"calories": calories, "id": id, "image_url": image_url, "ingredients": ingredients, "instructions": instructions, "name": name, "time": time}
    db.child("recipes").push(recipe)
    
    # if recipe doesn't exist throw an exception
    getRecipe(db, token, id)

def updateRecipe(db, token, recipeId, calories, image_url, ingredients, instructions, name, time):
    result = db.child("recipes").order_by_child("id").equal_to(recipeId).get(token)
    if not result.val():
        raise Exception

    db.child("recipes").child(result[0].key()).update({"calories": calories, "image_url": image_url, "ingredients": ingredients, "instructions": instructions, "name": name, "time": time})

    # if recipe doesn't exist throw an exception
    getRecipe(db, token, recipeId)

def isRecipeBeingUsed(db, token, recipeId):
    users = getAllUsers(db, token)
    for user in users:
        if recipeId in user["recipes"]:
            return True
    return False

def getAllUsers(db, token):
    result = db.child("users").get(token)
    if result.val() == None:
        raise Exception
    users = result.val()
    if isinstance(users, dict):
        return sorted(users.values(), key=lambda user: user["id"])
    else:
        return sorted(users, key=lambda user: user["id"])

def getNextUserId(db, token):
    try:
        users = getAllUsers(db, token)
        ids = [user["id"] for user in users]
        return min(set(range(0, max(ids) + 2)) - set(ids))
    except:
        return 0

def getUser(db, token, userId):
    result = db.child("users").order_by_child("id").equal_to(userId).get(token)
    if not result.val():
        raise Exception
    return result[0].val()

def removeUser(db, token, userId):
    # if user doesn't exist throw an exception
    result = db.child("users").order_by_child("id").equal_to(userId).get(token)
    if not result.val():
        raise Exception

    # get database table list index of the user
    index = result[0].item[0]

    # attempt delete on existing user
    db.child("users").child(index).remove(token)
    
    # if user still exists then throw exception
    try:
        getUser(db, token, userId)
        raise Exception
    #if user doesn't exist then successfully deleted
    except:
        return

def addUser(db, token, email, name, recipes):
    id = getNextUserId(db, token)
    user = {"email": email, "id": id, "name": name, "recipes": recipes}
    db.child("users").push(user)

    # if user doesn't exist throw an exception
    getUser(db, token, id)

def updateUser(db, token, userId, email, name, recipes):
    result = db.child("users").order_by_child("id").equal_to(userId).get(token)
    if not result.val():
        raise Exception

    db.child("users").child(result[0].key()).update({"email": email, "name": name, "recipes": recipes})

    # if user doesn't exist throw an exception
    getUser(db, token, userId)

def getAllUnits(db, token):
    result = db.child("units").get(token)
    if result.val() == None:
        raise Exception
    units = result.val()
    if isinstance(units, dict):
        return sorted(units.values(), key=lambda unit: unit["id"])
    else:
        return sorted(units, key=lambda unit: unit["id"])

def getUnit(db, token, unitId):
    result = db.child("units").order_by_child("id").equal_to(unitId).get(token)
    if not result.val():
        raise Exception
    return result[0].val()

def getUserGroceryList(db, token, userId):
    groceryList = []
    
    user = getUser(db, token, userId)
    recipeIds = user["recipes"]

    for recipeId in recipeIds:
        recipe = getRecipe(db, token, recipeId)
        ingredientQuantities = recipe["ingredients"]

        for ingredientQuantity in ingredientQuantities:
            ingredient = getIngredient(db, token, ingredientQuantity["ingredientId"])
            unit = getUnit(db, token, ingredientQuantity["unitId"])
            quantity = ingredientQuantity["quantity"]
            
            ingredientAdded = False
            for groceryItem in groceryList:
                if groceryItem["ingredient"]["id"] == ingredient["id"] and groceryItem["unit"]["id"] == unit["id"]:
                    groceryItem["quantity"] += quantity
                    ingredientAdded = True
                    break

            if not ingredientAdded:
                newGroceryItem = { "ingredient": ingredient, "unit": unit, "quantity": quantity }
                groceryList.append(newGroceryItem)

    return groceryList 
