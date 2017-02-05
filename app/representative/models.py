from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy(session_options={"autoflush": True})

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
    HAULER_ID = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)                  
    password = db.Column(db.String(64))                  
    
                     

class RepresentativeSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer(primary_key=True)    
    HAULER_ID = fields.Integer()    
    email = fields.String(validate=not_blank)            
    
     #self links
    def get_top_level_links(self, data, many):
        self_link = ''
        if many:
            self_link = "/representative/"
        else:            
            if 'attributes' in data:
                self_link = "/representative/{}".format(data['attributes']['id'])            
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'representative'
        

