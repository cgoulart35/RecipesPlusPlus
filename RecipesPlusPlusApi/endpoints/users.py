from flask_restful import Resource

class Users(Resource):
    def get(self, id=None):
        if not id:
            # get all users
            return 1
        else:
            # get specific user
            return id
    def post(self):
        return
    def delete(self, id):
        return