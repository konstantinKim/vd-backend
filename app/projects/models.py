from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

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



class Projects(db.Model, CRUD):    
    PROJECT_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)   
    street = db.Column(db.String(250), unique=True, nullable=False)  
    turner_number = db.Column(db.String(250), nullable=False)                
    tickets = db.relationship('TicketsRd', backref="project")

class TicketsRd(db.Model, CRUD):
    __tablename__ = 'tickets_rd'     
    TICKET_RD_ID = db.Column(db.Integer, primary_key=True)
    PROJECT_ID = db.Column(db.Integer, db.ForeignKey('projects.PROJECT_ID'), nullable=False)
    MATERIAL_ID = db.Column(db.Integer)
    FACILITY_ID = db.Column(db.Integer)
    ticket = db.Column(db.String(250))               
    
      
           
class ProjectsSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer()    
    PROJECT_ID = fields.Integer(primary_key=True)    
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
        