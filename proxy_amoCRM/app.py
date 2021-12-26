# -*- coding: utf-8 -*-
import html
from flask import Flask,request, render_template, session, make_response,redirect
from flask_cors import CORS, cross_origin
import requests
import json
from OpenSSL import SSL
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime,timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PATH'
app.secret_key = ''

app.permanent_session_lifetime = timedelta(days=60)
db = SQLAlchemy(app)

PROTO = ''
IP = ''
PORT = ''
URL = ''
USER_1C = ''
PASSWORD_1C = ''

'''WEB ИНТЕРФЕЙС'''
@app.route('/', methods=['GET','POST'])
def main():

    if request.method == 'GET':

        if 'tokenAuth' in session and checkAuth(session['tokenAuth']):
            return render_template('index.html')
        else:
            return render_template('login.html')
        
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if checkUser(username,password):
            return render_template('index.html')
        else:
            return render_template('login.html')

@app.route('/logs', methods=['GET'])
@app.route('/logs/<int:page_id>', methods=['GET'])
def listLogs(page_id = 1):

    if 'tokenAuth' in session and checkAuth(session['tokenAuth']):
        paginate = getReguest(page_id)
        listpage = []
        for i in range(1,paginate.pages):
            listpage.append(i)

        return render_template('logs.html', rowRequest = paginate.items, listpage = listpage, curent_page = page_id)
    else:
        return render_template('login.html')

@app.route('/exit', methods=['GET','POST'])
def exit():

    if request.method == 'GET':

        if 'tokenAuth' in session and checkAuth(session['tokenAuth']):
            killSession(session['tokenAuth'])

            return redirect('/')
        
@app.route('/users/<int:page_id>', methods=['GET'])
@app.route('/users', methods=['GET','POST'])
def users(page_id = 1):

    if request.method == 'GET':

        if 'tokenAuth' in session and checkAuth(session['tokenAuth']):
            paginate = getUsers(page_id)
            listpage = []
            for i in range(1,paginate.pages):
                listpage.append(i)

            return render_template('users.html', rowRequest = paginate.items, listpage = listpage, curent_page = page_id)
        else:
            return redirect('/')
    elif request.method == 'POST':
        if 'tokenAuth' in session and checkAuth(session['tokenAuth']):
            
            dataForm = {'name':request.form.get('username'),
                'password':request.form.get('password'),
                'confirm': request.form.get('passwordConfirm')
            }
            
            addUser(dataForm)

            paginate = getUsers(page_id)
            listpage = []
            for i in range(1,paginate.pages):
                listpage.append(i)

            return render_template('users.html', rowRequest = paginate.items, listpage = listpage, curent_page = page_id)
        else:
            return redirect('/')

@app.route('/settings_1c', methods=['GET','POST'])
def settings_1C():

    if request.method == 'GET':

        if 'tokenAuth' in session and checkAuth(session['tokenAuth']):
            data_settings = getSettings1C()

            return render_template('settings_1C.html', data_settings = data_settings)
    elif request.method == 'POST':
        if 'tokenAuth' in session and checkAuth(session['tokenAuth']):
            dateForm = {'PROTO': request.form.get('PROTO'),
                'IP' : request.form.get('IP'),
                'PORT':request.form.get('PORT'),
                'URL': request.form.get('URL'),
                'USER_1C': request.form.get('USER_1C'),
                'PASSWORD_1C': request.form.get('PASSWORD')
                }
            saveSettings(dateForm)
            
            data_settings = getSettings1C()
            return render_template('settings_1C.html', data_settings = data_settings, info = 'Данные обнавлены')


'''WEB ИНТЕРФЕЙС'''



'''API ИНТЕРФЕЙС'''
@app.route('/API/get_doctor_time', methods=['POST'])
@cross_origin()
def API():
    fl = True
    

    str_data = request.data.decode('utf8')

    try:
        my_json = json.loads(str_data)
        token = my_json['token']
        date = my_json['date']
    except:
        jsonSend = json.dumps({'Error': 'error format Json'})
        addRecLog(request,'/API/get_doctor_time',False,jsonSend)
        return jsonSend

    if checkToken(token):
        jsonData = json.dumps({'Date': date})
        DataPost = SendPostTo_1c(jsonData)
        jsonSend = json.dumps(json.loads(DataPost))
    else:
        jsonSend = json.dumps({'Error': 'Invalid token'})
        fl = False
    
    addRecLog(request,'/API/get_doctor_time',fl,jsonSend)
    return jsonSend


@app.route('/API/cretate_document', methods=['POST'])
@cross_origin()
def API_CreateDocument():

    fl = True
    
    token = ''
    date = '00010101'

    str_data = request.data.decode('utf8')
    try:
        my_json = json.loads(str_data)
        token       = my_json['token']
        date        = my_json['date']
        numberAmo   = my_json['numberAmo']
        doctor      = my_json['doctor']
        time        = my_json['time']
        customer    = my_json['customer']
        tel         = my_json['tel']
        gender      = my_json['gender']
        dateofBirth = my_json['DateofBirth']
    except:
        jsonSend = json.dumps({'Error': 'error format Json'})
        addRecLog(request,'/API/cretate_document',fl,jsonSend)

        return jsonSend
    
    if checkToken(token):
        jsonData = json.dumps({'Date': date,'NumberAmo':numberAmo, 
                                'Doctor': doctor,'Time': time,'Customer': customer,
                                'Tel': tel, 'Gender': gender, 'DateofBirth': dateofBirth})
        DataPost = SendPostCreateDocumetnTo_1C(jsonData)
        jsonSend = json.dumps(json.loads(DataPost))
    else:
        jsonSend = json.dumps({'Error': 'Invalid token'})
        fl = False

    
    addRecLog(request,'/API/cretate_document',fl,jsonSend)
    
    return jsonSend
 
'''API ИНТЕРФЕЙС'''

def SendPostTo_1c(jsonData):
    
    url = ''.join([PROTO,'://',IP,':',PORT,URL,'GetTimeDoctors'])

    response = requests.post(url,auth=(USER_1C,PASSWORD_1C),data=jsonData)
    
    return response.content.decode('utf-8')

def SendPostCreateDocumetnTo_1C(jsonData):
    
    url = ''.join([PROTO,'://',IP,':',PORT,URL,'CreateDocument'])

    response = requests.post(url,auth=(USER_1C,PASSWORD_1C),data=jsonData)
    
    return response.content.decode('utf-8')
    
def checkToken(token):
    
    TokenDB = db.session.query(Token).first()
    
    if TokenDB.token_value == token:
        return True
    else:
        return False

def checkUser(user,passwd):
    
    objUser = db.session.query(Users).filter(Users.name == user).first()
 
    if check_password_hash(objUser.password,passwd) == False:
        return False
    else:
        newToken = str(uuid.uuid1())

        objToken = TokenSession(user = objUser.id, token = newToken)
        db.session.add(objToken)
        db.session.commit()
        
        session['tokenAuth'] = {'UserId': objUser.id, 'Token': newToken}
        return True

def checkAuth(tokenAuth):
    if tokenAuth is None:
        return False

    token = tokenAuth['Token']
    UserId = tokenAuth['UserId']
    objToken = db.session.query(TokenSession).filter(TokenSession.user == UserId and TokenSession.token == token).first()
    if objToken is None:
        return False
    valid = objToken.created_on + timedelta(60)
    
    if valid > datetime.now():
        return True
    else:
        db.session.delete(objToken)
        db.session.commit()

        return False
    
def addRecLog(request,path,err,jsonSend):
    agent_client = str(request.user_agent)
    ip_client    = request.remote_addr
    
    rec = Logs(agent = agent_client, ip = ip_client, path = path, err = err, json = str(json.loads(jsonSend)))
    db.session.add(rec)
    db.session.commit()

def killSession(tokenAuth):
    token = tokenAuth['Token']
    UserId = tokenAuth['UserId']
    
    objToken = db.session.query(TokenSession).filter(TokenSession.user == UserId and TokenSession.token == token).first()
    
    if objToken is not None:
        db.session.delete(objToken)
        db.session.commit()
        session['tokenAuth'] = None
        
def getReguest(page):
    return db.session.query(Logs).paginate(page, 10, False)
    
def getUsers(page):
    return db.session.query(Users).paginate(page, 10, False)

def addUser(dataFrom):
    
    
    countUser = db.session.query(Users).filter(Users.name == dataFrom['name']).count()
    if countUser == 0:
        hash  = generate_password_hash(dataFrom['password'])
        objUser = Users(name = dataFrom['name'], password = hash)
        db.session.add(objUser)
        db.session.commit()

def getSettings1C():
    objSettings = db.session.query(Settings).first()
    if objSettings is not None:
        return json.loads(objSettings.value)
    else:
        return {'PROTO': PROTO,
            'IP':IP,
            'PORT':PORT,
            'URL':URL,
            'USER_1C':USER_1C,
            'PASSWORD_1C':PASSWORD_1C,
        }

def saveSettings(dictForm):

    obj1C = db.session.query(Settings).filter(Settings.name == '1C').all()
    dataJson = obj1C[0].value
    obj1C[0].value = json.dumps(dictForm)
    db.session.commit()
    
'''
MODELS
'''

class Logs(db.Model):
    __tablename__ = 'logs'
    id         = db.Column(db.Integer(), primary_key=True)
    ip         = db.Column(db.String(255), nullable=False)
    agent      = db.Column(db.String(255), nullable=False)
    path       = db.Column(db.String(255), nullable=False)
    err        = db.Column(db.Boolean, default=False, nullable=False)
    json       = db.Column(db.String(512), nullable=False)    
    created_on = db.Column(db.DateTime(), default=datetime.now)

class Users(db.Model):
    __tablename__ = 'users'
    id           = db.Column(db.Integer(), primary_key=True)
    name         = db.Column(db.String(255), nullable=False)
    password     = db.Column(db.String(255), nullable=False)
    created_on   = db.Column(db.DateTime(), default=datetime.utcnow)
    tokensession = db.relationship('TokenSession', backref='users')

class Token(db.Model):
    __tablename__ = 'token'
    id           = db.Column(db.Integer(), primary_key=True)
    token_value  = db.Column(db.String(512), nullable=False)
    created_on   = db.Column(db.DateTime(), default=datetime.utcnow)

class Settings(db.Model):
    __tablename__ = 'Settings'
    id           = db.Column(db.Integer(), primary_key=True)
    name         = db.Column(db.String(1024), nullable=False)
    value        = db.Column(db.String(1024), nullable=False)
    created_on   = db.Column(db.DateTime(), default=datetime.utcnow)

class TokenSession(db.Model):
    __tablename__ = 'token_session'
    id           = db.Column(db.Integer(), primary_key=True)
    user         = db.Column(db.Integer(), db.ForeignKey('users.id'))
    token        = db.Column(db.String(512), nullable=False)    
    created_on   = db.Column(db.DateTime(), default=datetime.utcnow)

'''
MODELS
'''

db.create_all()

def initDefaultSettings():
    
    #админская учетка для web
    countRoot = db.session.query(Users).filter(Users.name == 'root').count()
    if countRoot == 0:
        hash  = generate_password_hash('*')
        objUser = Users(name = 'root', password = hash)
        db.session.add(objUser)
        db.session.commit()
    
    #Token
    countToken = db.session.query(Token).count()
    if countToken == 0:
        vToken = '*'
        objToken = Token(token_value = vToken)
        db.session.add(objToken)
        db.session.commit()



    #1C connect
    global PROTO, IP, PORT, URL, USER_1C, PASSWORD_1C


    count1C = db.session.query(Settings).filter(Settings.name == '1C').count()
    if count1C == 0:
        PROTO       = 'http'
        IP          = 'localhost'
        PORT        = '8000'
        URL         = '/name_base/hs/service/'
        USER_1C     = 'USER_1C'
        PASSWORD_1C = 'PAssword_1C'

        data_1C = {'PROTO': PROTO,
            'IP':IP,
            'PORT':PORT,
            'URL':URL,
            'USER_1C':USER_1C,
            'PASSWORD_1C':PASSWORD_1C,
        }

        jsonData = json.dumps(data_1C)
        obj1CSettings = Settings(name = '1C', value = jsonData)
        db.session.add(obj1CSettings)
        db.session.commit()
    else:
        

        obj1C = db.session.query(Settings).filter(Settings.name == '1C').all()
        dataJson = obj1C[0].value
        
        dict1C = json.loads(dataJson)
        PROTO       = dict1C['PROTO']
        IP          = dict1C['IP']
        PORT        = dict1C['PORT']
        URL         = dict1C['URL']
        USER_1C     = dict1C['USER_1C']
        PASSWORD_1C = dict1C['PASSWORD_1C']
  

initDefaultSettings()

context = ('cert.pem', 'key.pem')

app.run(debug=False,host='0.0.0.0', port='5000', ssl_context=context)
