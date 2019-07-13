# -*- coding: utf-8 -*-
# src/models/ContaModel.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Modelo de Conta
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

    Modelos que determinam as estruturas lógicas de um banco de dados. Simplificando, determina como as tabelas
    ficariam no banco de dados. Os modelos definem como os registros podem ser manipulados ou recuperados no 
    banco de dados.

    Dados de Conta que serão buscados ao gerar boletos

    
"""

from marshmallow import fields, Schema
import datetime
from . import db, bcrypt

class ContaModel(db.Model):
  """
  User Conta

  Os campos de name, cidade, uf... na biblioteca python_boleto têm prefixo ou sufixo "cedente" 
        Ex: cedente, agencia_cedente, cedente_cidade, cedente_uf
  """

  # table name
  __tablename__ = 'contas'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False)
  codigo_banco = db.Column(db.String(128), nullable=False)
  convenio = db.Column(db.String(128), nullable=False)
  carteira = db.Column(db.String(128), nullable=False)
  agencia = db.Column(db.String(128), nullable=False)
  conta = db.Column(db.String(128), nullable=False)
  nosso_numero = db.Column(db.String(128), nullable=False, unique=True)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
 

  # class constructor - definir os atributos de classe
  def __init__(self, data):
    """
    Class constructor
    """
    self.name= data.get('name')
    self.codigo_banco= data.get('codigo_banco')
    self.convenio = data.get('convenio')
    self.carteira = data.get('carteira')
    self.agencia= data.get('agencia')
    self.conta= data.get('conta')
    self.nosso_numero = data.get('nosso_numero')
    self.owner_id= data.get('owner_id')
    self.cliente_id= data.get('cliente_id')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()

  #salvar Conta para o nosso banco de dados
  def save(self):
    db.session.add(self)
    db.session.commit()

  #atualizar o registro do nosso Conta no db
  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()
  #deletar o registro do nosso Conta no db
  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_all_Contas(): #obter todos os Conta do banco de dados
    return ContaModel.query.all()
  
  @staticmethod
  def get_one_conta(id): #obter um único Conta do db usando campo primary_key
    return ContaModel.query.get(id)
    
  @staticmethod
  def get_conta_by_user(owner_id): #obter um único Conta de Conta do db usando o id do user
    return ContaModel.query.filter_by(owner_id=owner_id).first() 

  @staticmethod
  def get_conta_by_nossonumero(value): #obter um único Conta de Conta do db usando o id do user
    return ContaModel.query.filter_by(nosso_numero=value).first() 
  
  @staticmethod
  def get_conta_by_codigocliente_and_codigobanco(codigocliente, codigobanco):
    return ContaModel.query.filter_by(owner_id=codigocliente).filter_by(codigo_banco=codigobanco).first()

  
  """Métodos estáticos adicionais"""
  #retornar uma representação imprimível do objeto UserModel, neste caso estamos apenas retornando o id
  def __repr(self):
    return '<id {}>'.format(self.id)




class ContaSchema(Schema):
  id = fields.Int(dump_only=True)
  name= fields.Str(required=True)
  codigo_banco = fields.Str(required=True)
  convenio = fields.Str(required=True)
  carteira = fields.Str(required=True)
  agencia = fields.Str(required=True)
  conta = fields.Str(required=True)
  nosso_numero = fields.Str(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
  owner_id = fields.Int(required=True)
  cliente_id= fields.Int(required=True)
  
