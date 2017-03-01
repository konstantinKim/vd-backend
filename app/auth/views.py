from flask import Blueprint, request, jsonify, make_response
from app.auth.models import Auth, basic_auth, token_auth, Security
from app.haulers.models import Haulers, HaulersSchema, db
from app.representative.models import Representative, RepresentativeSchema
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
            db.session.commit()            
            return (response)
        else:
            HAULER_ID = Security.getHaulerId(token)        
            query = Haulers.query.get_or_404(HAULER_ID)
            results = HaulersSchema().dump(query).data
            data = { 'token': token, 'HAULER_ID': results['data']['attributes']['HAULER_ID'], 'email': results['data']['attributes']['email'], 'contact': results['data']['attributes']['contact'], 'company': results['data']['attributes']['name']} 
            db.session.commit()
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

            if HAULER_ID:
                hauler = Haulers.query.get_or_404(HAULER_ID)
                setattr(hauler, 'password', password)
                hauler.update()
                
                hauler = Haulers.query.get_or_404(HAULER_ID)
                setattr(hauler, 'password', password)                
                hauler.update()
                
                token = Auth.setToken(HAULER_ID)                            
                if token:
                    db.engine.execute("UPDATE haulers SET updated_at=NOW() WHERE HAULER_ID="+ str(HAULER_ID) + "")                                  
                    results = HaulersSchema().dump(hauler).data
                    data = { 'token': token, 'HAULER_ID': results['data']['attributes']['HAULER_ID'], 'email': results['data']['attributes']['email'], 'contact': results['data']['attributes']['contact'], 'company': results['data']['attributes']['name']} 
                    response = make_response(json.dumps(data))
                    db.session.commit()
                    return (response)
            else: # Reps
                REPS_ID = Auth.validateRepsSignupToken(token)
                if REPS_ID:
                    reps = Representative.query.get_or_404(REPS_ID)
                    setattr(reps, 'password', password)
                    reps.update()

                    reps = Representative.query.get_or_404(REPS_ID)
                    setattr(reps, 'password', password)
                    reps.update()

                    hauler = Haulers.query.get_or_404(reps.HAULER_ID)
                    token = Auth.setToken(hauler.HAULER_ID)
                    if token:                        
                        results = HaulersSchema().dump(hauler).data
                        data = { 'token': token, 'HAULER_ID': results['data']['attributes']['HAULER_ID'], 'email': reps.email, 'contact': results['data']['attributes']['contact'], 'company': results['data']['attributes']['name']} 
                        response = make_response(json.dumps(data))
                        db.session.commit()
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

        splitPermits = []
        if results['data']['attributes']['permits']:
            splitPermits = results['data']['attributes']['permits'].split(',')
        
        results['data']['attributes']['permits'] = []
        for permit in splitPermits:
            results['data']['attributes']['permits'].append({'name':permit.strip()})

        splitAssociations = []
        if results['data']['attributes']['associations']:
            splitAssociations = results['data']['attributes']['associations'].split(',')
        
        results['data']['attributes']['associations'] = []
        for ass in splitAssociations: #)
            results['data']['attributes']['associations'].append({'name':ass.strip()})                   

        reps = []
        query = db.engine.execute("SELECT email, id FROM haulers_representative WHERE HAULER_ID="+ str(HAULER_ID) + "")        
        #query = Representative.query.filter(Representative.HAULER_ID==HAULER_ID).all()        
        data = query.fetchall()
        if data:
            for rep in data:                                                        
                reps.append({'email': rep.email, 'id': rep.id})
        results['data']['attributes']['reps'] = reps
        
        db.session.commit()
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
                db.session.commit()
                return (response)
            else: #Reps                 
                REPS_ID = Auth.validateRepsSignupToken(token)
                if REPS_ID:
                    reps = Representative.query.get_or_404(REPS_ID)
                    hauler = Haulers.query.get_or_404(reps.HAULER_ID)
                    results = HaulersSchema().dump(hauler).data                    
                    data = { 'token': token, 'HAULER_ID': results['data']['attributes']['HAULER_ID'], 'email': reps.email, 'contact': results['data']['attributes']['contact'], 'company': results['data']['attributes']['name']} 
                    response = make_response(json.dumps(data))
                    db.session.commit()
                    return (response)                       

            response = make_response("HTTP/1.1 403 Forbidden", 403)
            db.session.commit()            
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

class AuthByToken(Resource):                    
    def get(self, token):       
        token = Auth.loginByToken(token)        
        if not token:
            response = make_response("HTTP/1.1 401 Unauthorized", 401)            
            db.session.commit()
            return (response)
        else:
            HAULER_ID = Security.getHaulerId(token)        
            query = Haulers.query.get_or_404(HAULER_ID)
            results = HaulersSchema().dump(query).data
            data = { 'token': token, 'HAULER_ID': results['data']['attributes']['HAULER_ID'], 'email': results['data']['attributes']['email'], 'contact': results['data']['attributes']['contact'], 'company': results['data']['attributes']['name']} 
            response = make_response(json.dumps(data))
            db.session.commit()
            return (response)                     


api.add_resource(Authentiaction, '.json')
api.add_resource(UserData, '/data.json')
api.add_resource(SignUp, '/signup.json')
api.add_resource(ConfirmSignUp, '/confirm_signup/<token>.json')
api.add_resource(AuthByToken, '/token_login/<token>.json')
