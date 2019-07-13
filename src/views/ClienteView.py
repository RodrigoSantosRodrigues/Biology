# -*- coding: utf-8 -*-
#/src/views/ClienteView.py

"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        API do Cliente
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

  
"""

from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.ClienteModel import ClienteModel, ClienteSchema
from ..models.EntityModel import EntityModel, EntitySchema

cliente_api = Blueprint('cliente_api', __name__)
cliente_schema = ClienteSchema()
entity_schema= EntitySchema()



@cliente_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Cliente Function
  """
  ##para obter o objeto JSON do corpo da solicitação
  req_data = request.get_json()
  
  #validar e desserializar dados json de entrada do usuário
  req_data['owner_id'] = g.user.get('id')

  #consultar dados de Entity
  post_entity= EntityModel.get_entity_by_user(req_data['owner_id'])
  if not post_entity:
    return custom_response({'error': 'account in post not found'}, 404)
  data_entity = entity_schema.dump(post_entity).data

  req_data['entity_id']= data_entity['id']

  data, error = cliente_schema.load(req_data)
  if error:
    return custom_response(error, 400)

  post = ClienteModel(data)
  post.save()
  data = cliente_schema.dump(post).data
  return custom_response(data, 201)




@cliente_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Clientes
  """
  posts = ClienteModel.get_all_clientes()
  data = cliente_schema.dump(posts, many=True).data
  return custom_response(data, 200)




@cliente_api.route('/<int:cliente_id>', methods=['GET'])
def get_one(cliente_id):
  """
  Get A Cliente
  """
  post = ClienteModel.get_one_cliente(cliente_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = cliente_schema.dump(post).data
  return custom_response(data, 200)




@cliente_api.route('/<int:cliente_id>', methods=['PUT'])
@Auth.auth_required
def update(cliente_id):
  """
  Update A Cliente
  """
  req_data = request.get_json()
  post = ClienteModel.get_one_cliente(cliente_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = cliente_schema.dump(post).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)
  
  data, error = cliente_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)
  post.update(data)
  
  data = cliente_schema.dump(post).data
  return custom_response(data, 200)



@cliente_api.route('/<int:cliente_id>', methods=['DELETE'])
@Auth.auth_required
def delete(cliente_id):
  """
  Delete A Cliente
  """
  post = ClienteModel.get_one_cliente(cliente_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = cliente_schema.dump(post).data
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

