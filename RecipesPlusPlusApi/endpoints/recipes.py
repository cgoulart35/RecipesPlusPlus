from flask_restful import Resource

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