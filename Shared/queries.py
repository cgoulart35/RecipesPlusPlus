
def getAllIngredients(db, token):
    result = db.child("ingredients").get(token)
    if result.val() == None:
        raise Exception
    ingredients = sorted(result.val(), key=lambda ingredient: ingredient["id"])
    return ingredients

def getNextIngredientId(db, token):
    ingredients = getAllIngredients(db, token)
    ids = [ingredient["id"] for ingredient in ingredients]
    return min(set(range(0, max(ids) + 2)) - set(ids))

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

#def setIngredient(db, token, ingredientId, value):
    # push obj to list

def getAllRecipes(db, token):
    result = db.child("recipes").get(token)
    if result.val() == None:
        raise Exception
    recipes = sorted(result.val(), key=lambda recipe: recipe["id"])
    return recipes

def getNextRecipeId(db, token):
    recipes = getAllRecipes(db, token)
    ids = [recipe["id"] for recipe in recipes]
    return min(set(range(0, max(ids) + 2)) - set(ids))

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

#def setRecipe(db, token, recipeId, value):
    # push obj to list

def getAllUsers(db, token):
    result = db.child("users").get(token)
    if result.val() == None:
        raise Exception
    users = sorted(result.val(), key=lambda user: user["id"])
    return users

def getNextUserId(db, token):
    users = getAllUsers(db, token)
    ids = [user["id"] for user in users]
    return min(set(range(0, max(ids) + 2)) - set(ids))

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

#def setUser(db, token, userId, value):
    # push obj to list
