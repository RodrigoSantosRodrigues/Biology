# -*- coding: utf-8 -*-
#/src/views/ContaView.py

"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        API do Conta
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

  
"""

from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.ContaModel import ContaModel, ContaSchema
from ..models.ClienteModel import ClienteModel, ClienteSchema

conta_api = Blueprint('conta_api', __name__)
conta_schema = ContaSchema()
cliente_schema= ClienteSchema()



@conta_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Conta Function
  """
  ##para obter o objeto JSON do corpo da solicitação
  req_data = request.get_json()
  
  #validar e desserializar dados json de entrada do usuário
  req_data['owner_id'] = g.user.get('id')

  data, error = conta_schema.load(req_data)
  if error:
    return custom_response(error, 400)

  post_conta= ContaModel.get_conta_by_nossonumero(req_data['nosso_numero'])
  if post_conta:
    message = {'error': 'Value nosso_numero already exists'}
    return custom_response(message, 400)

  #consultar dados de Entity
  post_cliente= ClienteModel.get_one_cliente(req_data['cliente_id'])
  if not post_cliente:
    return custom_response({'error': 'account in post not found'}, 404)
  data_cliente = cliente_schema.dump(post_cliente).data

  req_data['cliente_id']= data_cliente['id']

  post = ContaModel(data)
  post.save()
  data = conta_schema.dump(post).data
  return custom_response(data, 201)




@conta_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Contas
  """
  posts = ContaModel.get_all_contas()
  data = conta_schema.dump(posts, many=True).data
  return custom_response(data, 200)




@conta_api.route('/<int:conta_id>', methods=['GET'])
def get_one(conta_id):
  """
  Get A Conta
  """
  post = ContaModel.get_one_conta(conta_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = conta_schema.dump(post).data
  return custom_response(data, 200)




@conta_api.route('/<int:conta_id>', methods=['PUT'])
@Auth.auth_required
def update(conta_id):
  """
  Update A Conta
  """
  req_data = request.get_json()
  post = ContaModel.get_one_conta(conta_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = conta_schema.dump(post).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)
  
  data, error = conta_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)
  post.update(data)
  
  data = conta_schema.dump(post).data
  return custom_response(data, 200)



@conta_api.route('/<int:conta_id>', methods=['DELETE'])
@Auth.auth_required
def delete(conta_id):
  """
  Delete A Conta
  """
  post = ContaModel.get_one_conta(conta_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = conta_schema.dump(post).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)

  post.delete()
  return custom_response({'message': 'deleted'}, 204)


  

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )

