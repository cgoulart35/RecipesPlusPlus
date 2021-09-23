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
