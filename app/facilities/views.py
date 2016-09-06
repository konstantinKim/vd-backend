from flask import Blueprint, request, jsonify, make_response
from app.facilities.models import Facilities, FacilitiesSchema, FacilitiesMaterials, db
from flask_restful import Api, Resource


 
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

facilities = Blueprint('facilities', __name__)

schema = FacilitiesSchema()
api = Api(facilities)

class FacilitiesList(Resource):                
    def get(self):        
        query = Facilities.query.filter().all()        
        results = schema.dump(query, many=True).data
        return results                

class FacilitiesMaterialList(Resource):                
    def get(self, material_id):        
        query = Facilities.query.filter().all()        
        results = schema.dump(query, many=True).data
        return results                        

api.add_resource(FacilitiesList, '.json')
api.add_resource(FacilitiesMaterialList, '/material/<int:material_id>.json')