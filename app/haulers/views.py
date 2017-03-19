from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource

from app.auth.models import Auth, basic_auth, token_auth, Security
from app.haulers.models import Haulers, HaulersSchema, db
from app.representative.models import Representative
from app.mail import send_email
from config import GH_VD_SECRET, MY_URL
 
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import json
import hashlib

haulers = Blueprint('haulers', __name__)
# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
#https://github.com/marshmallow-code/marshmallow-jsonapi
schema = HaulersSchema()
api = Api(haulers)

# Users
class HaulersList(Resource):            
    @token_auth.login_required
    def get(self):        
        query = Haulers.query.all()        
        results = schema.dump(query, many=True).data        
        #return results                    

class HaulersUpdate(Resource):            
    @token_auth.login_required
    def patch(self):
        HAULER_ID = Security.getHaulerId()        
        hauler = Haulers.query.get_or_404(HAULER_ID)
        raw_dict = {"data": {"attributes": request.form, "type": "haulers"}}

        try:            
            schema.validate(raw_dict)                                    
            params = raw_dict['data']['attributes']                                    

            for key, value in params.items():
                if('reps' == key):                    
                    reps = json.loads(value)
                    new_emails = []
                    if len(reps) > 0:
                        for rep in reps:
                            if 'email' in rep: 
                                new_emails.append(rep['email'])                        
                    if len(new_emails):
                        emails = ','.join('"' + item + '"' for item in new_emails)                        
                        db.engine.execute("DELETE FROM haulers_representative WHERE email NOT IN(" + emails + ") AND HAULER_ID="+ str(HAULER_ID) + "")                                    
                        query = db.engine.execute("SELECT email FROM haulers_representative WHERE HAULER_ID="+ str(HAULER_ID) + "")
                        existing_reps = query.fetchall()                        
                        existing_emails = []
                        if existing_reps:
                            for row in existing_reps:
                                existing_emails.append(row.email)
                        
                        for new_email in new_emails:
                            if new_email not in existing_emails:
                                representative = Representative(HAULER_ID=HAULER_ID, email=new_email)
                                representative.add(representative)                                                                
                                m = hashlib.md5()
                                hstr = str(representative.id) + representative.email + GH_VD_SECRET
                                m.update(hstr.encode('utf-8'))
                                token = m.hexdigest()

                                text = "You have been invited to register as a Vendor Representative for  %s <br />" % hauler.name 
                                text += '<b><a href="{0}/signup?token={1}">Please login to complete your registration</a></b> <br /><br />'.format(MY_URL, token) 
                                text += "Already have an account? <a href='http://vd.greenhalosystems.com/login'>Sign in here</a>."
                                send_email('Vendor Invitation', 'no-reply@greenhalosystems.com', new_email, text)
                    else:
                      query = db.engine.execute("DELETE FROM haulers_representative WHERE HAULER_ID="+ str(HAULER_ID) + "")                                  


                            
                setattr(hauler, key, value)
                                        

            hauler.update()            
            results = schema.dump(hauler).data    

            db.session.commit()

            return results['data']['attributes'], 201
        

        except ValidationError as err:
                resp = jsonify({"error": err.messages})
                resp.status_code = 403
                return resp               
                
        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 403
                return resp

        except ValueError as e:
                resp = jsonify({"error": str(e)})
                resp.status_code = 403
                resp.statusText = str(e)
                return resp        

api.add_resource(HaulersList, '/list.json')
api.add_resource(HaulersUpdate, '/update.json')
