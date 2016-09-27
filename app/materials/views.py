from flask import Blueprint, request, jsonify, make_response
from app.materials.models import Materials, MaterialsSchema, MaterialsSalvage, MaterialsSalvageSchema, db
from flask_restful import Api, Resource


 
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

materials = Blueprint('materials', __name__)

schema = MaterialsSchema()
salvageSchema = MaterialsSalvageSchema()
api = Api(materials)

class MaterialsList(Resource):                
    def get(self):        
        query = Materials.query.filter(Materials.cn_id < 1, Materials.pt_id < 1).all()        
        results = schema.dump(query, many=True).data
        return results                

class MaterialsSalvageList(Resource):                
    def get(self):        
        query = MaterialsSalvage.query.all()        
        results = salvageSchema.dump(query, many=True).data
        return results                        

api.add_resource(MaterialsList, '.json')
api.add_resource(MaterialsSalvageList, '/salvage.json')