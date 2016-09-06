from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import datetime

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

class Materials(db.Model):    
    __tablename__ = 'materials'     
    MATERIAL_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)        

class TicketsRd(db.Model, CRUD):
    __tablename__ = 'tickets_rd'     
    TICKET_RD_ID = db.Column(db.Integer, primary_key=True)
    DID = db.Column(db.Integer, nullable=False)
    PROJECT_ID = db.Column(db.Integer, nullable=False)    
    MATERIAL_ID = db.Column(db.Integer, db.ForeignKey('materials.MATERIAL_ID'))
    FACILITY_ID = db.Column(db.Integer)
    ticket = db.Column(db.String(250))                   
    thedate = db.Column(db.DateTime())
    weight = db.Column(db.Float())
    recycled = db.Column(db.Float())
    percentage = db.Column(db.Integer)
    rate_used = db.Column(db.Integer)
    submitted_by = db.Column(db.String(250))
    recipient_id = db.Column(db.Integer)
    ticket_efields = db.Column(db.Text())
    ticket_status = db.Column(db.String(128))
    data_before_reject = db.Column(db.Text())
    date_created = db.Column(db.DateTime())
    type = db.Column(db.Enum('rd', 'stream'))
    ticket_permit = db.Column(db.String(250))
    CONTRACTOR_SC_ID = db.Column(db.Integer)
    units = db.Column(db.Enum('yards','pounds','metric_tons','cubic_meter','kilograms','tons'))    
    HAULER_ID = db.Column(db.Integer, nullable=False )
    material = db.relationship('Materials', backref="material", lazy='joined') 

    def __init__(self, **kwargs):                
        self.DID = 75
        self.PROJECT_ID = kwargs.get('PROJECT_ID')
        self.MATERIAL_ID = kwargs.get('MATERIAL_ID',"0")
        self.FACILITY_ID = kwargs.get('FACILITY_ID',"0")
        self.ticket = kwargs.get('ticket')
        self.thedate = kwargs.get('thedate', datetime.datetime.today().strftime('%Y-%m-%d'))
        self.weight = kwargs.get('weight', 0)
        self.recycled = kwargs.get('recycled', 0)
        self.percentage = kwargs.get('percentage', 0)
        self.rate_used = kwargs.get('rate_used', 0)
        self.ticket_status = kwargs.get('ticket_status', '')
        self.type = kwargs.get('type', 'rd')
        self.units = kwargs.get('units', 'tons')
        HAULER_ID = HAULER_ID = db.Column(db.Integer, nullable=False )        

      
           
class TicketsRdSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer()    
    TICKET_RD_ID = fields.Integer(primary_key=True)    
    FACILITY_ID = fields.Integer()    
    PROJECT_ID = fields.Integer()    
    ticket = fields.String()
    submitted_by = fields.String()            
    weight = fields.String()            
    recycled = fields.String()            
    rate_used = fields.String()            
    date_created = fields.DateTime()
    
     #self links
    def get_top_level_links(self, data, many):                
        if many:
            self_link = "/tickets_rd/"
        else:            
            self_link = "/tickets_rd/{}".format(data['attributes']['TICKET_RD_ID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'tickets_rd'
        