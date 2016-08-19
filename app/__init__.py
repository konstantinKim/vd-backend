from flask import Flask, Response
from flask_restful import Resource, Api


app = Flask(__name__)

class MyResponse(Response):
     default_mimetype = 'application/xml'     

         
# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.response_class = MyResponse    
    
    from app.users.models import db
    db.init_app(app)    
    
    # Blueprints   
    from app.users.views import users
    app.register_blueprint(users, url_prefix='/api/v1/users')

    from app.projects.views import projects
    app.register_blueprint(projects, url_prefix='/api/v1/projects')

    from app.haulers.views import haulers
    app.register_blueprint(haulers, url_prefix='/api/v1/haulers')
            
    return app


