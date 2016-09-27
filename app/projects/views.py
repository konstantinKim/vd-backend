from flask import Blueprint, request, jsonify, make_response
from app.projects.models import Projects, ProjectsHaulers, ProjectsDebrisbox, ProjectsSchema, TicketsRd, db
from app.facilities.models import FacilitiesSchema
from app.ticketsRd.models import TicketsRdSchema
from app.materials.models import MaterialsSchema
from flask_restful import Api, Resource
from app.helper.helper import Calc
from app.auth.models import token_auth, Security
import json
import datetime

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
    #group tickets by facility
    tf = {}
    m_ids = []
    tickets_count = 0
    total_weight = 0
    total_recycled = 0
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

    result['data']['attributes']['materials_hauled'] = len(m_ids)
    result['data']['attributes']['tickets_count'] = tickets_count
    result['data']['attributes']['total_tons'] = total_weight
    result['data']['attributes']['recycled'] = total_recycled
    result['data']['attributes']['rate'] = Calc.rate(total_weight, total_recycled)

    #append facilities with related tickets to result    
    result['data']['attributes']['facilities'] = []
    fids = []
    for ticket in query.tickets:            
        if ticket.facility:
            facilities = FacilitiesSchema().dump(ticket.facility).data            
            facility = facilities['data']['attributes']            
            #prevent add duplictes            
            if not facility['FACILITY_ID'] in fids and facility['FACILITY_ID'] in tf:
                fids.append(facility['FACILITY_ID'])
                facility['tickets'] = tf[facility['FACILITY_ID']]
                result['data']['attributes']['facilities'].append(facility)


    return result['data']['attributes']        

class ProjectsList(Resource):    
        
    @token_auth.login_required
    def get(self):                
        HAULER_ID = Security.getHaulerId()        
        query = Projects.query.filter(ProjectsHaulers.HAULER_ID==HAULER_ID, ProjectsHaulers.PROJECT_ID==Projects.PROJECT_ID, Projects.status=='approved').all()
        print('///////////////////////////')
        haulersIds = []
        for project in query:
            print('///////////////////////////')
            print(project)
            haulersIds.append(project.PROJECT_ID)            

        debris = Projects.query.filter(ProjectsDebrisbox.HAULER_ID==HAULER_ID, ProjectsDebrisbox.PROJECT_ID==Projects.PROJECT_ID, Projects.status=='approved').all()            
        for project in debris:
            if not project.PROJECT_ID in haulersIds:            
                print('///////////////////////////')
                print(project)
                query.append(project)

        results = []
        for project in query:                                    
            results.append(buildResult(project))             
        
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
        
        return results                    
        #return(json.dumps([{"id": 9,"name": "XXXUPDCompleted project name","address": "project address","number": "01","company": "Vendor Company","materials_hauled": "1","total_tons": "0","recycled": "0","rate": "50","tickets_count": "5","facilities": [{"id": 9,"name": "Facility 1","tickets": [{"id": 1,"ticket": "ticket number","material": "Material Name","submitted_by": "Submitted By","weight": "100","recycled": "50","rate": "90","date": "7/26/2016"}, {"id": 2,"ticket": "ticket number","material": "Material Name","submitted_by": "Submitted By","weight": "100","recycled": "50","rate": "90","date": "7/26/2016"}]}]}]))

class ProjectsUpdate(Resource):        
    
    @token_auth.login_required
    def get(self, id):
        query = Projects.query.get_or_404(id)                                
        return buildResult(query)
    
    def patch(self, id):
        project = Projects.query.get_or_404(id)
        raw_dict = request.get_json(force=True)
        
        try:
            schema.validate(raw_dict)
            user_dict = raw_dict['data']['attributes']
            for key, value in user_dict.items():
                
                setattr(project, key, value)
          
            project.update()            
            return self.get(id)
            
        except ValidationError as err:
                resp = jsonify({"error": err.messages})
                resp.status_code = 401
                return resp               
                
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 401
                return resp
             
    def delete(self, id):
        project = Projects.query.get_or_404(id)
        try:
            delete = user.delete(user)
            response = make_response()
            response.status_code = 204
            return response
            
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 401
                return resp        

api.add_resource(ProjectsList, '.json')
api.add_resource(CompletedList, '/completed.json')
api.add_resource(CompletedCount, '/completed_count.json')
api.add_resource(ProjectsUpdate, '/<int:id>.json')