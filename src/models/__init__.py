#src/models/__init__.py

"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        __init__
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

    
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# initialize our db
db = SQLAlchemy()
bcrypt = Bcrypt()

from .ProfessionModel import ProfessionModel, ProfessionSchema
from .ProfileModel import ProfileModel, ProfileSchema
from .AddressModel import AddressModel, AddressSchema
from .EntityModel import EntityModel, EntitySchema
from .UserModel import UserModel, UserSchema
