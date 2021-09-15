def getIngredient(db, token, ingredientId):
    return db.child("ingredients").order_by_child("id").equal_to(ingredientId).limit_to_first(1).get(token).val()

#def setIngredient(db, token, ingredientId, value):
    # push obj to list

def getRecipe(db, token, recipeId):
    return db.child("recipes").order_by_child("id").equal_to(recipeId).limit_to_first(1).get(token).val()

#def setRecipe(db, token, recipeId, value):
    # push obj to list

def getUser(db, token, userId):
    return db.child("users").order_by_child("id").equal_to(userId).limit_to_first(1).get(token).val()

#def setUser(db, token, userId, value):
    # push obj to list