from marshmallow_jsonapi import Schema, fields
from marshmallow import validate, ValidationError
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import datetime
from config import APP_ROOT
import hashlib
import os
import subprocess

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

class Facilities(db.Model):    
    __tablename__ = 'facilities'     
    FACILITY_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)        

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
    FACILITY_ID = db.Column(db.Integer, db.ForeignKey('facilities.FACILITY_ID'))
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
    facility = db.relationship('Facilities', backref="facility", lazy='joined') 

    def __init__(self, **kwargs):                
        self.DID = 75
        self.PROJECT_ID = kwargs.get('PROJECT_ID')
        self.MATERIAL_ID = kwargs.get('MATERIAL_ID')
        self.FACILITY_ID = kwargs.get('FACILITY_ID')
        self.ticket = kwargs.get('ticket')
        self.thedate = kwargs.get('thedate', datetime.datetime.today().strftime('%Y-%m-%d'))
        self.weight = kwargs.get('weight')
        self.recycled = kwargs.get('recycled')
        self.percentage = kwargs.get('percentage')
        self.rate_used = kwargs.get('rate_used')
        self.submitted_by = kwargs.get('submitted_by')
        self.ticket_status = kwargs.get('ticket_status', 'approved')
        self.date_created = datetime.datetime.today().strftime('%Y-%m-%d')
        self.type = kwargs.get('type', 'rd')
        self.units = kwargs.get('units')
        self.HAULER_ID = kwargs.get('HAULER_ID')


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

    def save_file(self, file):        
        if file:
            folder = self.get_folder()                                    
            file.save(os.path.join(folder, 'ticket'))            
            #Convert to jpg
            cmd = "convert1 -quality 95 -type truecolor -colorspace RGB -append " + folder + "ticket " + folder + "ticket.jpg"            
            PIPE = subprocess.PIPE
            p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
                    stderr=subprocess.STDOUT)
            while True:
                s = p.stdout.readline()
                if not s: break
                print (s,)

    def validateTicket(self):
        FACILITY_ID = self.FACILITY_ID
        percentage = self.percentage
        query = db.engine.execute("SELECT SUM(percentage) FROM tickets_rd " +
            "WHERE FACILITY_ID=" + str(FACILITY_ID) + " AND ticket='" + self.ticket + "'")        
        total = query.fetchone()        
        if total and total[0]:            
            if total[0] + int(percentage) > 100:            
                raise ValueError("Ticket #"+self.ticket+" has already been used.")

    def setRecyclingRates(self):
        if int(self.FACILITY_ID) <= 0:
            raise valueError('Error validating ticket total because the facility ID is empty')
        
        PROJECT_ID = self.PROJECT_ID
        HAULER_ID = self.HAULER_ID
        FACILITY_ID = self.FACILITY_ID
        MATERIAL_ID = self.MATERIAL_ID
        percentage = self.percentage

        query = db.engine.execute("select projects.PROJECT_ID FROM projects "+
            "LEFT JOIN projects_haulers ON projects_haulers.PROJECT_ID=projects.PROJECT_ID "+
            "LEFT JOIN projects_debrisbox ON projects_debrisbox.PROJECT_ID=projects.PROJECT_ID "+
            "WHERE projects.status='approved' AND projects.PROJECT_ID=" + str(PROJECT_ID) + " AND (projects_haulers.HAULER_ID=" + str(HAULER_ID) + " OR projects_debrisbox.HAULER_ID="+str(HAULER_ID)+")")

        project = query.fetchone()
        if not project:
            raise ValueError("Sorry, you cannot add tickets to this project")

        query = db.engine.execute("SELECT conversion_rate FROM facilities_materials "+
            "WHERE FACILITY_ID="+str(FACILITY_ID)+" AND MATERIAL_ID=" + str(MATERIAL_ID))            
        rate = query.fetchone()
        if rate:
            rate = rate[0]
        else:
            raise ValueError("Invalid Facility or Material")            

        query = db.engine.execute("SELECT density FROM materials "+
            "WHERE MATERIAL_ID="+str(MATERIAL_ID))                
        
        material = query.fetchone()
        density = 0
        if material:
            density = material[0]
        else:
            raise ValueError("Invalid Material")

        weight = self.weight
        if self.units == 'yards':
            weight = weight * density;    
        if self.units == 'pounds':
            weight = weight / 2000
        if self.units == 'metric_tons':
            weight = weight * 1.10231
        if self.units == 'cubic_meter':
            cy = weight * 1.30795062
            weight = cy * density
        if self.units == 'kilograms':
            pounds = weight * 2.20462
            weight = pounds / 2000

        recycled = (((float(rate) / 100) * float(weight)) * (float(percentage) / 100))    
        if recycled < 0:
            recycled = 0            

        self.weight = weight
        self.recycled = recycled                                            

           
class TicketsRdSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')
    id = fields.Integer()    
    TICKET_RD_ID = fields.Integer(primary_key=True)    
    FACILITY_ID = fields.Integer()    
    MATERIAL_ID = fields.Integer()    
    PROJECT_ID = fields.Integer()    
    HAULER_ID = fields.Integer()    
    ticket = fields.String()
    submitted_by = fields.String()            
    units = fields.String()          
    weight = fields.String()            
    recycled = fields.String()            
    percentage = fields.String()
    rate_used = fields.String()    
    thedate = fields.DateTime()
    
     #self links
    def get_top_level_links(self, data, many):                
        if many:
            self_link = "/tickets_rd/"
        else:            
            self_link = "/tickets_rd/{}".format(data['attributes']['TICKET_RD_ID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'tickets_rd'

        