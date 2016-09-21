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
        print(recyclingTotals)
        return(1)

api.add_resource(RecyclingTotals, '/recycling_totals/<dateFrom>/<dateTo>.json')
