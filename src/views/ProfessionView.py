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
from ..models.UserModel import UserModel, UserSchema

profession_api = Blueprint('profession_api', __name__)
profession_schema = ProfessionSchema()
UserSchema = UserSchema()







@profession_api.route('/profession', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Profession Function
  ---
  /api/professions/profession:
    post:
      summary: Create Profession Function.
      security:
        - APIKeyHeader: []
      tags:
        - Profession
      requestBody:
        description: Profession Functions
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - descricao
              properties:
                name:
                  type: string
                descricao:
                  type: string
                  
      responses:
        '200':
          description: Profession successfully registered
        '400':
          description: Missing data
  
  """
  ##para obter o objeto JSON do corpo da solicitação
  req_data = request.get_json()
  
  #validar e desserializar dados json de entrada do usuário
  req_data['owner_id'] = g.user.get('id')

  data, error = profession_schema.load(req_data)
  if error:
    return custom_response(error, 400)

  post = ProfessionModel(data)
  post.save()
  data = profession_schema.dump(post).data
  return custom_response(data, 201)








@profession_api.route('/professions_al', methods=['GET'])
@Auth.auth_required
def get_all():
  """
  Get All Professions
  --- 
  /api/professions/professions_all:
    get:
      summary: Get all professions Function
      security:
        - APIKeyHeader: []
      tags:
        - Profesion
      
      responses:
        '200':
          description: Returns all professions
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

  posts = ProfessionModel.get_all_professions()
  data = profession_schema.dump(posts, many=True).data
  return custom_response(data, 200)








@profession_api.route('/<int:profession_id>', methods=['GET'])
@Auth.auth_required
def get_one(profession_id):
  """
  Get A Profession
  ---
  /api/professions/{profession_id}:
    get:
      summary: Gets a profession by ID.
      security:
        - APIKeyHeader: []
      tags:
        - Profession
      parameters:
        - in: path
          name: profession_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The profession ID.

      responses:
        '200':
          description: Data this profession successfully
        '400':
          description: user not found
        '401':
          description: Permission denied
  """
  post = ProfessionModel.get_one_profession(profession_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = profession_schema.dump(post).data

  if g.user.get('id') != data.get('owner_id'):
    return custom_response({'error': 'permission denied'}, 401)

  return custom_response(data, 200)








@profession_api.route('/edit/<int:profession_id>', methods=['PUT'])
@Auth.auth_required
def update(profession_id):
  """
  Update A Profession
  ---
  /api/professions/edit/{profession_id}:
    put:
      summary: Update A Profesion.
      security:
        - APIKeyHeader: []
      tags:
        - Profession
      parameters:
        - in: path
          name: profession_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The profession ID.
      requestBody:
        description: Profession Functions
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - descricao
              properties:
                name:
                  type: string
                descricao:
                  type: string
      responses:
        '200':
          description: Profesion successfully update
        '400':
          description: Profession not found
        '401':
          description: Permission denied
        '402':
          description: Missing data
  """
  req_data = request.get_json()

  post = ProfessionModel.get_one_profession(profession_id)
  if not post:
    return custom_response({'error': 'profession not found'}, 400)
  data = profession_schema.dump(post).data

  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 401)
  
  data, error = profession_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 402)
  post.update(data)
  
  data = profession_schema.dump(post).data
  return custom_response(data, 200)










@profession_api.route('/delete/<int:profession_id>', methods=['DELETE'])
@Auth.auth_required
def delete(profession_id):
  """
  Delete A Profession
  ---
  /api/professions/delete/{profession_id}:
    delete:
      summary: Delete a profession by ID.
      security:
        - APIKeyHeader: []
      tags:
        - Profession
      parameters:
        - in: path
          name: profession_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The profession ID.
      responses:
        '200':
          description: Profession successfully deleted
        '400':
          description: Profession not found
        '401':
          description: Permission denied
  """
  post = ProfessionModel.get_one_profession(profession_id)
  if not post:
    return custom_response({'error': 'profession not found'}, 400)
  data = profession_schema.dump(post).data
  
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

