# -*- coding: utf-8 -*-
# src/models/ProfileModel.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Modelo de Profile
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

    Modelos que determinam as estruturas lógicas de um banco de dados. Simplificando, determina como as tabelas
    ficariam no banco de dados. Os modelos definem como os registros podem ser manipulados ou recuperados no 
    banco de dados.

    Dados de Profile que serão buscados ao gerar boletos

    
"""

from marshmallow import fields, Schema
import datetime
from . import db, bcrypt

class ProfileModel(db.Model):
  """
  User Profile

  """

  # table name
  __tablename__ = 'profiles'

  id = db.Column(db.Integer, primary_key=True)
  Search_area = db.Column(db.String(128), nullable=False)
  idade = db.Column(db.Integer, nullable=False)
  sexo = db.Column(db.String(128), nullable=False)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  deleted = db.Column(db.Boolean, default=False, nullable= True)
  astyanax = db.Column(db.Boolean, default=False, nullable= True)
  kariofish = db.Column(db.Boolean, default=False, nullable= True)
  profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)
  entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
 

  # class constructor - definir os atributos de classe
  def __init__(self, data):
    """
    Class constructor
    """
    self.Search_area= data.get('Search_area')
    self.idade= data.get('idade')
    self.sexo = data.get('sexo')
    self.astyanax = data.get('astyanax')
    self.kariofish = data.get('kariofish')
    self.profession_id = data.get('profession_id')
    self.entity_id= data.get('entity_id')
    self.owner_id = data.get('owner_id')
    self.deleted = data.get('deleted')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()

  #salvar Profile para o nosso banco de dados
  def save(self):
    db.session.add(self)
    db.session.commit()

  #atualizar o registro do nosso Profile no db
  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()
  #deletar o registro do nosso Profile no db
  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_all_profiles(): #obter todos os Profile do banco de dados
    return ProfileModel.query.all()
  
  @staticmethod
  def get_one_profile(id): #obter um único Profile do db usando campo primary_key
    return ProfileModel.query.filter_by(id=id, deleted=False).first()
    

  
  """Métodos estáticos adicionais"""
  #retornar uma representação imprimível do objeto ProfileModel, neste caso estamos apenas retornando o id
  def __repr(self):
    return '<id {}>'.format(self.id)





class ProfileSchema(Schema):
  id = fields.Int(dump_only=True)
  Search_area= fields.Str(required= True)
  idade= fields.Integer(required=True)
  sexo = fields.Str(required=True)
  deleted= fields.Boolean(required=False)
  astyanax = fields.Boolean(required=False)
  kariofish = fields.Boolean(required=False)
  profession_id= fields.Int(required=True)
  entity_id= fields.Int(required=True)
  owner_id = fields.Int(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
 
  
