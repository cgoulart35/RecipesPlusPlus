import json
import pyrebase
import importlib.util
import pathlib
import requests
from configparser import ConfigParser
from flask import Blueprint, session, render_template, request, redirect, url_for

views = Blueprint(__name__, "views")

# get parent directory and dependencies
parentDir = str(pathlib.Path(__file__).parent.parent.absolute())
parentDir = parentDir.replace("\\",'/')

spec = importlib.util.spec_from_file_location('shared', parentDir + '/Shared/functions.py')
functions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(functions)

# get configuration variables
appConfig = ConfigParser()
appConfig.read('RecipesPlusPlusWebApp/app.ini')
sharedConfig = functions.buildSharedConfig(parentDir)

# initialize firebase and database
firebaseConfig = json.loads(sharedConfig['properties']['firebaseConfigJson'])
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()

@views.route("/")
@views.route("/home/")
def home():
    if "data" in session:
        return render_template("home.html", session = session, home = "active", ingredients = "inactive", recipes = "inactive", groceries = "inactive", profile = "inactive")
    else:
        return redirect(url_for("views.login"))

@views.route("/ingredients/")
def ingredients():
    if "data" in session:
        return render_template("ingredients.html", session = session, home = "inactive", ingredients = "active", recipes = "inactive", groceries = "inactive", profile = "inactive")
    else:
        return redirect(url_for("views.login"))

@views.route("/recipes/")
def recipes():
    if "data" in session:
        return render_template("recipes.html", session = session, home = "inactive", ingredients = "inactive", recipes = "active", groceries = "inactive", profile = "inactive")
    else:
        return redirect(url_for("views.login"))

@views.route("/groceries/")
def groceries():
    if "data" in session:
        return render_template("groceries.html", session = session, home = "inactive", ingredients = "inactive", recipes = "inactive", groceries = "active", profile = "inactive")
    else:
        return redirect(url_for("views.login"))

@views.route("/profile/")
def profile():
    if "data" in session:
        return render_template("profile.html", session = session, home = "inactive", ingredients = "inactive", recipes = "inactive", groceries = "inactive", profile = "active")
    else:
        return redirect(url_for("views.login"))

@views.route("/login/", methods = ["GET", "POST"])
def login():
    if "data" in session:
        return redirect(url_for("views.home"))
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.sign_in_with_email_and_password(email, password)

            response = requests.get(f"{appConfig['properties']['apiHost']}/users")
            profiles = json.loads(response.content)
            profile = next((profile for profile in profiles if profile["email"] == email), None)

            sessionData = {"user": user, "profile": profile}

            session['data'] = sessionData
            return redirect(url_for("views.home"))
        except:
            pass;       
        
    return render_template("login.html", home = "inactive", ingredients = "inactive", recipes = "inactive", groceries = "inactive", profile = "inactive")

@views.route("/signup/", methods = ["GET", "POST"])
def signup():
    if "data" in session:
        return redirect(url_for("views.home"))
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        try:
            response = requests.get(f"{appConfig['properties']['apiHost']}/users")
            profiles = json.loads(response.content)
            profile = next((profile for profile in profiles if profile["email"] == email), None)

            if profile == None:
                response = requests.post(f"{appConfig['properties']['apiHost']}/users", data = json.dumps({"email": email, "name": name}))
                response = requests.get(f"{appConfig['properties']['apiHost']}/users")
                profiles = json.loads(response.content)
                profile = next((profile for profile in profiles if profile["email"] == email), None)

                user = auth.create_user_with_email_and_password(email, password)

                sessionData = {"user": user, "profile": profile}
                print(sessionData)

                session['data'] = sessionData
                return redirect(url_for("views.home"))
        except:
            pass;   

    return redirect(url_for("views.login"))

@views.route("/logout/")
def logout():
    session.pop("data", None)
    return redirect(url_for("views.login"))


# @views.route("/profile/<id>")
# def profile(id):
#     # gets us query params
#     args = request.args
#     name = args.get('name')
#     return render_template("index.html", name = "Chris")

# @views.route("/goHome")
# def go_to_home():
#     # use func name in url_for()
#     return redirect(url_for("views.home"))