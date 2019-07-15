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


@profile_api.route('/profile', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Profile Function
  ---
  /api/profiles/profile:
    post:
      summary: Create Profile Function.
      security:
        - APIKeyHeader: []
      tags:
        - Profile
      requestBody:
        description: Profile Functions
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - Search_area
                - idade
                - sexo
              properties:
                Search_area:
                  type: string
                idade:
                  type: string
                sexo:
                  type: string
                  
      responses:
        '200':
          description: Profile successfully registered
        '400':
          description: Account in post not found
        '401':
          description: Missing data

  """
  ##para obter o objeto JSON do corpo da solicitação
  req_data = request.get_json()
  
  #validar e desserializar dados json de entrada do usuário
  req_data['owner_id'] = g.user.get('id')

  #consultar dados de Entity
  post_entity= EntityModel.get_entity_by_user(req_data['owner_id'])
  if not post_entity:
    return custom_response({'error': 'account in post not found'}, 400)
  data_entity = entity_schema.dump(post_entity).data

  req_data['entity_id']= data_entity['id']

  data, error = profile_schema.load(req_data)
  if error:
    return custom_response(error, 401)

  post = ProfileModel(data)
  post.save()
  data = profile_schema.dump(post).data
  return custom_response(data, 200)







@profile_api.route('/profiles_all', methods=['GET'])
@Auth.auth_required
def get_all():
  """
  Get All Profiles
  --- 
  /api/users/profiles_all:
    get:
      summary: Get all profiles Function
      security:
        - APIKeyHeader: []
      tags:
        - Profile
      
      responses:
        '200':
          description: Returns all profiles
        '400':
          description: User not found
        '401':
          description: Permission denied
  """
  post_user= UserModel.get_one_user(g.user.get('id'))
  if not post_user:
    return custom_response({'error': 'user not found'}, 400)
  data_user= UserSchema.dump(post_user).data

  if data_user.get('role') != 'Admin':
    return custom_response({'error': 'permission denied'}, 401)

  posts = profileModel.get_all_profiles()
  data = Profile_schema.dump(posts, many=True).data
  return custom_response(data, 200)







@profile_api.route('/<int:profile_id>', methods=['GET'])
@Auth.auth_required
def get_one(profile_id):
  """
  Get A Profile
  ---
  /api/profiles/{profile_id}:
    get:
      summary: Gets a profile by ID.
      security:
        - APIKeyHeader: []
      tags:
        - Profile
      parameters:
        - in: path
          name: profile_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The profile ID.

      responses:
        '200':
          description: Data this profile successfully
        '400':
          description: user not found
        '401':
          description: Permission denied
  """
  post = ProfileModel.get_one_profile(profile_id)
  if not post:
    return custom_response({'error': 'post not found'}, 400)
  data = profile_schema.dump(post).data

  if g.user.get('id') != data.get('owner_id'):
    return custom_response({'error': 'permission denied'}, 401)

  return custom_response(data, 200)







@profile_api.route('/edit/<int:profile_id>', methods=['PUT'])
@Auth.auth_required
def update(profile_id):
  """
  Update A Profile
  ---
  /api/profiles/edit/{profile_id}:
    put:
      summary: Update A Profile.
      security:
        - APIKeyHeader: []
      tags:
        - Profile
      parameters:
        - in: path
          name: profile_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The user ID.
      requestBody:
        description: Profile Functions
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - Search_area
                - idade
                - sexo
              properties:
                Search_area:
                  type: string
                idade:
                  type: string
                sexo:
                  type: string
      responses:
        '200':
          description: Profile successfully update
        '400':
          description: Profile not found
        '401':
          description: Permission denied
        '402':
          description: Missing data
  """
  req_data = request.get_json()

  post = ProfileModel.get_one_profile(profile_id)
  if not post:
    return custom_response({'error': 'profile not found'}, 400)
  data = profile_schema.dump(post).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 401)
  
  data, error = profile_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 402)
  post.update(data)
  
  data = profile_schema.dump(post).data
  return custom_response(data, 200)







@profile_api.route('/delete/<int:profile_id>', methods=['DELETE'])
@Auth.auth_required
def delete(profile_id):
  """
  Delete A Profile
  ---
  /api/profiles/delete/{profile_id}:
    delete:
      summary: Delete a profile by ID.
      security:
        - APIKeyHeader: []
      tags:
        - Profile
      parameters:
        - in: path
          name: profile_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The profile ID.
      responses:
        '200':
          description: Profile successfully deleted
        '400':
          description: Profile not found
        '401':
          description: Permission denied
  """
  post = ProfileModel.get_one_profile(profile_id)
  if not post:
    return custom_response({'error': 'profile not found'}, 400)
  data = profile_schema.dump(post).data
  
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 401)

  data['deleted']= True
  post.update(data)
  #post.delete()
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

