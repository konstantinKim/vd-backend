from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from app.helper.helper import Calc

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
    street = db.Column(db.String(250))
    zipcode = db.Column(db.String(250))       
    facility_materials = db.relationship(FacilitiesMaterials, backref="facility", lazy='joined')
    
                 
class FacilitiesSchema(Schema):    
    not_blank = validate.Length(min=1, error='Field cannot be blank')    
    id = fields.Integer()    
    FACILITY_ID = fields.Integer(primary_key=True)    
    name = fields.String(validate=not_blank)
    street = fields.String()
    zipcode = fields.String()
     
    
     #self links
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/facilities/"
        else:            
            self_link = "/facilities/{}".format(data['attributes']['FACILITY_ID'])
        return {'self': self_link}
   
    
    class Meta:
        type_ = 'facilities'
        

class RecyclersSearch():
    
    def __init__(self, **kwargs):
        self.LAT = 0
        self.LON = 0
        self.distance = 0
        self.name = ""
        self.city = ""
        self.county = ""
        self.state = ""
        self.street = ""
        self.phone = ""
        self.url = ""
        self.zipcode = ""


    def find(MATERIAL_ID, zipcode, radius):
        query = db.engine.execute("SELECT * FROM zipcodes WHERE zipcode >= '"+ zipcode +"' ORDER BY zipcode ASC LIMIT 1")
        zipcode = query.fetchone()        
                        
        select_clause = ", zipcodes.LAT, zipcodes.LON , SQRT( (69.1 * (zipcodes.LAT - "+str(zipcode['LAT'])+")) * (69.1 * (zipcodes.LAT - "+str(zipcode['LAT'])+")) + (53.0 * (zipcodes.LON - "+str(zipcode['LON'])+")) * (53.0 * (zipcodes.LON - "+str(zipcode['LON'])+")) ) AS distance , facilities_materials.conversion_rate, facilities_materials.conversion_leed "
        
        join_clause_zipcodes = ", zipcodes"
        join_clause = " INNER JOIN facilities_materials ON facilities_materials.FACILITY_ID=facilities.FACILITY_ID "
        where_clause_zipcodes = " AND zipcodes.zipcode=facilities.zipcode  AND facilities_materials.MATERIAL_ID=" + str(MATERIAL_ID) + "  AND SQRT( (69.1 * (zipcodes.LAT - "+str(zipcode['LAT'])+")) * (69.1 * (zipcodes.LAT - "+str(zipcode['LAT'])+")) + (53.0 * (zipcodes.LON - "+str(zipcode['LON'])+")) * (53.0 * (zipcodes.LON - "+str(zipcode['LON'])+")) )  <= " + str(radius) 
        
        query = db.engine.execute("SELECT DISTINCT(facilities.FACILITY_ID), facilities.*, counties.name AS county, counties.state, cities.name AS city, \
		    facilities.FACILITY_ID AS CONTEXT_ID "+ select_clause + " FROM cities, facilities \
		    INNER JOIN counties ON facilities.COUNTY_ID=counties.COUNTY_ID " + join_clause + " " + join_clause_zipcodes + " \
            WHERE facilities.CITY_ID=cities.CITY_ID AND facilities.enabled='true' " + where_clause_zipcodes + " ORDER BY distance ASC  "  )

        data = query.fetchall()
        result = []
        for f in data:
            rs = RecyclersSearch()
            rs.LAT = str(f.LAT)
            rs.LON = str(f.LON)
            rs.name = f.name
            rs.city = f.city
            rs.county = f.county
            rs.state = f.state
            rs.distance = Calc.myRound(f.distance) 
            rs.street = f.street
            rs.phone = f.phone
            rs.url = f.url
            rs.zipcode = f.zipcode
            result.append(rs.__dict__)        
        
        return(result)


