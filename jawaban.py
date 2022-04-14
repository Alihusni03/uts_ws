# 6A / 19090052 / Akhmad Ali Husni Fauzan
# 6A / 19090002 / M. Ade Noval Firmansyah
# 6A / 19090070 / Fikriyah Khairunnisa
# 6A / 19090054 / Dwi indah Fitria Sari



from distutils.log import Log
import os

from datetime import datetime
from flask import Flask
from flask import request
from flask import jsonify
from flask_httpauth import HTTPTokenAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "jawaban.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)
auth = HTTPTokenAuth(scheme='Bearer')

class User(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    token = db.Column(db.String(225), unique=True, nullable=True)
class events(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    event_creator = db.Column(db.String(20))
    event_name = db.Column(db.String(20))
    event_start_time = db.Column(db.Date)
    event_end_time = db.Column(db.Date)
    event_start_lat = db.Column(db.String(20))
    event_finish_lat = db.Column(db.String(20))
    event_finish_lng = db.Column(db.String(20))
    event_start_lng = db.Column(db.String(20))
    event_created_at = db.Column(db.Date,default=datetime.now())
class log(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(20))
    event_name = db.Column(db.String(20))
    log_lat = db.Column(db.String(20))
    log_lng = db.Column(db.String(20))
    created_at = db.Column(db.Date,default=datetime.now())
    
db.create_all()
@app.route("/api/v1/user/create", methods=["POST"])
def create():
    username= request.json["username"]
    password= request.json["password"]
    
    newusers = User(username=username,password=password)
    db.session.add(newusers)
    db.session.commit()
    return jsonify({"msg" : "Registrasi sukses"})

@app.route("/api/v1/login", methods=["POST"])
def login():
    username= request.json['username']
    password= request.json['password']
    S=10
    user=User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))
        user.token= token
        db.session.commit()
    return jsonify({
        "msg": "Login Berhasil",
        "status": 200,
        "token": token,
    })
@auth.verify_token
def verify_token(token):
    user=User.query.filter_by(token=token).first() 
    return user.keterangan 
@app.route("/api/v2/users/info", methods=["POST"])
@auth.login_required
def info():
    return "Hai, {}!".format(auth.current_user())
@app.route("/api/v1/events/create", methods=["POST"])
def event():
    token = request.json["token"]
    
    token = User.query.filter_by(token=token).first()
    if token:
        
        event_creator = token.username
        event_name = request.json['event_name']
        event_start_time = request.json['event_start_time']
        event_end_time = request.json['event_end_time']
        event_start_lat = request.json['event_start_lat']
        event_finish_lat = request.json['event_finish_lat']
        event_start_lng = request.json['event_start_lng']
        event_finish_lng = request.json['event_finish_lng']
        
        event_start_time = datetime.strptime(event_start_time, '%Y-%m-%d %H:%M:%S')
        event_end_time = datetime.strptime(event_end_time, '%Y-%m-%d %H:%M:%S')
        
        newEvents = events(event_start_time=event_start_time, event_end_time=event_end_time, event_creator=event_creator, event_name=event_name, event_start_lat=event_start_lat, event_finish_lat=event_finish_lat, event_start_lng=event_start_lng, event_finish_lng=event_finish_lng)
        
        db.session.add(newEvents)
        db.session.commit()
        
        return jsonify({
            'msg' : 'membuat event sukses'
        })
@app.route("/api/v1/events/log", methods=["POST"])
def event_log():
    token = request.json['token']
    
    token = User.query.filter_by(token=token).first()
    
    if token:
        username = token.username
        event_name = request.json['event_name']
        log_lat = request.json['log_lat']
        log_lng = request.json['log_lng']
        
        newLogs = log(username=username,event_name=event_name,log_lat=log_lat,log_lng=log_lng)
        
        db.session.add(newLogs)
        db.session.commit()
        
        return jsonify({
            'msg' : 'sukses mencatat posisi terbaru'
        })
@app.route("/api/v1/events/logs", methods=["GET"])
def event_logs():
    
    token = request.json['token']
    
    token = User.query.filter_by(token=token).first()
    if token:
    
        username = token.username
        event_name = request.json['event_name']
        
        logs_event =log.query.filter_by(event_name=event_name).all()
        
        logs_status = []
        
        for logg in logs_event:
            dict_logs = {}
            dict_logs.update({"username": logg.username, "event_name": logg.event_name, "log_lat": logg.log_lat, "log_lng": logg.log_lng, "created_at": logg.created_at})
            logs_status.append(dict_logs)
        return jsonify(logs_status)
    
if __name__ == '__main__':
    app.run(debug = True, port=4004)