from flask import Blueprint, request, jsonify, make_response
from app.ticketsRd.models import TicketsRd, TicketsRdSchema, db
from app.materials.models import MaterialsSchema
from flask_restful import Api, Resource
from app.auth.models import token_auth, Security

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

tickets_rd_bp = Blueprint('tickets_rd', __name__)

schema = TicketsRdSchema()
api = Api(tickets_rd_bp)

class TicketsRdList(Resource):
    @token_auth.login_required
    def get(self):                
        return (1)

    @token_auth.login_required
    def post(self):                   
        raw_dict = {"data": {"attributes": request.form, "type": "tickets_rd"}}        
        file = request.files
        print(file)
        print(request.headers)
        print(raw_dict)
        try:
                schema.validate(raw_dict)
                params = raw_dict['data']['attributes']                
                ticket = TicketsRd(ticket=params['ticket'], PROJECT_ID=params['PROJECT_ID'], HAULER_ID=Security.getHaulerId())
                ticket.add(ticket)                                
                query = TicketsRd.query.get(ticket.TICKET_RD_ID)                
                results = schema.dump(query).data                
                material = query.material
                if material:
                    material = MaterialsSchema().dump(query.material).data
                    material = material['data']['attributes']['name']
                else:    
                    material = '' 

                results['data']['attributes']['material'] = material
                return results['data']['attributes'], 201
            
        except ValidationError as err:
                resp = jsonify({"error": err.messages})
                resp.status_code = 403
                return resp               
                
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 403
                return resp
        


api.add_resource(TicketsRdList, '.json')
