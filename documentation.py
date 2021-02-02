# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 19:05:52 2021

@author: JSONAPI
"""

from flask import Flask
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList
from flask_sqlalchemy import SQLAlchemy
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

# Create the Flask application and the Flask-SQLAlchemy object.
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# Create model
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

# Create the database.
db.create_all()

# Create schema
class PersonSchema(Schema):
    class Meta:
        type_ = 'person'
        self_view = 'person_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'person_list'

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()

# Create resource managers
class PersonList(ResourceList):
    schema = PersonSchema
    data_layer = {'session': db.session,
                  'model': Person}

class PersonDetail(ResourceDetail):
    schema = PersonSchema
    data_layer = {'session': db.session,
                  'model': Person}

# Create the API object
api = Api(app)
api.route(PersonList, 'person_list', '/persons')
api.route(PersonDetail, 'person_detail', '/persons/<int:id>')

# Start the flask loop
if __name__ == '__main__':
    app.run()