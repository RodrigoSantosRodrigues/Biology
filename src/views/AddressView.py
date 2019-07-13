# -*- coding: utf-8 -*-
#/src/views/AddressView.py

"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        API do Address
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

  
"""

from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.AddressModel import AddressModel, AddressSchema
from ..models.UserModel import UserModel, UserSchema

address_api = Blueprint('address_api', __name__)
address_schema = AddressSchema()
UserSchema = UserSchema()


@address_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Address Function
  """
  ##para obter o objeto JSON do corpo da solicitação
  req_data = request.get_json()
  
  #validar e desserializar dados json de entrada do usuário
  req_data['owner_id'] = g.user.get('id')

  data, error = address_schema.load(req_data)
  if error:
    return custom_response(error, 400)

  post = AddressModel(data)
  post.save()
  data = address_schema.dump(post).data
  return custom_response(data, 200)




@address_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Addresss
  """
  req_data['owner_id'] = g.user.get('id')

  post_user= UserModel.get_one_user(req_data.get('owner_id'))
  if not post_user:
    return custom_response({'error': 'user not found'}, 400)
  data_user= UserSchema.dump(post_user).data

  if data_user.get('role') != 'Admin':
    return custom_response({'error': 'permission denied'}, 401)

  posts = AddressModel.get_all_addresss()
  data = address_schema.dump(posts, many=True).data
  return custom_response(data, 200)




@address_api.route('/<int:address_id>', methods=['GET'])
def get_one(address_id):
  """
  Get A Address
  """
  
  post = AddressModel.get_one_address(address_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = address_schema.dump(post).data
  return custom_response(data, 200)




@address_api.route('/<int:address_id>', methods=['PUT'])
@Auth.auth_required
def update(address_id):
  """
  Update A Address
  """
  req_data = request.get_json()
  post = AddressModel.get_one_address(address_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = address_schema.dump(post).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)
  
  data, error = address_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)
  post.update(data)
  
  data = address_schema.dump(post).data
  return custom_response(data, 200)



@address_api.route('/<int:address_id>', methods=['DELETE'])
@Auth.auth_required
def delete(address_id):
  """
  Delete A Address
  """
  post = AddressModel.get_one_address(address_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = address_schema.dump(post).data
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

