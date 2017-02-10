from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

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

class Representative(db.Model, CRUD):    
    __tablename__ = 'haulers_representative'     
    id = db.Column(db.Integer, primary_key=True)
    HAULER_ID = db.Column(db.Integer, db.ForeignKey('haulers.HAULER_ID'), nullable=False)

class Haulers(db.Model, CRUD):
    __tablename__ = 'haulers'     
    HAULER_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))   
    contact = db.Column(db.String(250),)        
    url = db.Column(db.String(250))        
    street = db.Column(db.String(250))        
    city = db.Column(db.String(250))        
    state = db.Column(db.String(250))        
    zipcode = db.Column(db.String(250))            
    phone = db.Column(db.String(250))        
    email = db.Column(db.String(250))        
    enabled = db.Column(db.Enum('true','false'), default='false')        
    hauling = db.Column(db.Enum('true','false'), default='false')        
    debrisbox = db.Column(db.Enum('true','false'), default='false')        
    cell = db.Column(db.String(250))        
    selfhaul = db.Column(db.Enum('true','false'), default='false')                
    password = db.Column(db.String(250))
    permits = db.Column(db.String())
    hours = db.Column(db.String())                
    associations = db.Column(db.String())                
      
           
class HaulersSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer(dump_only=True)    
    HAULER_ID = fields.Integer(primary_key=True)    
    name = fields.String(validate=not_blank)        
    contact = fields.String()        
    street = fields.String()        
    zipcode = fields.String()        
    debrisbox = fields.String()        
    hauling = fields.String()        
    selfhaul = fields.String()            
    phone = fields.String()        
    email = fields.Email(validate=not_blank)    
    url = fields.String()
    permits = fields.String()
    hours = fields.String()
    associations = fields.String()        
        
     #self links
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/haulers/"
        else:                        
            self_link = "/haulers/{}".format(data['attributes']['HAULER_ID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'haulers'
        