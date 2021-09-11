from flask_restful import Resource

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