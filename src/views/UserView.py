# -*- coding: utf-8 -*-
#/src/views/UserView

"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        API do usuário
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

    Quando um usuário cria uma conta, queremos retornar ao usuário um token jwt que será usado para qualquer
    solicitação de autenticação.

    request- contém todas as informações de solicitação do usuário, incluindo cabeçalhos, corpo e outras 
             informações.
    json- para serializar a saída JSON.

    Response- para criar nosso objeto de resposta.

    Blueprint- para agrupar nossos recursos de usuário flask.

                  Nota: Um usuário pode apenas atualizar e excluir sua própria conta.
"""

from flask import request, json, Response, Blueprint, g
from ..models.UserModel import UserModel, UserSchema
from ..shared.Authentication import Auth

#aplicativo de blueprint que usaremos para todos os recursos do usuário.
user_api = Blueprint('user_api', __name__) 
user_schema = UserSchema()




@user_api.route('/user', methods=['POST'])
def create():
  """
  

  Create User Function
  --- 
  /api/users/user:
    post:
      summary: Create a user Function. It will return the JWT token if the request was successful
      tags:
        - User
      requestBody:
        description: User Functions
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - email
                - password
                - role
              properties:
                name:
                  type: string
                email:
                  type: string
                password:
                  type: string
                role:
                  type: string
  
      responses:
        '200':
          description: User successfully registered
        '400':
          description: User already exist, please supply another email address

  """
  req_data = request.get_json() #para obter o objeto JSON do corpo da solicitação
  
  #validar e desserializar dados json de entrada do usuário, definimos 
  # UserSchemaclasse em nosso modelo UserModel.
  data, error = user_schema.load(req_data)

  if error:
    return custom_response(error, 400)
  
  # check if user already exist in the db
  user_in_db = UserModel.get_user_by_email(data.get('email'))
  if user_in_db:
    message = {'error': 'User already exist, please supply another email address'}
    return custom_response(message, 400)
  
  user = UserModel(data)
  user.save()
  ser_data = user_schema.dump(user).data
  #gerar token do utilizador e será usado posteriormente para decodificar token do utilizado
  token = Auth.generate_token(ser_data.get('id'))
  return custom_response({'jwt_token': token}, 200)







@user_api.route('/users_all', methods=['GET'])
@Auth.auth_required
def get_all():
  """
  Get all users

   endpoint que obterá todos os dados do usuário no banco de dados e 
   somente um usuário com um token válido poderá acessar essa rota.
   --- 
  /api/users/user_all:
    get:
      summary: Get all users Function
      security:
        - APIKeyHeader: []
      tags:
        - User
      
      responses:
        '200':
          description: Returns all users
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

  users = UserModel.get_all_users()
  ser_users = user_schema.dump(users, many=True).data
  return custom_response(ser_users, 200)






@user_api.route('/<int:user_id>', methods=['GET'])
@Auth.auth_required
def get_a_user(user_id):
  """
  Get a single user
  ---
  /api/users/{user_id}:
    get:
      summary: Gets a user by ID.
      security:
        - APIKeyHeader: []
      tags:
        - User
      parameters:
        - in: path
          name: user_id
          required: true
          schema:
            type: integer
            minimum: 1
            description: The user ID.

      responses:
        '200':
          description: Data this user successfully
        '400':
          description: user not found
        '401':
          description: Permission denied
  """
  user = UserModel.get_one_user(user_id)
  if not user:
    return custom_response({'error': 'user not found'}, 400)
  data = user_schema.dump(user).data

  if g.user.get('id') != data.get('owner_id'):
    return custom_response({'error': 'permission denied'}, 401)
  
  return custom_response(data, 200)







@user_api.route('/edit/me', methods=['PUT'])
@Auth.auth_required
def update():
  """
  Update me
  ---
  /api/users/edit/{me}:
    put:
      summary: Update A User.
      security:
        - APIKeyHeader: []
      tags:
        - User
      parameters:
        - in: path
          name: me
          required: true
          schema:
            type: string
            description: The user ID.
      requestBody:
        description: User Functions
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - email
                - password
                - role
              properties:
                name:
                  type: string
                email:
                  type: string
                password:
                  type: string
                role:
                  type: string
      responses:
        '200':
          description: User successfully update
        '400':
          description: Missing data
      
  """
  req_data = request.get_json()
  data, error = user_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)

  user = UserModel.get_one_user(g.user.get('id'))
  user.update(data)
  ser_user = user_schema.dump(user).data
  return custom_response(ser_user, 200)






@user_api.route('/delete/me', methods=['DELETE'])
@Auth.auth_required
def delete():
  """
  Delete a user
  ---
  /api/users/delete/me:
    delete:
      summary: Return your user data.
      security:
        - APIKeyHeader: []
      tags:
        - User
      responses:
        '200':
          description: An Access Token API to be used in Boleto Viewer
  """
  user = UserModel.get_one_user(g.user.get('id'))
  user['deleted']= True
  user.update(data)
  #user.delete()
  return custom_response({'message': 'deleted'}, 200)








@user_api.route('/me', methods=['GET'])
@Auth.auth_required
def get_me():
  """
  Get me
  ---
  /api/users/me:
    get:
      summary: Return your user data.
      security:
        - APIKeyHeader: []
      tags:
        - User
      responses:
        '200':
          description: An Access Token API to be used in Boleto Viewer
        '400':
          description: user in post not found
  """
  user = UserModel.get_one_user(g.user.get('id'))
  ser_user = user_schema.dump(user).data
  return custom_response(ser_user, 200)








@user_api.route('/login', methods=['POST'])
def login():
  """
  User Login Function

  endpoint de login- Precisamos configurar isso aqui para que um usuário possa obter um token

  /api/users/login:
    post:
      summary: 'User Login Function In API, return a token API.'
      tags:
        - User
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
      responses:
        '200':
          description: An Access Token API to be used in Boleto Viewer
        '400':
          description: you need email and password to sign in
        '401':
          description: you need email and password to sign in
        '402':
          description: Credentials are not valid
        '403':
          description: Credentials are not valid
  """
  req_data = request.get_json() # para obter os dados do corpo da solicitação

  data, error = user_schema.load(req_data, partial=True) #desserializar e validar o conteúdo dos dados
  if error:
    return custom_response(error, 400)

  if not data.get('email') or not data.get('password'):
    return custom_response({'error': 'you need email and password to sign in'}, 401)
  # filtrar a tabela do usuário usando o endereço de e-mail do usuário e retornar uma mensagem 
  # de erro se o usuário não existir.
  user = UserModel.get_user_by_email(data.get('email'))
  if not user:
    return custom_response({'error': 'invalid credentials'}, 402)

  #Se o usuário existir no banco de dados, adicionamos uma condição para validar a senha fornecida 
  # com a senha de hash salva do usuário user.check_hash(data.get('password'))
  if not user.check_hash(data.get('password')):
    return custom_response({'error': 'invalid credentials'}, 403)

  ser_data = user_schema.dump(user).data
  token = Auth.generate_token(ser_data.get('id'))
  return custom_response({'jwt_token': token}, 200)

  



def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )
