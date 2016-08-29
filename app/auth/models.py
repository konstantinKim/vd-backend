from flask import request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from app.haulers.models import Haulers, HaulersSchema, db
from config import SECRET_KEY

jwt = JWT(SECRET_KEY, expires_in=3600)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')    

@basic_auth.verify_password
def verify_password(username, password):
    hauler = Haulers.query.with_entities(Haulers.password, Haulers.HAULER_ID).filter_by(email = username).first()
    if  hauler and len(password) and check_password_hash(generate_password_hash(hauler.password), password):        
        return True
    return False

@token_auth.verify_token
def verify_token(token):        
    try:
        data = jwt.loads(token)
    except:
        return False
    if 'HAULER_ID' in data:        
        return True
    return False

class Auth():    
    def find_between( s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""
        
    def login(username, password):
        hauler = Haulers.query.with_entities(Haulers.password, Haulers.HAULER_ID).filter_by(email = username).first()
        if  hauler and len(password) and check_password_hash(generate_password_hash(hauler.password), password):
            user_token = jwt.dumps( {'HAULER_ID':  hauler.HAULER_ID} )                        
            return Auth.find_between( str(user_token), "'", "'" )
        return False

class Security():
    def getHaulerId():              
        access_token = request.headers.get('authorization')
        if access_token:
            access_token = access_token.replace('Bearer', '').strip()
            if len(access_token):
                data = jwt.loads(access_token)
                if 'HAULER_ID' in data:
                    return data['HAULER_ID']
        return false            