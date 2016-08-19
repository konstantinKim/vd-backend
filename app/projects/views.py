from flask import Blueprint, request, jsonify, make_response
from app.haulers.models import auth
from app.projects.models import Projects, ProjectsSchema, db
from flask_restful import Api, Resource


 
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

projects = Blueprint('projects', __name__)
# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
#https://github.com/marshmallow-code/marshmallow-jsonapi
schema = ProjectsSchema()
api = Api(projects)

# Users
class ProjectsList(Resource):    
        
    @auth.login_required
    def get(self):        
        query = Projects.query.all()                
        print(query)
        results = schema.dump(query, many=True).data                       
        return results                    

class ProjectsUpdate(Resource):        
    
    @auth.login_required
    def get(self, id):
        query = Projects.query.options(db.joinedload(Projects.tickets)).get_or_404(id)
        
        result = schema.dump(query).data
        #print(query.tickets)
        return result            
    
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
api.add_resource(ProjectsUpdate, '/<int:id>.json')