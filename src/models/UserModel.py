# -*- coding: utf-8 -*-
# src/models/UserModel.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Modelo de usuário
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

    Modelos que determinam as estruturas lógicas de um banco de dados. Simplificando, determina como as tabelas
    ficariam no banco de dados. Os modelos definem como os registros podem ser manipulados ou recuperados no 
    banco de dados.
"""

from marshmallow import fields, Schema
import datetime
from . import db, bcrypt
from .BoletoModel import BoletoSchema
from .EntityModel import EntitySchema
from .ClienteModel import ClienteSchema

class UserModel(db.Model):
  """
  User Model
  """

  # table name
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  email = db.Column(db.String(128), unique=True, nullable=False)
  password = db.Column(db.String(128), nullable=False)
  role = db.Column(db.String(128), nullable=False)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  entities = db.relationship('EntityModel', backref='entitiess', lazy=True)
 

  # class constructor - definir os atributos de classe
  def __init__(self, data):
    """
    Class constructor
    """
    self.name = data.get('name')
    self.email = data.get('email')
    self.password = self.__generate_hash(data.get('password'))
    self.role = data.get('role')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()

  #salvar usuários para o nosso banco de dados
  def save(self):
    db.session.add(self)
    db.session.commit()
  
  #atualizar o registro do nosso usuário no db
  def update(self, data):
    for key, item in data.items():
      if key == 'password':
        self.password = self.__generate_hash(value)
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()
  
  #excluir o registro do db
  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_all_users(): #obter todos os usuários do banco de dados 
    return UserModel.query.all()

  @staticmethod
  def get_one_user(id): #obter um único usuário do db usando campo primary_key
    return UserModel.query.get(id)
  
  @staticmethod
  def get_user_by_email(value):
    return UserModel.query.filter_by(email=value).first()
  
  """Métodos estáticos adicionais"""
  #saremos __generate_hash() a senha do usuário de hash antes de salvá-lo no banco de dados
  def __generate_hash(self, password):
    return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")
  
  #será usado posteriormente em nosso código para validar a senha do usuário durante o login
  def check_hash(self, password):
    return bcrypt.check_password_hash(self.password, password)
  
  #retornar uma representação imprimível do objeto UserModel, neste caso estamos apenas retornando o id
  def __repr(self):
    return '<id {}>'.format(self.id)

class UserSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  email = fields.Email(required=True)
  password = fields.Str(required=True, load_only=True)
  role = fields.Str(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  entities = fields.Nested(EntitySchema, many=True)
 