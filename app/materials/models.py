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



class Materials(db.Model, CRUD):  
    __tablename__ = 'materials'       
    MATERIAL_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)       
    cn_id = db.Column(db.Integer)       
    pt_id = db.Column(db.Integer)       
                     

class MaterialsSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer()    
    MATERIAL_ID = fields.Integer(primary_key=True)    
    name = fields.String(validate=not_blank)            
     
    
     #self links
    def get_top_level_links(self, data, many):
        self_link = ''
        if many:
            self_link = "/materials/"
        else:            
            if 'attributes' in data:
                self_link = "/materials/{}".format(data['attributes']['MATERIAL_ID'])            
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'materials'
        

class MaterialsSalvage(db.Model, CRUD):    
    __tablename__ = 'materials_salvage'     
    MATERIAL_SALVAGE_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)           


class MaterialsSalvageSchema(Schema):     
    not_blank = validate.Length(min=1, error='Field cannot be blank')       
    id = fields.Integer()    
    MATERIAL_SALVAGE_ID = fields.Integer(primary_key=True)    
    name = fields.String(validate=not_blank)            
     
    
     #self links
    def get_top_level_links(self, data, many):
        self_link = ''
        if many:
            self_link = "/materials/salvage/"
        else:            
            if 'attributes' in data:
                self_link = "/materials/salvage/{}".format(data['attributes']['MATERIAL_SALVAGE_ID'])            
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'materials_salvage'        


