# -*- coding: utf-8 -*-
# src/models/EntityModel.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Modelo de Entity
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

    Modelos que determinam as estruturas lógicas de um banco de dados. Simplificando, determina como as tabelas
    ficariam no banco de dados. Os modelos definem como os registros podem ser manipulados ou recuperados no 
    banco de dados.

    Dados de Entity 

    
"""

from marshmallow import fields, Schema
import datetime
from . import db, bcrypt
from .AddressModel import AddressSchema
from .ProfileModel import ProfileSchema

class EntityModel(db.Model):
  """
  User Entity
  """

  # table name
  __tablename__ = 'entities'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  documento = db.Column(db.String(128), nullable=False, unique=True)
  image= db.Column(db.Text, nullable=True)
  deleted = db.Column(db.Boolean, default=False, nullable= True)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
  address = db.relationship('AddressModel', backref='adresss', lazy=True)
  #Profile = db.relationship('ProfileModel', backref='profiles', lazy=True)

  # class constructor - definir os atributos de classe
  def __init__(self, data):
    """
    Class constructor
    """
    self.name= data.get('name')
    self.documento= data.get('documento')
    self.image.get('image')
    self.owner_id= data.get('owner_id')
    self.deleted = data.get('deleted')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()

  #salvar Entity para o nosso banco de dados
  def save(self):
    db.session.add(self)
    db.session.commit()

  #atualizar o registro do nosso Entity no db
  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()
  #deletar o registro do nosso Entity no db
  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_all_Entities(): #obter todos os Entity do banco de dados
    return EntityModel.query.all()
  
  @staticmethod
  def get_one_entity(id): #obter um único Entity do db usando campo primary_key
    return EntityModel.query.filter_by(id=id, deleted=False).fisrt()
  
  @staticmethod
  def get_entity_by_user(owner_id):
    return EntityModel.query.filter_by(owner_id= owner_id, deleted=False).fisrt()
  
  @staticmethod
  def get_entity_by_documento(documento):
    return EntityModel.query.filter_by(documento= documento, deleted=False).fisrt()

  """Métodos estáticos adicionais"""
  #retornar uma representação imprimível do objeto UserModel, neste caso estamos apenas retornando o id
  def __repr(self):
    return '<id {}>'.format(self.id)




class EntitySchema(Schema):
  id = fields.Int(dump_only=True)
  name= fields.Str(required=True)
  documento= fields.Str(required=True)
  image= fields.Str(required=False)
  deleted= fields.Boolean(required=False)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  owner_id = fields.Int(required=True)
  address = fields.Nested(AddressSchema, many=True)
  profile = fields.Nested(ProfileSchema, many=True)
  
