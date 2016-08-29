from flask import Flask, Response
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin

class MyResponse(Response):
     default_mimetype = 'application/json'          

         
# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_filename)        
    app.response_class = MyResponse    
    
    from app.users.models import db
    db.init_app(app)    
    
    # Blueprints   
    from app.auth.views import auth
    app.register_blueprint(auth, url_prefix='/api/v1/auth')

    from app.users.views import users
    app.register_blueprint(users, url_prefix='/api/v1/users')

    from app.projects.views import projects
    app.register_blueprint(projects, url_prefix='/api/v1/projects')

    from app.haulers.views import haulers
    app.register_blueprint(haulers, url_prefix='/api/v1/haulers')
            
    return app


