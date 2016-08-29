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

class Haulers(db.Model, CRUD):
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
      
           
class HaulersSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer(dump_only=True)
    email = fields.Email(validate=not_blank)    
    name = fields.String(validate=not_blank)        
    HAULER_UID = fields.Integer(primary_key=True)    
 
    
     #self links
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/haulers/"
        else:            
            self_link = "/haulers/{}".format(data['attributes']['HAULER_UID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'haulers'
        