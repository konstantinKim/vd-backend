from flask import Flask, Response
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from flask.ext.sqlalchemy import SQLAlchemy

class MyResponse(Response):
     default_mimetype = 'application/json'          

         
# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_filename)        
    app.response_class = MyResponse    
    
    # from app.users.models import db
    # db.init_app(app)

    db = SQLAlchemy(app)            
    
    # Blueprints   
    from app.auth.views import auth
    app.register_blueprint(auth, url_prefix='/api/v1/auth')    

    from app.projects.views import projects
    app.register_blueprint(projects, url_prefix='/api/v1/projects')

    from app.haulers.views import haulers
    app.register_blueprint(haulers, url_prefix='/api/v1/haulers')

    from app.ticketsRd.views import tickets_rd_bp
    app.register_blueprint(tickets_rd_bp, url_prefix='/api/v1/tickets_rd')

    from app.ticketsSr.views import tickets_sr_bp
    app.register_blueprint(tickets_sr_bp, url_prefix='/api/v1/tickets_sr')

    from app.materials.views import materials
    app.register_blueprint(materials, url_prefix='/api/v1/materials')

    from app.facilities.views import facilities
    app.register_blueprint(facilities, url_prefix='/api/v1/facilities')

    from app.statistics.views import statistics
    app.register_blueprint(statistics, url_prefix='/api/v1/statistics')    
            
    return app


