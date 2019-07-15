# -*- coding: utf-8 -*-
# src / app.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Create app
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5


"""

from flask import Flask, render_template

from .config import app_config
from .models import db, bcrypt

# import user_api blueprint
from .views.UserView import user_api as user_blueprint
from .views.EntityView import entity_api as entity_blueprint
from .views.AddressView import address_api as address_blueprint
from .views.ProfileView import profile_api as profile_blueprint
from .views.ProfessionView import profession_api as profession_blueprint

from flask_swagger_ui import get_swaggerui_blueprint


def create_app(env_name):
  """
    param: env_name -> necessário para carregar nossa configuração no modo development ou production

    DOC API USING SWAGGER UI  
    Create app
  """
  
  # app initiliazation
  APP = Flask(__name__)

  APP.config.from_object(app_config[env_name])

  # initializing bcrypt and db
  bcrypt.init_app(APP)
  db.init_app(APP)

  ### swagger specific ###
  SWAGGER_URL = '/apidocs'
  API_URL = '/static/api/openapi.json'
  SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Biology Database API"
    }
  )
  APP.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
  ### end swagger specific ###


  APP.register_blueprint(user_blueprint, url_prefix='/api/users')
  APP.register_blueprint(entity_blueprint, url_prefix='/api/entities')
  APP.register_blueprint(address_blueprint, url_prefix='/api/addresss')
  APP.register_blueprint(profile_blueprint, url_prefix='/api/profiles')
  APP.register_blueprint(profession_blueprint, url_prefix='/api/professions')



  @APP.route('/', methods=['GET'])
  def index():
    """
    Home
    """
    return render_template('index.html')

  return APP