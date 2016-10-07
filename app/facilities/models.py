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


class FacilitiesMaterials(db.Model):    
    __tablename__ = 'facilities_materials'     
    MATERIAL_ID = db.Column(db.Integer, primary_key=True)
    FACILITY_ID = db.Column(db.Integer, db.ForeignKey('facilities.FACILITY_ID'))    

class Facilities(db.Model, CRUD):    
    __tablename__ = 'facilities'     
    FACILITY_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)       
    facility_materials = db.relationship(FacilitiesMaterials, backref="facility", lazy='joined')
    
                 
class FacilitiesSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer()    
    FACILITY_ID = fields.Integer(primary_key=True)    
    name = fields.String(validate=not_blank)            
     
    
     #self links
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/facilities/"
        else:            
            self_link = "/facilities/{}".format(data['attributes']['FACILITY_ID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'facilities'
        