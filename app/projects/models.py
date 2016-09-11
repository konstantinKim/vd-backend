from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

import hashlib
import os
from config import APP_ROOT

db = SQLAlchemy()

class CRUD():   

    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()   

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()

class Materials(db.Model, CRUD):    
    __tablename__ = 'materials'     
    MATERIAL_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)       

class TicketsRd(db.Model):
    __tablename__ = 'tickets_rd'     
    TICKET_RD_ID = db.Column(db.Integer, primary_key=True)
    PROJECT_ID = db.Column(db.Integer, db.ForeignKey('projects.PROJECT_ID'), nullable=False)
    MATERIAL_ID = db.Column(db.Integer, db.ForeignKey('materials.MATERIAL_ID'))
    FACILITY_ID = db.Column(db.Integer, db.ForeignKey('facilities.FACILITY_ID'))
    HAULER_ID = db.Column(db.Integer)
    ticket = db.Column(db.String(250))               
    facility = db.relationship('Facilities', backref="tickets", lazy='joined')      
    material = db.relationship('Materials', backref="material", lazy='joined') 
    submitted_by = db.Column(db.String()) 
    weight = db.Column(db.Numeric(precision=14, scale=4))  
    recycled = db.Column(db.Numeric(precision=14, scale=4))   
    rate_used = db.Column(db.String()) 
    thedate = db.Column(db.DateTime())                         

    def get_folder(self, half=None):        
        type = 'tickets'
        ID = str(self.TICKET_RD_ID)+'RD'
        m = hashlib.md5()
        m.update(ID.encode('utf-8'))
        parts = m.hexdigest()
        half_path = "/data/extensions_data/"+type+"/"+parts[0]+"/"+parts[1]+"/"+parts[2]+"/"+parts[3]+"/"+parts[4]+"/"+ID+"/"
        path = APP_ROOT + half_path
        os.makedirs(path, mode=0o0775, exist_ok=True)
        if half:
            return (half_path)
        return (path)

class Facilities(db.Model):    
    __tablename__ = 'facilities'     
    FACILITY_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)           

class ProjectsHaulers(db.Model):    
    __tablename__ = 'projects_haulers'     
    PROJECT_HAULER_ID = db.Column(db.Integer, primary_key=True)    
    HAULER_ID = db.Column(db.Integer)    
    PROJECT_ID = db.Column(db.Integer, db.ForeignKey('projects.PROJECT_ID'), nullable=False)

class ProjectsDebrisbox(db.Model):    
    __tablename__ = 'projects_debrisbox'     
    PROJECT_DEBRISBOX_ID = db.Column(db.Integer, primary_key=True)    
    HAULER_ID = db.Column(db.Integer)    
    PROJECT_ID = db.Column(db.Integer, db.ForeignKey('projects.PROJECT_ID'), nullable=False)


class Projects(db.Model, CRUD):    
    PROJECT_ID = db.Column(db.Integer, primary_key=True)
    CITY_ID = db.Column(db.Integer)    
    name = db.Column(db.String(250), unique=True, nullable=False)   
    street = db.Column(db.String(250), unique=True, nullable=False)  
    turner_number = db.Column(db.String(250), nullable=False)                
    status = db.Column(db.String(250))                
    tickets = db.relationship(TicketsRd, backref="project", lazy='joined' )
    projects_haulers = db.relationship(ProjectsHaulers, backref="hauler_project", lazy='joined')
    projects_debrisbox = db.relationship(ProjectsDebrisbox, backref="debrisbox_project", lazy='joined')

        
           
class ProjectsSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer()    
    PROJECT_ID = fields.Integer(primary_key=True)    
    CITY_ID = fields.Integer()        
    name = fields.String(validate=not_blank)        
    street = fields.String(validate=not_blank)        
    turner_number = fields.String(validate=not_blank)           
     
    
     #self links
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/projects/"
        else:            
            self_link = "/projects/{}".format(data['attributes']['PROJECT_ID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'projects'
        