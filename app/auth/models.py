from flask import request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as JWT
from app.haulers.models import Haulers, HaulersSchema, db
from config import SECRET_KEY
import hashlib

jwt = JWT(SECRET_KEY, expires_in=3600)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')    

@basic_auth.verify_password
def verify_password(username, password):
    if len(username) > 0 and len(password) > 0:
        hauler = Haulers.query.with_entities(Haulers.password, Haulers.HAULER_ID).filter_by(email = username).first()
        if  hauler and check_password_hash(generate_password_hash(hauler.password), password):        
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

    def setToken(HAULER_ID):
        if not HAULER_ID:
            raise ValueError("Invalid Vendor ID")

        user_token = jwt.dumps( {'HAULER_ID':  HAULER_ID} )                        
        return Auth.find_between( str(user_token), "'", "'" )
        
    def login(username, password):
        if len(username) > 0 and len(password) > 0:
            hauler = Haulers.query.with_entities(Haulers.password, Haulers.HAULER_ID).filter_by(email = username).first()
            if  hauler and len(password) and check_password_hash(generate_password_hash(hauler.password), password):
                user_token = jwt.dumps( {'HAULER_ID':  hauler.HAULER_ID} )                        
                return Auth.setToken( hauler.HAULER_ID )
        return False

    def validateSignupToken(token):
        token = token.strip()
        if token:            
            key = "GH_VD_SECRET_vtE7p"            
            query = db.engine.execute("SELECT HAULER_ID, email, password FROM haulers WHERE MD5(CONCAT(HAULER_ID, email,'" + key + "')) = '"+ token +"'" )
            hauler = query.fetchone()            
            if hauler:                                
                if hauler.password:
                    raise ValueError("token expired, Vendor already has an account.")
                
                return(hauler.HAULER_ID)

        raise ValueError("Invalid token")

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