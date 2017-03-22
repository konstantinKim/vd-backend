import requests
from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
import datetime
from config import APP_ROOT, DEBUG
import hashlib
import os
import subprocess
from config import GH_URL

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

class Facilities(db.Model):    
    __tablename__ = 'facilities'     
    FACILITY_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)

class Materials(db.Model):    
    __tablename__ = 'materials'     
    MATERIAL_ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)        

class TicketsSr(db.Model, CRUD):
    __tablename__ = 'tickets_sr'     
    TICKET_SR_ID = db.Column(db.Integer, primary_key=True)
    DID = db.Column(db.Integer)
    PROJECT_ID = db.Column(db.Integer, nullable=False)
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
    material = db.relationship('Materials', backref="material", lazy='joined') 
    facility = db.relationship('Facilities', backref="facility", lazy='joined') 

    def __init__(self, **kwargs):                
        self.DID = 75
        self.PROJECT_ID = kwargs.get('PROJECT_ID')
        self.MATERIAL_ID = kwargs.get('MATERIAL_ID', 7)
        self.CONSTRUCTION_TYPE_ID = kwargs.get('CONSTRUCTION_TYPE_ID')
        self.FACILITY_ID = kwargs.get('FACILITY_ID', 0)
        self.ticket = kwargs.get('ticket', '')
        self.weight = kwargs.get('weight')
        self.cubic_yards = 0
        self.description = kwargs.get('description')
        self.inventory = kwargs.get('inventory', '')
        self.thedate = datetime.datetime.today().strftime('%Y-%m-%d')
        self.thedate_ticket = kwargs.get('thedate_ticket', datetime.datetime.today().strftime('%Y-%m-%d'))
        self.submitted_by = kwargs.get('submitted_by')
        self.percentage = kwargs.get('percentage')        
        self.HAULER_ID = kwargs.get('HAULER_ID')

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

    def save_file(self, file, filename):        
        if file:
            folder = self.get_folder()                                    
            file.save(os.path.join(folder, filename))            
            #Convert to jpg
            if DEBUG:
                cmd = "convert -quality 95 -type truecolor -colorspace RGB -append " + folder + filename + " " + folder + filename + ".jpg"
                #cmd = "convert1 -quality 95 -type truecolor -colorspace RGB -append " + folder + filename + " " + folder + filename + ".jpg"            
            else:
                cmd = "convert -quality 95 -type truecolor -colorspace RGB -append " + folder + filename + " " + folder + filename + ".jpg"                
            PIPE = subprocess.PIPE
            p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
                    stderr=subprocess.STDOUT)
            while True:
                s = p.stdout.readline()
                if not s: break
                print (s,)    

    def validateDate(self):           
        if self.thedate_ticket:             
            ticket_date = datetime.datetime.strptime(self.thedate_ticket, "%Y-%m-%d")
            current_date = datetime.datetime.now()
            d = current_date - ticket_date        
            if d.total_seconds() < 0:       
                raise ValueError("Cannot use future Ticket Date.")  
    
    def sendLargeTicketNotification(self):        
        if self.weight > 100:            
            requests.get('{0}/?func=messages/send_large_ticket_notification&ticket_id={1}&ticket_type=sr'.format(GH_URL, self.TICKET_SR_ID))                            

    def setRecyclingRates(self, params):
        try:
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
            
            query = db.engine.execute("SELECT density FROM materials "+
                "WHERE MATERIAL_ID="+str(MATERIAL_ID))                
            
            material = query.fetchone()
            density = 0
            if material:
                density = material[0]
            else:
                raise ValueError("Invalid Material")

            weight = Decimal(self.weight)        
            cubic_yards = weight / density

            if params['units'] == 'yards':
                cubic_yards = weight
                weight = weight * density
            if params['units'] == 'pounds':
                weight = weight / 2000                
                cubic_yards = weight / density
            if params['units'] == 'metric_tons':
                weight = weight * 1.10231
                cubic_yards = weight * 1.30795062
            if params['units'] == 'cubic_meter':
                cubic_yards = weight * 1.30795062
                weight = cubic_yards * density
            if params['units'] == 'kilograms':
                pounds = weight * 2.20462
                weight = pounds / 2000
                cubic_yards = weight / density        

            self.weight = weight                    
            self.cubic_yards = cubic_yards
        except Exception as e:
            print(e)
            raise ValueError("Oops! That was no valid data. Check data and try again...")


      
           
class TicketsSrSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer()    
    TICKET_SR_ID = fields.Integer(primary_key=True)    
    FACILITY_ID = fields.Integer()    
    PROJECT_ID = fields.Integer()    
    CONSTRUCTION_TYPE_ID = fields.Integer()  
    HAULER_ID = fields.Integer()    
    CONSTRUCTION_TYPE_ID = fields.Integer()    
    ticket = fields.String()            
    submitted_by = fields.String()            
    weight = fields.String()            
    percentage = fields.String()
    description = fields.String()
    inventory = fields.String()
    thedate_ticket = fields.DateTime()
     
    
     #self links
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/tickets_sr/"
        else:            
            self_link = "/tickets_sr/{}".format(data['attributes']['TICKET_SR_ID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'tickets_sr'
        