from flask import Blueprint, request, jsonify, make_response
from app.auth.models import Auth, basic_auth, token_auth, Security
from app.haulers.models import Haulers, HaulersSchema, db
from flask_restful import Api, Resource
 
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

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

            print('---------------------')
            print(params)

            for key, value in params.items():                
                setattr(hauler, key, value)            

            hauler.update()
            results = schema.dump(hauler).data    

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
