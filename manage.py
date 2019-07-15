# -*- coding: utf-8 -*-
# /manage.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Migrations
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

    Migrar alterações de modelos para o banco de dados.
"""
import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from src.app import create_app, db


env_name = os.getenv('FLASK_ENV')
app = create_app(env_name)

migrate = Migrate(app=app, db=db)

manager = Manager(app=app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
  manager.run()
