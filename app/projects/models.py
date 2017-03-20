from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

import hashlib
import os
from config import APP_ROOT

db = SQLAlchemy(session_options={"autoflush": False})

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

class Counties(db.Model, CRUD):    
    __tablename__ = 'counties'     
    COUNTY_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    state = db.Column(db.String(250))               

class Cities(db.Model, CRUD):    
    __tablename__ = 'cities'     
    CITY_ID = db.Column(db.Integer, primary_key=True)
    COUNTY_ID = db.Column(db.Integer, db.ForeignKey('counties.COUNTY_ID'))
    name = db.Column(db.String(250), nullable=False)
    efields = db.Column(db.Text())
    county = db.relationship(Counties, backref="city", lazy='joined' )    

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
    units = db.Column(db.Enum('yards','pounds','metric_tons','cubic_meter','kilograms','tons'))    
    weight = db.Column(db.Numeric(precision=14, scale=4))  
    recycled = db.Column(db.Numeric(precision=14, scale=4))   
    percentage = db.Column(db.String())
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

class TicketsSr(db.Model):
    __tablename__ = 'tickets_sr'     
    TICKET_SR_ID = db.Column(db.Integer, primary_key=True)
    DID = db.Column(db.Integer)
    PROJECT_ID = db.Column(db.Integer, db.ForeignKey('projects.PROJECT_ID'), nullable=False)
    MATERIAL_ID = db.Column(db.Integer, db.ForeignKey('materials.MATERIAL_ID'))
    CONSTRUCTION_TYPE_ID = db.Column(db.Integer)
    FACILITY_ID = db.Column(db.Integer, db.ForeignKey('facilities.FACILITY_ID'))
    ticket = db.Column(db.String(250))
    weight = db.Column(db.Float())
    cubic_yards = db.Column(db.Float())
    description = db.Column(db.Text())
    inventory = db.Column(db.Text())
    thedate = db.Column(db.DateTime())
    thedate_ticket = db.Column(db.DateTime())
    submitted_by = db.Column(db.String(250))
    percentage = db.Column(db.Integer)        
    HAULER_ID = db.Column(db.Integer, nullable=False)            
    material = db.relationship('Materials', backref="sr_material", lazy='joined')
    facility = db.relationship('Facilities', backref="sr_facility", lazy='joined')     

    def get_folder(self, half=None):        
        type = 'tickets'
        ID = str(self.TICKET_SR_ID)+'SR'
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
    street = db.Column(db.String(250))
    zipcode = db.Column(db.String(250))
    CITY_ID = db.Column(db.Integer, db.ForeignKey('cities.CITY_ID'))           
    city = db.relationship(Cities, backref="facility", lazy='joined' )

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
    CITY_ID = db.Column(db.Integer, db.ForeignKey('cities.CITY_ID'))    
    UID = db.Column(db.Integer)
    final_HAULER_ID = db.Column(db.Integer)
    final_thedate = db.Column(db.DateTime())
    name = db.Column(db.String(250), unique=True, nullable=False)   
    street = db.Column(db.String(250), unique=True, nullable=False)  
    state = db.Column(db.String(10))
    zipcode = db.Column(db.String(12))    
    tracking = db.Column(db.String(64), nullable=False)                
    status = db.Column(db.String(250))                    
    tickets = db.relationship(TicketsRd, backref="project", lazy='joined' )
    tickets_sr = db.relationship(TicketsSr, backref="project", lazy='joined' )
    projects_haulers = db.relationship(ProjectsHaulers, backref="hauler_project", lazy='joined')
    projects_debrisbox = db.relationship(ProjectsDebrisbox, backref="debrisbox_project", lazy='joined')
    city = db.relationship(Cities, backref="project", lazy='joined' )
    hauling_option = db.Column(db.String(64))
    vendor_terms_agree = db.Column(db.String(10))
        
           
class ProjectsSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer()    
    PROJECT_ID = fields.Integer(primary_key=True)    
    CITY_ID = fields.Integer()        
    name = fields.String(validate=not_blank)        
    street = fields.String(validate=not_blank)
    state = fields.String()
    zipcode = fields.String()        
    tracking = fields.String(validate=not_blank)           
    hauling_option = fields.String()
    vendor_terms_agree = fields.String()
     
    
     #self links
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/projects/"
        else:            
            self_link = "/projects/{}".format(data['attributes']['PROJECT_ID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'projects'

def syncProject(id):
    query = db.engine.execute("UPDATE projects "+
        "SET tickets_rd=(SELECT COUNT(*) FROM tickets_rd trd WHERE trd.PROJECT_ID="+ str(id) + ") "+
        "WHERE PROJECT_ID=" + str(id))        
    query = db.engine.execute("UPDATE projects SET tickets_sr=(SELECT COUNT(*) FROM tickets_sr WHERE PROJECT_ID="+str(id)+") WHERE PROJECT_ID="+str(id))        
    query = db.engine.execute("UPDATE projects SET sr=(SELECT SUM(weight) FROM tickets_sr WHERE PROJECT_ID="+str(id)+") WHERE PROJECT_ID="+str(id))        
    query = db.engine.execute("UPDATE projects SET r=(SELECT SUM(recycled) FROM tickets_rd trd WHERE PROJECT_ID="+str(id)+") WHERE PROJECT_ID="+str(id))        
    query = db.engine.execute("UPDATE projects SET d=(SELECT SUM(weight * (percentage / 100)) - SUM(recycled) FROM tickets_rd trd WHERE PROJECT_ID="+str(id)+") WHERE PROJECT_ID="+str(id))        
    query = db.engine.execute("UPDATE projects SET rs=(sr + r) WHERE PROJECT_ID="+str(id))        
    query = db.engine.execute("UPDATE projects SET percentage=(rs / (rs + d)) * 100 WHERE PROJECT_ID="+str(id))        
    
    return True
        