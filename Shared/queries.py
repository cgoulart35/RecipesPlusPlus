def getAllIngredients(db, token):
    result = db.child("ingredients").get(token)
    if result.val() == None:
        raise Exception
    return result.val()

def getIngredient(db, token, ingredientId):
    result = db.child("ingredients").order_by_child("id").equal_to(ingredientId).get(token)
    if result.val() == None:
        raise Exception
    return result[0].val()

#def setIngredient(db, token, ingredientId, value):
    # push obj to list

def getAllRecipes(db, token):
    result = db.child("recipes").get(token)
    if result.val() == None:
        raise Exception
    return result.val()

def getRecipe(db, token, recipeId):
    result = db.child("recipes").order_by_child("id").equal_to(recipeId).get(token)
    if result.val() == None:
        raise Exception
    return result[0].val()

#def setRecipe(db, token, recipeId, value):
    # push obj to list

def getAllUsers(db, token):
    result = db.child("users").get(token)
    if result.val() == None:
        raise Exception
    return result.val()

def getUser(db, token, userId):
    result = db.child("users").order_by_child("id").equal_to(userId).get(token)
    if result.val() == None:
        raise Exception
    return result[0].val()

#def setUser(db, token, userId, value):
    # push obj to list