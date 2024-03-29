# -*- coding: utf-8 -*-
# src/models/AddressModel.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Modelo de Address (Ação)
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5


    Dados de Address que serão buscados ao gerar boletos

"""

from marshmallow import fields, Schema
import datetime
from . import db, bcrypt

class AddressModel(db.Model):
  """
  User Address
  """

  # table name
  __tablename__ = 'addresss'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  cidade = db.Column(db.String(128), nullable=False)
  uf = db.Column(db.String(128), nullable=False)
  rua = db.Column(db.String(128), nullable=False)
  bairro = db.Column(db.String(128), nullable=False)
  cep = db.Column(db.String(128), nullable=False)
  deleted = db.Column(db.Boolean, default=False, nullable= True)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)

  # class constructor - definir os atributos de classe
  def __init__(self, data):
    """
    Class constructor
    """
    self.name = data.get('name')
    self.cidade= data.get('cidade')
    self.uf= data.get('uf')
    self.rua= data.get('logradouro')
    self.bairro= data.get('bairro')
    self.cep= data.get('cep')
    self.deleted = data.get('deleted')
    self.owner_id= data.get('owner_id')
    self.entity_id= data.get('entity_id')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()



  #salvar Address para o nosso banco de dados
  def save(self):
    db.session.add(self)
    db.session.commit()

  #atualizar o registro do nosso Address no db
  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()
  #deletar o registro do nosso Address no db
  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_all_addresss(): #obter todos os Address do banco de dados
    return AddressModel.query.all()
  
  @staticmethod
  def get_one_address(id): #obter um único Address do db usando campo primary_key
    return AddressModel.query.filter_by(id=id, deleted=False).fisrt()

  """Métodos estáticos adicionais"""
  #retornar uma representação imprimível do objeto UserModel, neste caso estamos apenas retornando o id
  def __repr(self):
    return '<id {}>'.format(self.id)




class AddressSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  cidade = fields.Str(required=True)
  uf = fields.Str(required=True)
  rua = fields.Str(required=True)
  bairro = fields.Str(required=True)
  cep = fields.Str(required=True)
  deleted= fields.Boolean(required=False)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  owner_id = fields.Int(required=True)
  entity_id= fields.Int(required=True)

