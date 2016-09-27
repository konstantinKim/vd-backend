from flask import Blueprint, request, jsonify, make_response
from app.auth.models import Auth, basic_auth
from app.haulers.models import Haulers
from flask_restful import Api, Resource
import json
import hashlib

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

auth = Blueprint('auth', __name__)
api = Api(auth)

class Authentiaction(Resource):                
    @basic_auth.login_required
    def get(self):                              
        token = Auth.login(request.authorization.username, request.authorization.password)        
        if not token:
            response = make_response("HTTP/1.1 401 Unauthorized", 401)            
            return (response)
        else:
            response = make_response(json.dumps(token))
            return (response)                

class SignUp(Resource):                    
    def get(self, token):       
        Auth.validateSignupToken(token)

    def post(self):
        try:
            params = request.form           
            token = params['token'].strip()
            password = params['password'].strip()
            print(token, password)
            HAULER_ID = Auth.validateSignupToken(params['token'])

            if HAULER_ID:
                hauler = Haulers.query.get_or_404(HAULER_ID)
                setattr(hauler, 'password', password)
                hauler.update()
                token = Auth.setToken(HAULER_ID)                            
                if token:
                    response = make_response(json.dumps(token))
                    return (response)                   

            response = make_response("HTTP/1.1 403 Forbidden", 403)            
            return (response)

        except ValidationError as err:
                resp = jsonify({"error": err.messages})
                resp.status_code = 403
                return resp               
                
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 403
                return resp 

        except ValueError as e:
                resp = jsonify({"error": str(e)})
                resp.status_code = 403
                resp.statusText = str(e)
                return resp 


api.add_resource(Authentiaction, '.json')
#api.add_resource(SignUp, '/signup/<token>.json')
api.add_resource(SignUp, '/signup.json')