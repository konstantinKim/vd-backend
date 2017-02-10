from marshmallow_jsonapi import Schema, fields
from marshmallow import validate, ValidationError
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import datetime
from config import APP_ROOT, DEBUG
import hashlib
import os
import subprocess

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

class HaulersImages(db.Model, CRUD):    
    __tablename__ = 'haulers_images'     
    id = db.Column(db.Integer, primary_key=True)
    HAULER_ID = db.Column(db.Integer)    
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(6), nullable=False)

    def __init__(self, **kwargs):                        
        self.HAULER_ID = kwargs.get('HAULER_ID')
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')
                

    def get_folder(self, half=None):                 
        half_path = "/data/extensions_data/haulers_images/"+str(self.HAULER_ID)+"/"
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
            os.remove(folder + filename)    

class HaulersImagesSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')
    id = fields.Integer()            
    HAULER_ID = fields.Integer()    
    name = fields.String()
    type = fields.String()
    
    #self links
    def get_top_level_links(self, data, many):                
        if many:
            self_link = "/haulers_images/"
        else:            
            self_link = "/haulers_images/{}".format(data['attributes']['id'])
        return {'self': self_link}
   
    class Meta:
        type_ = 'haulers_images'

