from flask import Blueprint, request, jsonify, make_response
from app.ticketsSr.models import TicketsSr, TicketsSrSchema, db
from app.projects.models import syncProject
from app.materials.models import MaterialsSchema
from app.facilities.models import FacilitiesSchema
from flask_restful import Api, Resource
from app.auth.models import token_auth, Security
import time
import os
import datetime

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

tickets_sr_bp = Blueprint('tickets_sr', __name__)

schema = TicketsSrSchema()
api = Api(tickets_sr_bp)

class TicketsSrList(Resource):        

    @token_auth.login_required
    def post(self):                   
        raw_dict = {"data": {"attributes": request.form, "type": "tickets_sr"}}                
        try:                        
            schema.validate(raw_dict)                                                
            params = raw_dict['data']['attributes']                                                                                

            if not len(params['inventory']):
                raise ValueError("Please choose salvage materials")

            _FACILITY_ID = 0
            _ticket = ''
            _thedate_ticket = datetime.datetime.today().strftime('%Y-%m-%d')
            if params['CONSTRUCTION_TYPE_ID'] == '18':                                                
                _FACILITY_ID = params['FACILITY_ID']
                _ticket =  params['ticket']
                _thedate_ticket = params['thedate_ticket']                                    
            
            ticket = TicketsSr(                    
                PROJECT_ID=params['PROJECT_ID'],
                MATERIAL_ID=7,
                CONSTRUCTION_TYPE_ID=params['CONSTRUCTION_TYPE_ID'],
                FACILITY_ID=_FACILITY_ID,
                ticket=_ticket, 
                weight=params['weight'],
                description=params['description'],                                    
                thedate_ticket=_thedate_ticket,                    
                submitted_by=params['submitted_by'],                    
                percentage=params['percentage'],                                                        
                inventory=params['inventory'],                                                        
                HAULER_ID=Security.getHaulerId(),
            )            
                        
            ticket.validateDate()  
            ticket.setRecyclingRates(params)
            ticket.add(ticket)
            ticket.sendLargeTicketNotification()                                

            if 'image' in request.files:
                file = request.files['image']
                ticket.save_file(file, 'ticket')

            if 'material_image_1' in request.files:                
                ticket.save_file(request.files['material_image_1'], 'material')            

            if 'material_image_2' in request.files:                
                file = request.files['material_image_2']
                ticket.save_file(file, 'material2')

            if 'material_image_3' in request.files:                
                file = request.files['material_image_3']
                ticket.save_file(file, 'material3')

            if 'material_image_4' in request.files:                
                file = request.files['material_image_4']
                ticket.save_file(file, 'material4')

            query = TicketsSr.query.get(ticket.TICKET_SR_ID)                
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

            #Set Salvage Materials
            inventory = []
            if ticket.inventory:
                inventoryQuery = db.engine.execute("SELECT name FROM materials_salvage "+
                    "WHERE MATERIAL_SALVAGE_ID IN("+str(ticket.inventory)+")")

                salvage_materials = inventoryQuery.fetchall()
                
                for m in salvage_materials:
                    inventory.append(m.name)                        
            
            results['data']['attributes']['salvage_materials'] = ', '.join(inventory)
            results['data']['attributes']['units'] = 'tons'

            if ticket.CONSTRUCTION_TYPE_ID == 18:
                results['data']['attributes']['name'] = 'Donated';
            if ticket.CONSTRUCTION_TYPE_ID == 17:
                results['data']['attributes']['name'] = 'Reuse OnSite';    
            if ticket.CONSTRUCTION_TYPE_ID == 19:
                results['data']['attributes']['name'] = 'Salvage for reuse on other project';    
            
            folder = ticket.get_folder()
            if os.path.isfile(folder + 'ticket.jpg'):
                results['data']['attributes']['image'] = ticket.get_folder(True) + "ticket.jpg"
            else:
                results['data']['attributes']['image'] = ''                

            if os.path.isfile(folder + 'material.jpg'):
                results['data']['attributes']['material_image'] = ticket.get_folder(True) + "material.jpg"
            else:
                results['data']['attributes']['material_image'] = ''                                

            if os.path.isfile(folder + 'material2.jpg'):
                results['data']['attributes']['material_image2'] = ticket.get_folder(True) + "material2.jpg"
            else:
                results['data']['attributes']['material_image2'] = ''                                

            if os.path.isfile(folder + 'material3.jpg'):
                results['data']['attributes']['material_image3'] = ticket.get_folder(True) + "material3.jpg"
            else:
                results['data']['attributes']['material_image3'] = ''                                

            if os.path.isfile(folder + 'material4.jpg'):
                results['data']['attributes']['material_image4'] = ticket.get_folder(True) + "material4.jpg"
            else:
                results['data']['attributes']['material_image4'] = ''                                
                        
            split_date = results['data']['attributes']['thedate_ticket'].split('T')
            results['data']['attributes']['thedate_ticket'] = split_date[0]

            syncProject(ticket.PROJECT_ID)
            db.session.commit()
            
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

        except ValueError as e:
            resp = jsonify({"error": str(e)})
            resp.status_code = 403
            resp.statusText = str(e)
            return resp

class TicketsSrUpdate(Resource):
    @token_auth.login_required
    def patch(self, id):        
        HAULER_ID = Security.getHaulerId()        
        ticket = TicketsSr.query.filter(TicketsSr.TICKET_SR_ID==id, TicketsSr.HAULER_ID==HAULER_ID).first_or_404()
        raw_dict = {"data": {"attributes": request.form, "type": "tickets_sr"}}                

        try:                                
            schema.validate(raw_dict)                                    
            params = raw_dict['data']['attributes']                                                
            for key, value in params.items():                    
                setattr(ticket, key, value)                            
                        
            ticket.validateDate()
            ticket.setRecyclingRates(params)
            ticket.update()
            db.session.commit()                                                          
            
            if 'image' in request.files:
                file = request.files['image']
                ticket.save_file(file)            

            if 'material_image_1' in request.files:                
                ticket.save_file(request.files['material_image_1'], 'material')            

            if 'material_image_2' in request.files:                
                file = request.files['material_image_2']
                ticket.save_file(file, 'material2')

            if 'material_image_3' in request.files:                
                file = request.files['material_image_3']
                ticket.save_file(file, 'material3')

            if 'material_image_4' in request.files:                
                file = request.files['material_image_4']
                ticket.save_file(file, 'material4')    
            
            query = TicketsSr.query.get(ticket.TICKET_SR_ID)                
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

            #Set Salvage Materials
            inventory = []
            if ticket.inventory:
                inventoryQuery = db.engine.execute("SELECT name FROM materials_salvage "+
                    "WHERE MATERIAL_SALVAGE_ID IN("+str(ticket.inventory)+")")

                salvage_materials = inventoryQuery.fetchall()
                
                for m in salvage_materials:
                    inventory.append(m.name)                        
            
            results['data']['attributes']['salvage_materials'] = ', '.join(inventory)
            results['data']['attributes']['units'] = 'tons'

            if ticket.CONSTRUCTION_TYPE_ID == 18:
                results['data']['attributes']['name'] = 'Donated';
            if ticket.CONSTRUCTION_TYPE_ID == 17:
                results['data']['attributes']['name'] = 'Reuse OnSite';    
            if ticket.CONSTRUCTION_TYPE_ID == 19:
                results['data']['attributes']['name'] = 'Salvage for reuse on other project';    
            
            folder = ticket.get_folder()
            if os.path.isfile(folder + 'ticket.jpg'):
                results['data']['attributes']['image'] = ticket.get_folder(True) + "ticket.jpg"
            else:
                results['data']['attributes']['image'] = ''                

            if os.path.isfile(folder + 'material.jpg'):
                results['data']['attributes']['material_image'] = ticket.get_folder(True) + "material.jpg"
            else:
                results['data']['attributes']['material_image'] = ''                                

            if os.path.isfile(folder + 'material2.jpg'):
                results['data']['attributes']['material_image2'] = ticket.get_folder(True) + "material2.jpg"
            else:
                results['data']['attributes']['material_image2'] = ''                                

            if os.path.isfile(folder + 'material3.jpg'):
                results['data']['attributes']['material_image3'] = ticket.get_folder(True) + "material3.jpg"
            else:
                results['data']['attributes']['material_image3'] = ''                                

            if os.path.isfile(folder + 'material4.jpg'):
                results['data']['attributes']['material_image4'] = ticket.get_folder(True) + "material4.jpg"
            else:
                results['data']['attributes']['material_image4'] = ''                                
                        
            split_date = results['data']['attributes']['thedate_ticket'].split('T')
            results['data']['attributes']['thedate_ticket'] = split_date[0]

            syncProject(ticket.PROJECT_ID)
            db.session.commit()
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

        except ValueError as e:
                resp = jsonify({"error": str(e)})
                resp.status_code = 403
                resp.statusText = str(e)
                return resp        

    @token_auth.login_required
    def delete(self, id):                
        HAULER_ID = Security.getHaulerId()
        ticket = TicketsSr.query.filter(TicketsSr.TICKET_SR_ID==id, TicketsSr.HAULER_ID==HAULER_ID).first_or_404()
        try:            
            delete = ticket.delete(ticket)            
            syncProject(ticket.PROJECT_ID)
            db.session.commit()
            response = make_response()
            response.status_code = 204
            return response
            
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


api.add_resource(TicketsSrList, '.json')
api.add_resource(TicketsSrUpdate, '/<int:id>.json')
