from pymongo import MongoClient
import flask
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import datetime as DT
import hashlib
import urllib


client = MongoClient('mongodb+srv://kevinujunior:191210051@cluster0.onmj24e.mongodb.net/?retryWrites=true&w=majority')


DB = client.xenon
USERS = DB.users
CONTACT = DB.contact
app = flask.Flask(__name__)
jwt = JWTManager(app) 
app.config['JWT_SECRET_KEY'] = '38dd56f56d405e02ec0ba4be4adu89ab'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = DT.timedelta(days=1) 


@app.route("/signup", methods=["POST"])
def signup():
    new_user = flask.request.json 
    new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() 
    doc = USERS.find_one({"username": new_user["username"]}) 
    if not doc:
        USERS.insert_one(new_user)
        return flask.jsonify({'message': 'User created successfully'}), 201
    else:
        return flask.jsonify({"success":False,'message': 'User already exists'}), 409
   
   

@app.route("/login", methods=["POST"])
def login():
    login_details = flask.request.json 
    user_from_db = USERS.find_one({'username': login_details['username']})  
    if user_from_db:
        encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrpted_password == user_from_db['password']:
            access_token = create_access_token(identity=user_from_db['username'])
            return flask.jsonify(access_token=access_token), 200
    return flask.jsonify({"success":False,'message': 'Incorrect credentials'}), 401



@app.route("/contact", methods=["POST"])
@jwt_required()
def contact():
    user = get_jwt_identity()
    user_from_db = USERS.find_one({'username' : user})
    if user_from_db:
        req = flask.request.json
        username = user_from_db["username"]
        query = req["query"]
        timestamp = int(DT.datetime.now().timestamp())
        obj = {
            "username" : username,
            "query" : query,
            "timestamp" : timestamp
        }
        CONTACT.insert_one(obj)
        return flask.jsonify({"success":True,"message" : "Query created Successfully"})
    return flask.jsonify({"success":False,'message': 'Incorrect credentials'}), 401


@app.route("/get_user_queries", methods=["POST"])
@jwt_required()
def get_user_queries():
    user = get_jwt_identity()
    user_from_db = USERS.find_one({'username' : user})
    if user_from_db:
        user_template = {'username' : user_from_db["username"]}
        #_id:0 means this field will be excluded
        return flask.jsonify({"success":True,"message":list(CONTACT.find(user_template, {"_id":0}))}), 200
    return flask.jsonify({"success":False,'message': 'Incorrect credentials'}), 401


if __name__ == "__main__":
    app.run(debug=True)

