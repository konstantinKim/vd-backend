from flask import Blueprint, request, jsonify, make_response
from app.auth.models import Auth, basic_auth
from flask_restful import Api, Resource
import json

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

api.add_resource(Authentiaction, '.json')