from flask import Blueprint, request, jsonify, make_response
from app.auth.models import Auth, basic_auth, token_auth, Security
from app.haulers.models import Haulers, HaulersSchema
from app.helper.helper import Format
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
            HAULER_ID = Security.getHaulerId(token)        
            query = Haulers.query.get_or_404(HAULER_ID)
            results = HaulersSchema().dump(query).data
            data = { 'token': token, 'HAULER_ID': results['data']['attributes']['HAULER_ID'], 'email': results['data']['attributes']['email'], 'contact': results['data']['attributes']['contact'], 'company': results['data']['attributes']['name']} 
            response = make_response(json.dumps(data))
            return (response)                

class SignUp(Resource):                    
    def get(self, token):       
        Auth.validateSignupToken(token)

    def post(self):
        try:
            params = request.form           
            token = params['token'].strip()
            password = params['password'].strip()            
            HAULER_ID = Auth.validateSignupToken(params['token'])
            print('----------------------------------------------------')
            print(token, password, HAULER_ID)

            if HAULER_ID:
                hauler = Haulers.query.get_or_404(HAULER_ID)
                setattr(hauler, 'password', password)
                hauler.update()

                hauler = Haulers.query.get_or_404(HAULER_ID)
                setattr(hauler, 'password', password)
                hauler.update()
                
                token = Auth.setToken(HAULER_ID)                            
                if token:
                    results = HaulersSchema().dump(hauler).data
                    data = { 'token': token, 'HAULER_ID': results['data']['attributes']['HAULER_ID'], 'email': results['data']['attributes']['email'], 'contact': results['data']['attributes']['contact'], 'company': results['data']['attributes']['name']} 
                    response = make_response(json.dumps(data))
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

class UserData(Resource):                
    @token_auth.login_required
    def get(self):                              
        HAULER_ID = Security.getHaulerId()        
        query = Haulers.query.get_or_404(HAULER_ID)
        results = HaulersSchema().dump(query).data        
        
        results['data']['attributes']['phone_1'] = ''
        results['data']['attributes']['phone_2'] = ''
        results['data']['attributes']['phone_3'] = ''
        results['data']['attributes']['phone_4'] = ''
        formatPhone = Format.phone(results['data']['attributes']['phone'])
        if 'phone_1' in formatPhone:
            results['data']['attributes']['phone_1'] = formatPhone['phone_1']
        if 'phone_2' in formatPhone:
            results['data']['attributes']['phone_2'] = formatPhone['phone_2']
        if 'phone_3' in formatPhone:
            results['data']['attributes']['phone_3'] = formatPhone['phone_3']    
        if 'phone_4' in formatPhone:
            results['data']['attributes']['phone_4'] = formatPhone['phone_4']    


        #data = { 'HAULER_ID': results['data']['attributes']['HAULER_ID'], 'email': results['data']['attributes']['email'], 'contact': results['data']['attributes']['contact'], 'company': results['data']['attributes']['name']} 
        #response = make_response(json.dumps(data))        
        
        return (results['data']['attributes'])                        
        #return (response)
                        
class ConfirmSignUp(Resource):                    
    def get(self, token):       
        try:
            HAULER_ID = Auth.validateSignupToken(token)
            if HAULER_ID:
                hauler = Haulers.query.get_or_404(HAULER_ID)
                results = HaulersSchema().dump(hauler).data
                data = { 'token': token, 'HAULER_ID': results['data']['attributes']['HAULER_ID'], 'email': results['data']['attributes']['email'], 'contact': results['data']['attributes']['contact'], 'company': results['data']['attributes']['name']} 
                response = make_response(json.dumps(data))
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
api.add_resource(UserData, '/data.json')
api.add_resource(SignUp, '/signup.json')
api.add_resource(ConfirmSignUp, '/confirm_signup/<token>.json')
