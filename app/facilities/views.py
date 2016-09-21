from flask import Blueprint, request, jsonify, make_response
from app.facilities.models import Facilities, FacilitiesSchema, FacilitiesMaterials, db
from flask_restful import Api, Resource
from app.auth.models import token_auth, Security


 
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

facilities = Blueprint('facilities', __name__)

schema = FacilitiesSchema()
api = Api(facilities)

class FacilitiesList(Resource):                
    @token_auth.login_required
    def get(self):        
        query = Facilities.query.filter().all()        
        results = schema.dump(query, many=True).data
        return results                

class FacilitiesMaterialList(Resource):                
    @token_auth.login_required
    def get(self, city_id, material_id, project_id):        
        #query = Facilities.query.filter().all()        
        #results = schema.dump(query, many=True).data
        #print(material_id)
        query = db.engine.execute("SELECT DISTINCT(facilities.FACILITY_ID), facilities.* FROM facilities, cities_facilities, facilities_materials "+
          "WHERE facilities.FACILITY_ID=cities_facilities.FACILITY_ID "+
          "AND cities_facilities.CITY_ID=" + str(city_id) + " " +
          "AND facilities.CONTRACTOR_ID < 1 "+
          "AND facilities.FACILITY_ID=facilities_materials.FACILITY_ID "+
          "AND facilities_materials.MATERIAL_ID=" + str(material_id) + " ORDER BY name ASC")
        results = schema.dump(query, many=True).data

        query = db.engine.execute("SELECT DISTINCT(facilities.FACILITY_ID), facilities.* FROM facilities, projects_facilities, facilities_materials \
        WHERE facilities.FACILITY_ID=facilities_materials.FACILITY_ID AND facilities_materials.MATERIAL_ID=" + str(material_id) + " \
        AND facilities.FACILITY_ID=projects_facilities.FACILITY_ID \
        AND projects_facilities.PROJECT_ID=" + str(project_id) + " ORDER BY name ASC")                

        results['selected_facilities'] = schema.dump(query, many=True).data
                
        return results                        

api.add_resource(FacilitiesList, '.json')
api.add_resource(FacilitiesMaterialList, '/city/<int:city_id>/material/<int:material_id>/project/<int:project_id>.json')