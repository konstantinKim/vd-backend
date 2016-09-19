from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()

class Statistics():        
    reused = 0
    recycled = 0
    disposed = 0
    def recyclingTotals():
        pass


        