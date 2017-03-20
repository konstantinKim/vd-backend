from flask import Blueprint, request, jsonify, make_response
from app.projects.models import Projects, ProjectsHaulers, ProjectsDebrisbox, ProjectsSchema, TicketsRd, db
from app.facilities.models import FacilitiesSchema
from app.ticketsRd.models import TicketsRdSchema
from app.ticketsSr.models import TicketsSrSchema
from app.materials.models import MaterialsSchema
from flask_restful import Api, Resource
from app.helper.helper import Calc
from app.auth.models import token_auth, Security
import json
import datetime
import os

from app.helper.phpserialize import *
from collections import OrderedDict

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

projects = Blueprint('projects', __name__)
# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
#https://github.com/marshmallow-code/marshmallow-jsonapi
schema = ProjectsSchema()
api = Api(projects)

def buildResult(query):    
    HAULER_ID = Security.getHaulerId()
    result = schema.dump(query).data
    print('================================')
    print(result)                        
    #group tickets by facility
    tf = {}
    m_ids = []
    tickets_count = 0
    total_weight = 0
    total_recycled = 0
    total_reused = 0
    for ticket in query.tickets:        
        ticketDump = TicketsRdSchema().dump(ticket).data                                
        if ticket.material and ticketDump['data']['attributes']['HAULER_ID'] == HAULER_ID:
            ticket_image = ticket.get_folder(True) + "ticket.jpg"
            tickets_count += 1
            material = MaterialsSchema().dump(ticket.material).data        
            material = material['data']['attributes']            
                        
            ticketDump = ticketDump['data']['attributes']
            ticketDump['material'] = material['name']
            ticketDump['image'] = ticket_image            
            split_date = ticketDump['thedate'].split('T')            
            ticketDump['thedate'] = split_date[0]
            
            if not material['MATERIAL_ID'] in m_ids:
                m_ids.append(material['MATERIAL_ID'])

            if not ticketDump['FACILITY_ID'] in tf:
                tf[ticketDump['FACILITY_ID']] = []
            
            tf[ticketDump['FACILITY_ID']].append(ticketDump)                
            total_weight += float(ticketDump['weight'])
            total_recycled += float(ticketDump['recycled'])

    reused_types_tickets = []
    donatedTickets = []
    reuseTickets = []
    salvageTickets = []
    for ticket_sr in query.tickets_sr:        
        ticketSrDump = TicketsSrSchema().dump(ticket_sr).data                                
        if ticket_sr.material and ticketSrDump['data']['attributes']['HAULER_ID'] == HAULER_ID:            
            ticketSrDump = ticketSrDump['data']['attributes']
            tickets_count += 1

            folder = ticket_sr.get_folder()
            if os.path.isfile(folder + 'ticket.jpg'):
                ticket_image = ticket_sr.get_folder(True) + "ticket.jpg"
            else:
                ticket_image = ''                
            if os.path.isfile(folder + 'material.jpg'):
                ticketSrDump['material_image'] = ticket_sr.get_folder(True) + "material.jpg"
            else:
                ticketSrDump['material_image'] = ''                                

            if os.path.isfile(folder + 'material2.jpg'):
                ticketSrDump['material_image2'] = ticket_sr.get_folder(True) + "material2.jpg"
            else:
                ticketSrDump['material_image2'] = ''                                

            if os.path.isfile(folder + 'material3.jpg'):
                ticketSrDump['material_image3'] = ticket_sr.get_folder(True) + "material3.jpg"
            else:
                ticketSrDump['material_image3'] = ''                                

            if os.path.isfile(folder + 'material4.jpg'):
                ticketSrDump['material_image4'] = ticket_sr.get_folder(True) + "material4.jpg"
            else:
                ticketSrDump['material_image4'] = ''                                            


            material = MaterialsSchema().dump(ticket_sr.material).data        
            material = material['data']['attributes']            

            if ticket_sr.facility:
                facility = FacilitiesSchema().dump(ticket_sr.facility).data                                    
                ticketSrDump['facility'] = facility['data']['attributes']['name']
            else:
                ticketSrDump['facility'] = ''

            inventory = []
            if ticket_sr.inventory:
                inventoryQuery = db.engine.execute("SELECT name FROM materials_salvage "+
                    "WHERE MATERIAL_SALVAGE_ID IN("+str(ticket_sr.inventory)+")")

                salvage_materials = inventoryQuery.fetchall()
                
                for m in salvage_materials:
                    inventory.append(m.name)                        
            
            ticketSrDump['salvage_materials'] = ', '.join(inventory)
            ticketSrDump['units'] = 'tons'            

            ticketSrDump['material'] = material['name']
            ticketSrDump['image'] = ticket_image            
            split_date = ticketSrDump['thedate_ticket'].split('T')            
            ticketSrDump['thedate_ticket'] = split_date[0]

            if not material['MATERIAL_ID'] in m_ids:
                m_ids.append(material['MATERIAL_ID'])                        
            
            if ticketSrDump['CONSTRUCTION_TYPE_ID'] == 18:
                donatedTickets.append(ticketSrDump)                
                ticketSrDump['name'] = 'Donated';

            if ticketSrDump['CONSTRUCTION_TYPE_ID'] == 17:
                reuseTickets.append(ticketSrDump)                
                ticketSrDump['name'] = 'Reuse OnSite';

            if ticketSrDump['CONSTRUCTION_TYPE_ID'] == 19:
                salvageTickets.append(ticketSrDump)                
                ticketSrDump['name'] = 'Salvage for reuse on other project';

            total_weight += float(ticketSrDump['weight'])
            total_reused += float(ticketSrDump['weight'])

    if len(donatedTickets):
        reused_types_tickets.append({'name': 'Donated', 'CONSTRUCTION_TYPE_ID': 18, 'tickets': donatedTickets})
    if len(reuseTickets):
        reused_types_tickets.append({'name': 'Reuse OnSite', 'CONSTRUCTION_TYPE_ID': 17, 'tickets': reuseTickets})    
    if len(salvageTickets):
        reused_types_tickets.append({'name': 'Salvage for reuse on other project', 'CONSTRUCTION_TYPE_ID': 19, 'tickets': salvageTickets})

    result['data']['attributes']['reused_types'] = reused_types_tickets
    result['data']['attributes']['materials_hauled'] = len(m_ids)
    result['data']['attributes']['tickets_count'] = tickets_count
    result['data']['attributes']['total_tons'] = total_weight
    result['data']['attributes']['recycled'] = total_recycled
    result['data']['attributes']['reused'] = total_reused
    result['data']['attributes']['rate'] = Calc.rate(total_weight, total_recycled)

    #append facilities with related tickets to result    
    result['data']['attributes']['facilities'] = []
    fids = []
    for ticket in query.tickets:
        ticketFacility = ticket.facility           
        if ticketFacility:
            facilities = FacilitiesSchema().dump(ticket.facility).data            
            facility = facilities['data']['attributes']                                    
            #prevent add duplictes            
            if not facility['FACILITY_ID'] in fids and facility['FACILITY_ID'] in tf:
                city = ticketFacility.city
                county = city.county
                fids.append(facility['FACILITY_ID'])
                facility['tickets'] = tf[facility['FACILITY_ID']]                
                facility['city'] = city.name
                facility['state'] = county.state
                result['data']['attributes']['facilities'].append(facility)
    
    print('========START CITY=======')
    city = query.city    
    result['data']['attributes']['city'] = city.name
    print(city.name)
    if len(city.efields):
        try:
            print('========START TERMS=======')    
            res = loads(dumps(city.efields), array_hook=OrderedDict)
            print('===1===')
            res = loads(res, object_hook=phpobject)
            print('===2===')    
            vendor_terms_key = 'vendor_terms1'.encode("utf-8")
            print('===3===')
            if vendor_terms_key in res:
                print('===4===')
                result['data']['attributes']['vendor_terms'] = str(res[vendor_terms_key],'utf-8')
            else:
                print('===5===')
                result['data']['attributes']['vendor_terms'] = 'The City did not provide Terms and Conditions.'            
        except RuntimeError:
            print('===6===')
            result['data']['attributes']['vendor_terms'] = 'The City did not provide Terms and Conditions.'                                          
    else:
        print('===7===')
        result['data']['attributes']['vendor_terms'] = 'The City did not provide Terms and Conditions.'                                                          

    return result['data']['attributes']        

class ProjectsList(Resource):    
        
    @token_auth.login_required
    def get(self):                        
        HAULER_ID = Security.getHaulerId()        
        query = Projects.query.filter(ProjectsHaulers.HAULER_ID==HAULER_ID, ProjectsHaulers.PROJECT_ID==Projects.PROJECT_ID, Projects.status=='approved').all()        
        haulersIds = []
        for project in query:                        
            haulersIds.append(project.PROJECT_ID)            

        debris = Projects.query.filter(ProjectsDebrisbox.HAULER_ID==HAULER_ID, ProjectsDebrisbox.PROJECT_ID==Projects.PROJECT_ID, Projects.status=='approved').all()            
        for project in debris:
            if not project.PROJECT_ID in haulersIds:                                        
                query.append(project)

        results = []
        for project in query:                                    
            results.append(buildResult(project))                             
        
        db.session.commit()
        return results                    
        #return(json.dumps([{"id": 9,"name": "XXXUPDCompleted project name","address": "project address","number": "01","company": "Vendor Company","materials_hauled": "1","total_tons": "0","recycled": "0","rate": "50","tickets_count": "5","facilities": [{"id": 9,"name": "Facility 1","tickets": [{"id": 1,"ticket": "ticket number","material": "Material Name","submitted_by": "Submitted By","weight": "100","recycled": "50","rate": "90","date": "7/26/2016"}, {"id": 2,"ticket": "ticket number","material": "Material Name","submitted_by": "Submitted By","weight": "100","recycled": "50","rate": "90","date": "7/26/2016"}]}]}]))

class CompletedList(Resource):    
        
    @token_auth.login_required
    def get(self):                                
        HAULER_ID = Security.getHaulerId()        
        query = Projects.query.filter(ProjectsHaulers.HAULER_ID==HAULER_ID, ProjectsHaulers.PROJECT_ID==Projects.PROJECT_ID, Projects.status=='completed').all()        
        
        haulersIds = []
        for project in query:
            haulersIds.append(project.PROJECT_ID)            

        debris = Projects.query.filter(ProjectsDebrisbox.HAULER_ID==HAULER_ID, ProjectsDebrisbox.PROJECT_ID==Projects.PROJECT_ID, Projects.status=='completed').all()            
        for project in debris:
            if not project.PROJECT_ID in haulersIds:            
                query.append(project)

        results = []
        for project in query:                                    
            results.append(buildResult(project))             
        
        db.session.commit()
        return results                    
        #return(json.dumps([{"id": 9,"name": "XXXUPDCompleted project name","address": "project address","number": "01","company": "Vendor Company","materials_hauled": "1","total_tons": "0","recycled": "0","rate": "50","tickets_count": "5","facilities": [{"id": 9,"name": "Facility 1","tickets": [{"id": 1,"ticket": "ticket number","material": "Material Name","submitted_by": "Submitted By","weight": "100","recycled": "50","rate": "90","date": "7/26/2016"}, {"id": 2,"ticket": "ticket number","material": "Material Name","submitted_by": "Submitted By","weight": "100","recycled": "50","rate": "90","date": "7/26/2016"}]}]}]))

class CompletedCount(Resource):    
        
    @token_auth.login_required
    def get(self):                                
        HAULER_ID = Security.getHaulerId()        
        query = Projects.query.filter(ProjectsHaulers.HAULER_ID==HAULER_ID, ProjectsHaulers.PROJECT_ID==Projects.PROJECT_ID, Projects.status=='completed').all()        
        
        haulersIds = []
        for project in query:
            haulersIds.append(project.PROJECT_ID)            

        debris = Projects.query.filter(ProjectsDebrisbox.HAULER_ID==HAULER_ID, ProjectsDebrisbox.PROJECT_ID==Projects.PROJECT_ID, Projects.status=='completed').all()            
        for project in debris:
            if not project.PROJECT_ID in haulersIds:            
                haulersIds.append(project.PROJECT_ID)

        results = len(haulersIds)        
        db.session.commit()

        return results                    
        #return(json.dumps([{"id": 9,"name": "XXXUPDCompleted project name","address": "project address","number": "01","company": "Vendor Company","materials_hauled": "1","total_tons": "0","recycled": "0","rate": "50","tickets_count": "5","facilities": [{"id": 9,"name": "Facility 1","tickets": [{"id": 1,"ticket": "ticket number","material": "Material Name","submitted_by": "Submitted By","weight": "100","recycled": "50","rate": "90","date": "7/26/2016"}, {"id": 2,"ticket": "ticket number","material": "Material Name","submitted_by": "Submitted By","weight": "100","recycled": "50","rate": "90","date": "7/26/2016"}]}]}]))

class ProjectsUpdate(Resource):        
    
    @token_auth.login_required
    def get(self, id):
        db.session.commit()
        query = Projects.query.get_or_404(id)                                
        return buildResult(query)
    
    @token_auth.login_required
    def patch(self, id):                
        project = Projects.query.get_or_404(id)        
        raw_dict = {"data": {"attributes": request.form, "type": "projects"}}
        
        try:
            HAULER_ID = Security.getHaulerId()            
            schema.validate(raw_dict)
            params_dict = raw_dict['data']['attributes']            
            
            #for key, value in params_dict.items():                
                #setattr(project, key, value)

            if 'vendor_terms_agree' in params_dict:                
                setattr(project, 'vendor_terms_agree', 'true')
                project.update()
                query = db.engine.execute("INSERT INTO projects_notes (DID, PROJECT_ID, UID, note, thedate) VALUES (75, {0}, {1}, 'Vendor has agreed to project terms and has accepted', NOW())".format(id, project.UID))                                                  

            if 'status' in params_dict:                
                setattr(project, 'status', 'submitted_for_final')
                setattr(project, 'final_HAULER_ID', HAULER_ID)
                setattr(project, 'final_thedate', datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
                project.update()                
          
            
            db.session.commit()            
            return (id)
            
        except ValidationError as err:
                resp = jsonify({"error": err.messages})
                resp.status_code = 401
                return resp               
                
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 401
                return resp    

class ProjectsTermsAgree(Resource):                
    
    @token_auth.login_required
    def patch(self, id):                        
        project = Projects.query.get_or_404(id)        
        raw_dict = {"data": {"attributes": request.form, "type": "projects"}}
        
        try:                                        
            setattr(project, 'vendor_terms_agree', 'true')          
            project.update()
            
            query = db.engine.execute("INSERT INTO projects_notes (DID, PROJECT_ID, UID, note, thedate) VALUES (75, {0}, {1}, 'Vendor has agreed to project terms and has accepted', NOW())".format(id, project.UID))                                  
            
            db.session.commit()            
            return (id) 
            
        except ValidationError as err:
                resp = jsonify({"error": err.messages})
                resp.status_code = 401
                return resp               
                
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 401
                return resp

                            

api.add_resource(ProjectsList, '.json')
api.add_resource(CompletedList, '/completed.json')
api.add_resource(CompletedCount, '/completed_count.json')
api.add_resource(ProjectsUpdate, '/<int:id>.json')
#api.add_resource(ProjectsTermsAgree, '/terms_agree/<int:id>.json')