from flask import Blueprint, request, jsonify, make_response
from app.haulersImages.models import HaulersImages, HaulersImagesSchema, db
from flask_restful import Api, Resource
from app.auth.models import token_auth, Security
import time
import hashlib
import random
import string

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

haulers_images_bp = Blueprint('haulers_images', __name__)

schema = HaulersImagesSchema()
api = Api(haulers_images_bp)

class HaulersImagesList(Resource):
    @token_auth.login_required
    def get(self):
        HAULER_ID = Security.getHaulerId()
        db.session.commit()
        query = db.engine.execute("SELECT * FROM haulers_images WHERE HAULER_ID="+ str(HAULER_ID) + "")
        query = query.fetchall()                
        query = HaulersImages.query.filter(HaulersImages.HAULER_ID==HAULER_ID).all()                
        results = schema.dump(query, many=True).data        
        return results


    @token_auth.login_required
    def post(self):                   
        raw_dict = {"data": {"attributes": request.form, "type": "haulers_images"}}                
        try:
                HAULER_ID = Security.getHaulerId()
                schema.validate(raw_dict)                                                
                params = raw_dict['data']['attributes']
                uid = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
                m = hashlib.md5()
                m.update(str(HAULER_ID).encode('utf-8') + str(time.time()).encode('utf-8') + uid.encode('utf-8'))                
                filename = m.hexdigest()                                                                            
                haulersImage = HaulersImages(
                        HAULER_ID=Security.getHaulerId(),
                        name = filename,
                        type = 'jpg'
                        )
                
                file = request.files['image']                
                haulersImage.save_file(file, filename)
                haulersImage.add(haulersImage)

                response = make_response("HTTP/1.1 201 CREATED", 201)            
                return (response)    
            
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

class HaulersImagesUpdate(Resource):
    @token_auth.login_required
    def delete(self, id):        
        HAULER_ID = Security.getHaulerId()
        row = HaulersImages.query.filter(HaulersImages.id==id, HaulersImages.HAULER_ID==HAULER_ID).first_or_404()
        try:                
                delete = row.delete(row)  
                print("==============DELETE===============")               
                response = make_response("HTTP/1.1 204 DELETED", 204)
                response.status_code = 204
                return (response)
        
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

api.add_resource(HaulersImagesList, '.json')
api.add_resource(HaulersImagesUpdate, '/<int:id>.json')
