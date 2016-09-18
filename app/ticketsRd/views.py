from flask import Blueprint, request, jsonify, make_response
from app.ticketsRd.models import TicketsRd, TicketsRdSchema, db
from app.materials.models import MaterialsSchema
from app.facilities.models import FacilitiesSchema
from flask_restful import Api, Resource
from app.auth.models import token_auth, Security
import time

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

tickets_rd_bp = Blueprint('tickets_rd', __name__)

schema = TicketsRdSchema()
api = Api(tickets_rd_bp)

class TicketsRdList(Resource):    
    def get(self):                
        folder = TicketsRd.get_folder('ticket', '881RD')
        print(folder)

        return(1)

    @token_auth.login_required
    def post(self):                   
        raw_dict = {"data": {"attributes": request.form, "type": "tickets_rd"}}                
        try:
                schema.validate(raw_dict)                                
                params = raw_dict['data']['attributes']                                            
                
                ticket = TicketsRd(                    
                    PROJECT_ID=params['PROJECT_ID'],
                    MATERIAL_ID=params['MATERIAL_ID'],
                    FACILITY_ID=params['FACILITY_ID'],
                    ticket=params['ticket'], 
                    thedate=params['thedate'],                    
                    weight=params['weight'],
                    recycled=params['weight'],
                    percentage=params['percentage'],
                    rate_used=100,
                    submitted_by=params['submitted_by'],
                    units=params['units'],
                    HAULER_ID=Security.getHaulerId(),
                )
                ticket.add(ticket)                                

                file = request.files['image']
                ticket.save_file(file)

                query = TicketsRd.query.get(ticket.TICKET_RD_ID)                
                results = schema.dump(query).data                
                
                #Set Material Name
                material = query.material
                if material:
                    material = MaterialsSchema().dump(material).data
                    material = material['data']['attributes']['name']
                else:    
                    material = '' 

                results['data']['attributes']['material'] = material

                #Set Facility Name
                facility = query.facility
                if facility:
                    facility = FacilitiesSchema().dump(facility).data
                    facility = facility['data']['attributes']['name']
                else:    
                    facility = '' 

                results['data']['attributes']['facility'] = facility
                results['data']['attributes']['image'] = ticket.get_folder(True) + "ticket.jpg"
                split_date = results['data']['attributes']['thedate'].split('T')
                results['data']['attributes']['thedate'] = split_date[0]
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

class TicketsRdUpdate(Resource):
    @token_auth.login_required
    def patch(self, id):
        HAULER_ID = Security.getHaulerId()        
        ticket = TicketsRd.query.filter(TicketsRd.TICKET_RD_ID==id, TicketsRd.HAULER_ID==HAULER_ID).first_or_404()
        raw_dict = {"data": {"attributes": request.form, "type": "tickets_rd"}}                

        try:            
            schema.validate(raw_dict)                        
            params = raw_dict['data']['attributes']                        
            
            for key, value in params.items():                
                setattr(ticket, key, value)            

            ticket.update()                                                          
            
            if 'image' in request.files:
                file = request.files['image']
                ticket.save_file(file)            
            
            query = TicketsRd.query.get(ticket.TICKET_RD_ID)                
            results = schema.dump(query).data

            #Set Material Name
            material = query.material
            if material:
                material = MaterialsSchema().dump(material).data
                material = material['data']['attributes']['name']
            else:    
                material = '' 

            results['data']['attributes']['material'] = material

            #Set Facility Name
            facility = query.facility
            if facility:
                facility = FacilitiesSchema().dump(facility).data
                facility = facility['data']['attributes']['name']
            else:    
                facility = '' 

            results['data']['attributes']['facility'] = facility
            results['data']['attributes']['image'] = ticket.get_folder(True) + "ticket.jpg?v=" + str(time.time())
            split_date = results['data']['attributes']['thedate'].split('T')
            results['data']['attributes']['thedate'] = split_date[0]
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

    def delete(self, id):
        HAULER_ID = Security.getHaulerId()        
        ticket = TicketsRd.query.filter(TicketsRd.TICKET_RD_ID==id, TicketsRd.HAULER_ID==HAULER_ID).first_or_404()
        try:
            delete = ticket.delete(ticket)
            response = make_response()
            response.status_code = 204
            return response
            
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 401
                return resp


api.add_resource(TicketsRdList, '.json')
api.add_resource(TicketsRdUpdate, '/<int:id>.json')
