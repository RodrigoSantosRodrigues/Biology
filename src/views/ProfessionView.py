# -*- coding: utf-8 -*-
#/src/views/ProfessionView.py

"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        API do Profession
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

  
"""

from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.ProfessionModel import ProfessionModel, ProfessionSchema

profession_api = Blueprint('profession_api', __name__)
profession_schema = ProfessionSchema()



@profession_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Profession Function
  """
  ##para obter o objeto JSON do corpo da solicitação
  req_data = request.get_json()
  
  #validar e desserializar dados json de entrada do usuário
  req_data['owner_id'] = g.user.get('id')

  data, error = profession_schema.load(req_data)
  if error:
    return custom_response(error, 400)

  post_profession= ProfessionModel.get_profession_by_nossonumero(req_data['nosso_numero'])
  if post_profession:
    message = {'error': 'Value nosso_numero already exists'}
    return custom_response(message, 400)

  post = ProfessionModel(data)
  post.save()
  data = profession_schema.dump(post).data
  return custom_response(data, 201)




@profession_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Professions
  """
  posts = ProfessionModel.get_all_professions()
  data = profession_schema.dump(posts, many=True).data
  return custom_response(data, 200)




@profession_api.route('/<int:profession_id>', methods=['GET'])
def get_one(profession_id):
  """
  Get A Profession
  """
  post = ProfessionModel.get_one_profession(profession_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = profession_schema.dump(post).data
  return custom_response(data, 200)




@profession_api.route('/<int:profession_id>', methods=['PUT'])
@Auth.auth_required
def update(profession_id):
  """
  Update A Profession
  """
  req_data = request.get_json()
  post = ProfessionModel.get_one_profession(profession_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = profession_schema.dump(post).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)
  
  data, error = profession_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)
  post.update(data)
  
  data = profession_schema.dump(post).data
  return custom_response(data, 200)



@profession_api.route('/<int:profession_id>', methods=['DELETE'])
@Auth.auth_required
def delete(profession_id):
  """
  Delete A Profession
  """
  post = ProfessionModel.get_one_profession(profession_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = profession_schema.dump(post).data
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

