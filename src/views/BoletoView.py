# -*- coding: utf-8 -*-
# encoding: utf-8
#/src/views/BoletoView.py

"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        API do Boleto
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

  
"""

from flask import request, g, Blueprint, json, Response, jsonify
from ..shared.Authentication import Auth
from ..models.BoletoModel import BoletoModel, BoletoSchema
from ..models.UserModel import UserModel, UserSchema
from ..models.EntityModel import EntityModel, EntitySchema
from ..models.ClienteModel import ClienteModel, ClienteSchema
from ..models.ContaModel import ContaModel, ContaSchema



boleto_api = Blueprint('boleto_api', __name__)
boleto_schema = BoletoSchema()

user_schema = UserSchema()
entity_schema = EntitySchema()
cliente_schema = ClienteSchema()
conta_schema = ContaSchema()




@boleto_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Boleto Function
  """
  ##para obter o objeto JSON do corpo da solicitação
  #validar e desserializar dados json de entrada do usuário
  req_data = request.get_json()
  
  data, error = boleto_schema.load(req_data) #verificar se todos os dados estão requeridos
  if error:
    return custom_response(error, 400)
  
  req_data['owner_id'] = g.user.get('id')
  req_data['codigo_banco']= req_data.get('linha_digitavel')[0:3] #recebe os 3 primeiros digitos que se refere ao codigo do banco

  # check if linha_digitavel already exist in the db
  boleto_in_db = BoletoModel.get_boleto_by_linha_digitavel(req_data.get('linha_digitavel'))
  if boleto_in_db:
    message = {'error': 'Digitable line already exists in db'}
    return custom_response(message, 400)

  #consultar dados de clientes (Ação)
  post_cliente = ClienteModel.get_one_cliente(req_data.get('cliente_id'))#codigo_carteira == id do cliente
  if not post_cliente:
    return custom_response({'error': 'post not found'}, 404)
  data_cliente = cliente_schema.dump(post_cliente).data

  #consultar dados a conta (Ação) pelço codigo do cliente e o codigo do banco
  post_conta = ContaModel.get_conta_by_codigocliente_and_codigobanco(data_cliente.get('id'), req_data.get('codigo_banco'))
  if not post_conta:
    return custom_response({'error': 'post not found'}, 404)
  data_conta = conta_schema.dump(post_conta).data
  
  req_data['cliente_id']= data_cliente.get('id')
  data, error = boleto_schema.load(req_data) #verificar se todos os dados estão requeridos antes de salvar
  if error:
    return custom_response(error, 400)

  req_data= BoletoModel.format_date_boleto(req_data) #formatar data no formato para gerar o Boleto
  boleto_html= BoletoModel.generate_boleto(req_data, data_cliente, data_conta) #GERA o Boleto

  #Se o usuário solicitar visualizar o Boleto, é retornado em HTML ou base 64
  if req_data.get('view_boleto') == 'true': 
    data['visualized']= True
    data= BoletoModel.format_date_create(data)
    post = BoletoModel(data)
    post.save() #Salva os dados do Boleto antes de retornar para o usuário
    if req_data.get('format_boleto') == 'html':
      if req_data.get('base_64') == 'true':
        return custom_response({'base_64': boleto_html}, 200)
      return custom_response_html(boleto_html, 200)
    return custom_response({'Sucess': 'PDF format not implemented, sorry!'}, 200)
  
  #Salva o Boleto e retorna somente o id
  data= BoletoModel.format_date_create(data) #formatar a datas para salvar no banco
  post = BoletoModel(data)
  post.save()
  data = boleto_schema.dump(post).data
  
  return custom_response({'id': data['id']}, 201)
  





@boleto_api.route('view/<int:boleto_id>', methods=['GET'])
@Auth.auth_required
def view_boleto(boleto_id):
  """
  View Boleto : Visualizar o Boleto pelo id
  """
  req_data= request.get_json()

  #consultar dados de boletos
  post_boleto = BoletoModel.get_one_boleto(boleto_id)
  if not post_boleto:
    return custom_response({'error': 'post not found'}, 404)
  data_boleto = boleto_schema.dump(post_boleto).data

  #somente o usuário proprietário pode visualizar o seu boleto, caso não seja retorna um erro
  if data_boleto.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)

  #consultar dados de clientes (Ação)
  post_cliente = ClienteModel.get_one_cliente(data_boleto['cliente_id'])#codigo_carteira == id do cliente
  if not post_cliente:
    return custom_response({'error': 'post not found'}, 404)
  data_cliente = cliente_schema.dump(post_cliente).data

  #consultar dados a conta (Ação) pelço codigo do cliente e o codigo do banco
  post_conta = ContaModel.get_conta_by_codigocliente_and_codigobanco(data_cliente['id'], data_boleto['codigo_banco'])
  if not post_conta:
    return custom_response({'error': 'post not found'}, 404)
  data_conta = conta_schema.dump(post_conta).data

  data_boleto['format_boleto']= req_data['format_boleto']
  data_boleto['base_64']= req_data['base_64']

  #verificar se o boleto já foi visualizado, se não: altera para visualizado
  if data_boleto.get('visualized') != True:
    data_boleto['visualized']= True #Add True em campo visualized
    print(data_boleto)
    post_boleto.update(data_boleto) #Atualiza os dados do Boleto
    
  data_boleto= BoletoModel.format_date_view(data_boleto) #formata a data para visualizar o boleto

  boleto_html= BoletoModel.generate_boleto(data_boleto, data_cliente, data_conta)#GERA o boleto

  if req_data['format_boleto'] == 'html':
    if req_data['base_64'] == True:
      return custom_response({'base_64': boleto_html}, 200)
    
    return custom_response_html(boleto_html, 200)
  
  return custom_response({'Sucess': 'PDF format not implemented, sorry!'}, 200)






@boleto_api.route('/', methods=['GET'])
@Auth.auth_required
def get_all():
  """
  Get All Boletos
  """
  #consultar dados de user
  post_user = UserModel.get_one_user(g.user.get('id'))#codigo_carteira == id do cliente
  if not post_user:
    return custom_response({'error': 'user not found'}, 404)
  data_user = user_schema.dump(post_user).data

  #se o usuário logado for diferente de de administrador, é negado a permissão. manage ou admin
  if data_user.get('role') != 'manage':
    return custom_response({'error': 'permission denied'}, 400)

  posts = BoletoModel.get_all()
  data = boleto_schema.dump(posts, many=True).data
  return custom_response(data, 200)




@boleto_api.route('/<int:boleto_id>', methods=['GET'])
@Auth.auth_required
def get_one(boleto_id):
  """
  Get A Boleto
  Busca um boleto pelo campo id
  """
  post = BoletoModel.get_one_boleto(boleto_id)
  
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = boleto_schema.dump(post).data

  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)

  return custom_response(data, 200)





@boleto_api.route('/<int:boleto_id>', methods=['PUT'])
@Auth.auth_required
def update(boleto_id):
  """
  Update A Boleto
  """
  req_data = request.get_json()
  post = BoletoModel.get_one_boleto(boleto_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = boleto_schema.dump(post).data
  #somente o usuário proprietário pode alterar um registro, caso não seja retorna um erro
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)
  
  if data.get('visualized') == True:
    return custom_response({'error': 'permission denied, boleto has already been viewed'}, 400)
  
  data, error = boleto_schema.load(req_data, partial=True)
  if error:
    return custom_response(error, 400)
  post.update(data)
  
  data = boleto_schema.dump(post).data
  return custom_response(data, 200)





@boleto_api.route('/<int:boleto_id>', methods=['DELETE'])
@Auth.auth_required
def delete(boleto_id):
  """
  Delete A Boleto
  """
  post = BoletoModel.get_one_boleto(boleto_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = boleto_schema.dump(post).data
  #só o usuário proprietário pode deletar os dados
  if data.get('owner_id') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)
  
  if data.get('visualized') == True:
    return custom_response({'error': 'permission denied, boleto has already been viewed'}, 400)

  post.delete()
  return custom_response({'message': 'deleted'}, 204)






def custom_response_html(res, status_code):
  """
  Custom Response Function in HTML
  """
  return Response(
    mimetype="text/html",
    response=res,
    status=status_code
  )

def custom_response(res, status_code):
  """
  Custom Response Function in Jason
  """
  return Response(
    mimetype="application/jason",
    response=json.dumps(res),
    status=status_code
  )

