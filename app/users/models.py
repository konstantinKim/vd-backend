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

class Users(db.Model, CRUD):
    UID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)       
    password = db.Column(db.String(250), nullable=False)        

    def __init__(self,  username,  company_name):        
        self.username = username
        self.company_name = company_name        
      
           
class UsersSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer()
    username = fields.Email(validate=not_blank)        
    UID = fields.Integer(primary_key=True)    
 
    
     #self links
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/users/"
        else:            
            self_link = "/users/{}".format(data['attributes']['UID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'users'
        