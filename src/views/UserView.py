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

@user_api.route('/', methods=['POST'])
def create():
  """
  Retornará o token JWT se a solicitação foi bem-sucedida

  Create User Function
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
  return custom_response({'jwt_token': token}, 201)


@user_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
  """
  Get all users

   endpoint que obterá todos os dados do usuário no banco de dados e 
   somente um usuário com um token válido poderá acessar essa rota.
  """
  users = UserModel.get_all_users()
  ser_users = user_schema.dump(users, many=True).data
  return custom_response(ser_users, 200)


@user_api.route('/<int:user_id>', methods=['GET'])
@Auth.auth_required
def get_a_user(user_id):
  """
  Get a single user
  """
  user = UserModel.get_one_user(user_id)
  if not user:
    return custom_response({'error': 'user not found'}, 404)
  
  ser_user = user_schema.dump(user).data
  return custom_response(ser_user, 200)


@user_api.route('/me', methods=['PUT'])
@Auth.auth_required
def update():
  """
  Update me
  """
  req_data = request.get_json()
  data, error = user_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)

  user = UserModel.get_one_user(g.user.get('id'))
  user.update(data)
  ser_user = user_schema.dump(user).data
  return custom_response(ser_user, 200)


@user_api.route('/me', methods=['DELETE'])
@Auth.auth_required
def delete():
  """
  Delete a user
  """
  user = UserModel.get_one_user(g.user.get('id'))
  user.delete()
  return custom_response({'message': 'deleted'}, 204)


@user_api.route('/me', methods=['GET'])
@Auth.auth_required
def get_me():
  """
  Get me
  """
  user = UserModel.get_one_user(g.user.get('id'))
  ser_user = user_schema.dump(user).data
  return custom_response(ser_user, 200)


@user_api.route('/login', methods=['POST'])
def login():
  """
  User Login Function

  endpoint de login- Precisamos configurar isso aqui para que um usuário possa obter um token
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
