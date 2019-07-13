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

from flask import Flask

from .config import app_config
from .models import db, bcrypt

# import user_api blueprint
from .views.UserView import user_api as user_blueprint
from .views.BoletoView import boleto_api as boleto_blueprint
from .views.EntityView import entity_api as entity_blueprint
from .views.ClienteView import cliente_api as cliente_blueprint
from .views.ContaView import conta_api as conta_blueprint

def create_app(env_name):
  """
    param: env_name -> necessário para carregar nossa configuração no modo development ou production
    Create app
  """
  
  # app initiliazation
  app = Flask(__name__)

  app.config.from_object(app_config[env_name])

  # initializing bcrypt and db
  bcrypt.init_app(app)
  db.init_app(app)

  app.register_blueprint(user_blueprint, url_prefix='/api/users')
  app.register_blueprint(boleto_blueprint, url_prefix='/api/boletos')
  app.register_blueprint(entity_blueprint, url_prefix='/api/entities')
  app.register_blueprint(cliente_blueprint, url_prefix='/api/clientes')
  app.register_blueprint(conta_blueprint, url_prefix='/api/contas')

  @app.route('/', methods=['GET'])
  def index():
    """
    Home
    """
    return "Congratulations! You're in Boleto Viewer."

  return app

