from flask import Blueprint, request, jsonify, make_response
from app.haulers.models import Haulers, HaulersSchema, db, auth
from flask_restful import Api, Resource
 
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

haulers = Blueprint('haulers', __name__)
# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
#https://github.com/marshmallow-code/marshmallow-jsonapi
schema = HaulersSchema()
api = Api(haulers)

# Users
class HaulersList(Resource):            
    @auth.login_required
    def get(self):        
        query = Haulers.query.all()        
        results = schema.dump(query, many=True).data        
        return results                    

api.add_resource(HaulersList, '.json')