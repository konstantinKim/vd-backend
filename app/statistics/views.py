from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from app.auth.models import token_auth, Security
from app.statistics.models import Statistics

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

statistics = Blueprint('statistics', __name__)

api = Api(statistics)

class RecyclingTotals(Resource):    
    @token_auth.login_required
    def get(self, dateFrom, dateTo):                                        
        Stats = Statistics(dateFrom = dateFrom, dateTo = dateTo)
        recyclingTotals = Stats.recyclingTotals()                
                        
        return(recyclingTotals.__dict__)

class CarbonFootprint(Resource):    
    @token_auth.login_required
    def get(self, dateFrom, dateTo):                                        
        Stats = Statistics(dateFrom = dateFrom, dateTo = dateTo)
        carbonFootprint = Stats.carbonFootprint()                
                        
        return(carbonFootprint.__dict__)        \

class MaterialsRecycled(Resource):    
    @token_auth.login_required
    def get(self, dateFrom, dateTo):                                        
        Stats = Statistics(dateFrom = dateFrom, dateTo = dateTo)
        data = Stats.materialsRecycled()                
                        
        return(data.__dict__)                

class FacilitiesUsed(Resource):    
    @token_auth.login_required
    def get(self, dateFrom, dateTo):                                        
        Stats = Statistics(dateFrom = dateFrom, dateTo = dateTo)
        data = Stats.facilitiesUsed()                
                        
        return(data.__dict__)                        

class ProjectTypes(Resource):    
    @token_auth.login_required
    def get(self, dateFrom, dateTo):                                        
        Stats = Statistics(dateFrom = dateFrom, dateTo = dateTo)
        data = Stats.projectTypes()                
                        
        return(data.__dict__)                                

class BuildingTypes(Resource):    
    @token_auth.login_required
    def get(self, dateFrom, dateTo):                                        
        Stats = Statistics(dateFrom = dateFrom, dateTo = dateTo)
        data = Stats.buildingTypes()                
                        
        return(data.__dict__)                                        

class HaulingTypes(Resource):    
    @token_auth.login_required
    def get(self, dateFrom, dateTo):                                        
        Stats = Statistics(dateFrom = dateFrom, dateTo = dateTo)
        data = Stats.haulingTypes()                
                        
        return(data.__dict__)                                                

api.add_resource(RecyclingTotals, '/recycling_totals/<dateFrom>/<dateTo>.json')
api.add_resource(CarbonFootprint, '/carbon_footprint/<dateFrom>/<dateTo>.json')
api.add_resource(MaterialsRecycled, '/materials/<dateFrom>/<dateTo>.json')
api.add_resource(FacilitiesUsed, '/facilities/<dateFrom>/<dateTo>.json')
api.add_resource(ProjectTypes, '/projects/<dateFrom>/<dateTo>.json')
api.add_resource(BuildingTypes, '/buildings/<dateFrom>/<dateTo>.json')
api.add_resource(HaulingTypes, '/hauling/<dateFrom>/<dateTo>.json')
