# -*- coding: utf-8 -*-
# src/models/ClienteModel.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Modelo de cliente (Ação)
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5


    Dados de cliente que serão buscados ao gerar boletos

"""

from marshmallow import fields, Schema
import datetime
from . import db, bcrypt
from .BoletoModel import BoletoSchema
from .ContaModel import ContaSchema

class ClienteModel(db.Model):
  """
  User Cliente

  Os campos de name, cidade, uf... na biblioteca python_boleto têm prefixo ou sufixo "cedente" 
        Ex: cedente, agencia_cedente, cedente_cidade, cedente_uf
  """

  # table name
  __tablename__ = 'clientes'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  documento = db.Column(db.String(128), nullable=False)
  cidade = db.Column(db.String(128), nullable=False)
  uf = db.Column(db.String(128), nullable=False)
  logradouro = db.Column(db.String(128), nullable=False)
  bairro = db.Column(db.String(128), nullable=False)
  cep = db.Column(db.String(128), nullable=False)
  logoboleto= db.Column(db.Text, nullable=True)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)
  contas = db.relationship('ContaModel', backref='contas', lazy=True)
  boletos = db.relationship('BoletoModel', backref='boletos', lazy=True)

  # class constructor - definir os atributos de classe
  def __init__(self, data):
    """
    Class constructor
    """
    self.name = data.get('name')
    self.cidade= data.get('cidade')
    self.uf= data.get('uf')
    self.logradouro= data.get('logradouro')
    self.bairro= data.get('bairro')
    self.cep= data.get('cep')
    self.logoboleto.get('logoboleto')
    self.documento= data.get('documento')
    self.owner_id= data.get('owner_id')
    self.entity_id= data.get('entity_id')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()



  #salvar cliente para o nosso banco de dados
  def save(self):
    db.session.add(self)
    db.session.commit()

  #atualizar o registro do nosso cliente no db
  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()
  #deletar o registro do nosso cliente no db
  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_all_clientes(): #obter todos os cliente do banco de dados
    return ClienteModel.query.all()
  
  @staticmethod
  def get_one_cliente(id): #obter um único cliente do db usando campo primary_key
    return ClienteModel.query.get(id)

  @staticmethod
  def get_cliente_by_user(owner_id): #obter um único Entity de Entity do db usando o id do user
    return ClienteModel.query.filter_by(owner_id=owner_id).first() 
  
  
  """Métodos estáticos adicionais"""
  #retornar uma representação imprimível do objeto UserModel, neste caso estamos apenas retornando o id
  def __repr(self):
    return '<id {}>'.format(self.id)




class ClienteSchema(Schema):
  id = fields.Int(dump_only=True)
  name = fields.Str(required=True)
  cidade = fields.Str(required=False)
  uf = fields.Str(required=False)
  logradouro = fields.Str(required=False)
  bairro = fields.Str(required=False)
  cep = fields.Str(required=False)
  logoboleto= fields.Str(required=True)
  documento = fields.Str(required=False)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  owner_id = fields.Int(required=True)
  entity_id= fields.Int(required=True)
  contas = fields.Nested(ContaSchema, many=True)
  boletos = fields.Nested(BoletoSchema, many=True)

