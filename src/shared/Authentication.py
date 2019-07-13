# -*- coding: utf-8 -*-
#src/shared/Authentication
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        API do usuário
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

   
"""

import jwt
import os
import datetime
from flask import json, Response, request, g
from functools import wraps
from ..models.UserModel import UserModel


class Auth():
  """
  Auth Class
  """

  @staticmethod
  def generate_token(user_id):
    """
    Generate Token Method
    """
    try:
      payload = {
        #exp -> data do token como 1 dia após sua criação
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=int(60)),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
      }
      return jwt.encode(
        payload,
        os.getenv('JWT_SECRET_KEY'),
        'HS256'
      ).decode("utf-8")
    except Exception as e:
      return Response(
        mimetype="application/json",
        response=json.dumps({'error': 'error in generating user token'}),
        status=400
      )

  @staticmethod
  def decode_token(token):
    """
    Decode token method

    método estático para decodificar o token do usuário fornecido 
    usando o mesmo JWT_SECRET_KEY que usamos ao assinar o token

    verifica e valida o token
    """
    re = {'data': {}, 'error': {}}
    try:
      payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'))
      re['data'] = {'user_id': payload['sub']}
      return re
    except jwt.ExpiredSignatureError as e1:
      re['error'] = {'message': 'token expired, please login again'}
      return re
    except jwt.InvalidTokenError:
      re['error'] = {'message': 'Invalid token, please try again with a new token'}
      return re

  # decorator
  @staticmethod
  def auth_required(func):
    """
    Auth decorator

    apenas o usuário registrado possa obter todos os usuários, o que significa que um 
    usuário sem um token de autenticação não pode acessar essa rota.

    configuramos uma condição que verifica se api-tokenexiste no cabeçalho da solicitação, 
    um usuário precisará anexar o token obtido da criação de uma conta ou o obtido a partir do login. 
    Se o token existir no cabeçalho da solicitação, passamos o token para decode_token método para validar 
    a autenticidade do token, se o token é válido,
    """
    @wraps(func)
    def decorated_auth(*args, **kwargs):
      if 'api-token' not in request.headers:
        return Response(
          mimetype="application/json",
          response=json.dumps({'error': 'Authentication token is not available, please request to get one'}),
          status=400
        )
      token = request.headers.get('api-token')
      data = Auth.decode_token(token)
      if data['error']:
        return Response(
          mimetype="application/json",
          response=json.dumps(data['error']),
          status=401
        )
        
      user_id = data['data']['user_id']
      check_user = UserModel.get_one_user(user_id)
      if not check_user:
        return Response(
          mimetype="application/json",
          response=json.dumps({'error': 'user does not exist, invalid token'}),
          status=402
        )
      g.user = {'id': user_id}
      return func(*args, **kwargs)
    return decorated_auth
