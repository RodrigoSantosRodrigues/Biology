# -*- coding: utf-8 -*-
#/src/views/ProfileView.py

"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        API do Profile
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

  
"""

from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.ProfileModel import ProfileModel, ProfileSchema
from ..models.EntityModel import EntityModel, EntitySchema

profile_api = Blueprint('profile_api', __name__)
profile_schema = ProfileSchema()
entity_schema= EntitySchema()



@profile_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Profile Function
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

  data, error = profile_schema.load(req_data)
  if error:
    return custom_response(error, 400)

  post = ProfileModel(data)
  post.save()
  data = profile_schema.dump(post).data
  return custom_response(data, 201)




@profile_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Profiles
  """
  posts = profileModel.get_all_profiles()
  data = Profile_schema.dump(posts, many=True).data
  return custom_response(data, 200)




@profile_api.route('/<int:profile_id>', methods=['GET'])
def get_one(profile_id):
  """
  Get A Profile
  """
  post = ProfileModel.get_one_profile(profile_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = profile_schema.dump(post).data
  return custom_response(data, 200)




@profile_api.route('/<int:profile_id>', methods=['PUT'])
@Auth.auth_required
def update(profile_id):
  """
  Update A Profile
  """
  req_data = request.get_json()
  post = ProfileModel.get_one_profile(profile_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = profile_schema.dump(post).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)
  
  data, error = profile_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)
  post.update(data)
  
  data = profile_schema.dump(post).data
  return custom_response(data, 200)



@profile_api.route('/<int:profile_id>', methods=['DELETE'])
@Auth.auth_required
def delete(profile_id):
  """
  Delete A Profile
  """
  post = ProfileModel.get_one_profile(profile_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = profile_schema.dump(post).data
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

