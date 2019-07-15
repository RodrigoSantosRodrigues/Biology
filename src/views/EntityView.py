# -*- coding: utf-8 -*-
#/src/views/EntityView.py

"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        API do Entity
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

  
"""

from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.EntityModel import EntityModel, EntitySchema
from ..models.UserModel import UserModel, UserSchema

entity_api = Blueprint('entity_api', __name__)
entity_schema = EntitySchema()
UserSchema = UserSchema()



@entity_api.route('/entity', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Entity Function
   ---
  /api/entities/entity:
    post:
      summary: Create Profession Function.
      security:
        - APIKeyHeader: []
      tags:
        - Entity
      requestBody:
        description: Entity Functions
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - documento
              properties:
                name:
                  type: string
                documento:
                  type: string
                image:
                  type: string
                  
      responses:
        '200':
          description: Entity successfully registered
        '400':
          description: Missing data
        '401':
          description: Document already exists for this user, please supply another document
        '402':
          description: There is already a registration for this user
  """
  ##para obter o objeto JSON do corpo da solicitação
  req_data = request.get_json()
  
  #validar e desserializar dados json de entrada do usuário
  req_data['owner_id'] = g.user.get('id')
  data, error = entity_schema.load(req_data)
  if error:
    return custom_response(error, 400)
  
  # check if documento already exist in the db
  document_in_db = EntityModel.get_entity_by_documento(data.get('documento'))
  if document_in_db:
    message = {'error': 'Document already exists for this user, please supply another document'}
    return custom_response(message, 401)
  
  # check if user already exist in the db
  user_in_db = EntityModel.get_entity_by_user(data.get('owner_id'))
  if user_in_db:
    message = {'error': 'There is already a registration for this user'}
    return custom_response(message, 402)
  
  post = EntityModel(data)
  post.save()
  data = entity_schema.dump(post).data
  return custom_response(data, 200)








@entity_api.route('/entities_all', methods=['GET'])
@Auth.auth_required
def get_all():
  """
  Get All Entitys
  --- 
  /api/entities/entities_all:
    get:
      summary: Get all entities Function
      security:
        - APIKeyHeader: []
      tags:
        - Entity
      
      responses:
        '200':
          description: Returns all entities
        '400':
          description: User not found
        '401':
          description: Permission denied
  """
  post_user= UserModel.get_one_user(g.user.get('id'))
  if not post_user:
    return custom_response({'error': 'user not found'}, 400)
  data_user= UserSchema.dump(post_user).data
  print(data_user)
  if data_user.get('role') != 'Admin':
    return custom_response({'error': 'permission denied'}, 401)

  posts = EntityModel.get_all_Entities()
  data = entity_schema.dump(posts, many=True).data
  return custom_response(data, 200)







@entity_api.route('/<int:entity_id>', methods=['GET'])
@Auth.auth_required
def get_one(entity_id):
  """
  Get A Entity
  ---
  /api/entities/{entity_id}:
    get:
      summary: Gets a entity by ID.
      security:
        - APIKeyHeader: []
      tags:
        - Entity
      parameters:
        - in: path
          name: entity_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The entity ID.

      responses:
        '200':
          description: Data this entity successfully
        '400':
          description: user not found
        '401':
          description: Permission denied
  """
  post = EntityModel.get_one_entity(entity_id)
  if not post:
    return custom_response({'error': 'post not found'}, 400)
  data = entity_schema.dump(post).data

  if g.user.get('id') != data.get('owner_id'):
    return custom_response({'error': 'permission denied'}, 401)

  return custom_response(data, 200)








@entity_api.route('/edit/<int:entity_id>', methods=['PUT'])
@Auth.auth_required
def update(entity_id):
  """
  Update A Entity
  ---
  /api/entities/edit/{entity_id}:
    put:
      summary: Update A Entity.
      security:
        - APIKeyHeader: []
      tags:
        - Entity
      parameters:
        - in: path
          name: entity_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The Entity ID.
      requestBody:
        description: Entity Functions
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - documento
              properties:
                name:
                  type: string
                documento:
                  type: string
                image:
                  type: string
      responses:
        '200':
          description: Entity successfully update
        '400':
          description: Entity not found
        '401':
          description: Permission denied
        '402':
          description: Missing data
        '403':
          description: Document already exists for this user, please supply another document
        '404':
          description: There is already a registration for this user
  """
  req_data = request.get_json()
  post = EntityModel.get_one_entity(entity_id)
  if not post:
    return custom_response({'error': 'entity not found'}, 400)
  data = entity_schema.dump(post).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 401)
  
  data, error = entity_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 402)
  post.update(data)

  # check if documento already exist in the db
  document_in_db = EntityModel.get_entity_by_documento(data.get('documento'))
  if document_in_db:
    message = {'error': 'Document already exists for this user, please supply another document'}
    return custom_response(message, 403)
  
  # check if user already exist in the db
  user_in_db = EntityModel.get_entity_by_user(data.get('owner_id'))
  if user_in_db:
    message = {'error': 'There is already a registration for this user'}
    return custom_response(message, 404)
  
  data = entity_schema.dump(post).data
  return custom_response(data, 200)









@entity_api.route('/delete/<int:entity_id>', methods=['DELETE'])
@Auth.auth_required
def delete(entity_id):
  """
  Delete A Entity
  ---
  /api/entities/delete/{entity_id}:
    delete:
      summary: Delete a entity by ID.
      security:
        - APIKeyHeader: []
      tags:
        - Entity
      parameters:
        - in: path
          name: entity_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The entity ID.
      responses:
        '200':
          description: Entity successfully deleted
        '400':
          description: Entity not found
        '401':
          description: Permission denied
  """
  post = EntityModel.get_one_entity(entity_id)
  if not post:
    return custom_response({'error': 'entity not found'}, 400)
  data = entity_schema.dump(post).data
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 401)

  data['deleted']= True
  post.update(data)
  #post.delete()
  return custom_response({'message': 'deleted'}, 200)


  




def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )

