# -*- coding: utf-8 -*-
# src/models/ProfessionModel.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Modelo de Profession
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

class ProfessionModel(db.Model):
  """
  User Profession

  Os campos de name, cidade, uf... na biblioteca python_boleto têm prefixo ou sufixo "cedente" 
        Ex: cedente, agencia_cedente, cedente_cidade, cedente_uf
  """

  # table name
  __tablename__ = 'professions'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  descricao = db.Column(db.String(128), nullable=True)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
 

  # class constructor - definir os atributos de classe
  def __init__(self, data):
    """
    Class constructor
    """
    self.name= data.get('name')
    self.descricao= data.get('descricao')
    self.owner_id = data.get('owner_id')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()

  #salvar Profession para o nosso banco de dados
  def save(self):
    db.session.add(self)
    db.session.commit()

  #atualizar o registro do nosso Profession no db
  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()
  #deletar o registro do nosso Profession no db
  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_all_professions(): #obter todos os Profession do banco de dados
    return ProfessionModel.query.all()
  
  @staticmethod
  def get_one_profession(id): #obter um único Profession do db usando campo primary_key
    return ProfessionModel.query.get(id)
    
  @staticmethod
  def get_profession_by_user(owner_id): #obter um único Profession de Profession do db usando o id do user
    return ProfessionModel.query.filter_by(owner_id=owner_id).one() 

  @staticmethod
  def get_profession_by_nossonumero(value): #obter um único Profession de Profession do db usando o id do user
    return ProfessionModel.query.filter_by(nosso_numero=value).one() 
  
  @staticmethod
  def get_profession_by_codigocliente_and_codigobanco(codigocliente, codigobanco):
    return professionModel.query.filter_by(owner_id=codigocliente).filter_by(codigo_banco=codigobanco).one()

  
  """Métodos estáticos adicionais"""
  #retornar uma representação imprimível do objeto ProfessionModel, neste caso estamos apenas retornando o id
  def __repr(self):
    return '<id {}>'.format(self.id)





class ProfessionSchema(Schema):
  id = fields.Int(dump_only=True)
  name= fields.Str(required= True)
  descricao= fields.Integer(required=False)
  owner_id = fields.Int(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
 
  
