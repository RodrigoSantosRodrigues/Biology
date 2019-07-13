# -*- coding: utf-8 -*-
# src/models/BoletoModel.py
"""
    ...Web Flask com autorização JWT (Jason web token authorization)
    ------------------------------------------------------------------------
                        Modelo de boleto
    ------------------------------------------------------------------------
    
    URLs: https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb
          https://medium.com/@dushan14/create-a-web-application-with-python-flask-postgresql-and-deploy-on-heroku-243d548335cc
          https://github.com/oleg-agapov/flask-jwt-auth
          https://www.codementor.io/olawalealadeusi896/restful-api-with-python-flask-framework-and-postgres-db-part-1-kbrwbygx5

    Modelos que determinam as estruturas lógicas do banco de dados. Simplificando, determina como as tabelas
    ficariam no banco de dados. Os modelos definem como os registros podem ser manipulados ou recuperados no 
    banco de dados.


    ------------------PARÂMETROS  PARA GERAR BOLETO ------------------
  
     Todos os parâmetros devem ser passados como ``**kwargs`` para o construtor
    ou então devem ser passados depois, porém antes de imprimir o boleto.

   

    eg::
 
        bData = BoletoData(logo_image : type base64)
        bData.cedente = 'João Ninguém'
        bData.cedente_cidade = 'Rio de Janeiro'
        bData.cedente_uf = 'RJ'
        # Assim por diante até preencher todos os campos obrigatórios.

    **Parâmetros obrigatórios para gerar o Boleto**:
    :param codigo_banco: 
    :param carteira: Depende do Banco.
    :param nosso_numero: 
    :param convenio:
    :param agencia_cedente: Tamanho pode variar com o banco.
    :param conta_cedente: Conta do Cedente sem o dígito verificador.
    :param valor_documento:
    :param data_documento: type `datetime.date`
    :param data_vencimento: type `datetime.date`
    

    **Parâmetros obrigatórios por indicação da FEBRABAN NO BRASIL, incluindo informações de quem paga e quem recebe**:
    :param aceite: 'N' para o caixa não aceitar o boleto após a validade ou 'A' para aceitar. *(default: 'N')*
    :param cedente: Nome do Cedente
    :param cedente_cidade:
    :param cedente_uf:
    :param cedente_logradouro: Endereço do Cedente
    :param cedente_bairro:
    :param cedente_cep:
    :param cedente_documento: CPF ou CNPJ do Cedente.
    :param data_processamento:
    :type data_processamento: `datetime.date`
    :param numero_documento: Número Customizado para controle. Pode ter até 13caracteres dependendo do banco.
    :param ios: santander usa esse campo- IOS - somente para Seguradoras (Se 7% informar 7, limitado 9%)/ Demais clientes usar 0 (zero)
    :param sacado_nome: Nome do Sacado
    :param sacado_documento: CPF ou CNPJ do Sacado
    :param sacado_cidade:
    :param sacado_uf:
    :param sacado_endereco: Endereco do Sacado
    :param sacado_bairro:
    :param sacado_cep:
    

    **Parâmetros não obrigatórios**:
    :param instrucoes:
    :param demonstrativo:
    :param quantidade:
    :param especie: Nunca precisa mudar essa opção *(default: 'R$')*
    :param especie_documento:
    :param local_pagamento: *(default: 'Pagável em qualquer banco até o vencimento')*
    :param moeda: Nunca precisa mudar essa opção *(default: '9')*

    Observações:
a) conforme Lei Federal 12.039, de 01/10/2009, nos documentos de
cobrança de dívida encaminhados ao consumidor, devem constar o nome,
o endereço e o número de inscrição no Cadastro de Pessoas Físicas –
CPF ou no Cadastro Nacional de Pessoa Jurídica – CNPJ do fornecedor
do produto ou serviço.
b) é recomendável que também no recibo do sacado conste a linha digitável
e o código de barras, de forma a facilitar eventual consulta pelo sacado. 


"""
from . import db
import datetime
from marshmallow import fields, Schema
import base64
from datetime import date

#IMPORT DO python_boleto
import sys
sys.path.append('...python_boleto') 
from python_boleto.pdf import BoletoPDF
from python_boleto.html import BoletoHTML
from python_boleto import bank

class BoletoModel(db.Model):
  """
  Boleto Model
  """

  __tablename__ = 'boletos'

  id = db.Column(db.Integer, primary_key=True)
  aceite = db.Column(db.String(128), nullable=True)
  codigo_banco = db.Column(db.String(128), nullable=False)
  data_documento = db.Column(db.Date(), nullable=False)
  data_vencimento = db.Column(db.Date(), nullable=False)
  data_processamento = db.Column(db.Date(), nullable=True)
  demonstrativo = db.Column(db.String(128), nullable= True)
  numero_documento = db.Column(db.String(128), nullable=True)
  sacado_nome = db.Column(db.String(128), nullable=True)
  sacado_documento = db.Column(db.String(128), nullable=True)
  sacado_cidade = db.Column(db.String(128), nullable=True)
  sacado_uf = db.Column(db.String(128), nullable=True)
  sacado_endereco = db.Column(db.String(128), nullable=True)
  sacado_bairro = db.Column(db.String(128), nullable=True)
  sacado_cep = db.Column(db.String(128), nullable=True)
  quantidade = db.Column(db.String(50), nullable=True)
  especie = db.Column(db.String(50), nullable=True)
  ios = db.Column(db.String(50), nullable=True)
  instrucoes = db.Column(db.String(200), nullable=True)
  especie_documento = db.Column(db.String(128), nullable=True)
  local_pagamento = db.Column(db.String(200), nullable=True)
  linha_digitavel = db.Column(db.String(200), nullable=False, unique=True)
  moeda = db.Column(db.String(30), nullable=True)
  valor_documento = db.Column(db.String(200), nullable=False)
  visualized = db.Column(db.Boolean, default=False, nullable= True)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)



  # class constructor - definir os atributos de classe
  def __init__(self, data):
    self.aceite = data.get('aceite')
    self.codigo_banco = data.get('codigo_banco')
    self.data_documento = data.get('data_documento')
    self.data_vencimento = data.get('data_vencimento')
    self.data_processamento = data.get('data_processamento')
    self.demonstrativo = data.get('demonstrativo')
    self.numero_documento = data.get('numero_documento')
    self.sacado_nome = data.get('sacado_nome')
    self.sacado_documento = data.get('sacado_documento')
    self.sacado_cidade = data.get('sacado_cidade')
    self.sacado_uf = data.get('sacado_uf')
    self.sacado_endereco = data.get('sacado_endereco')
    self.sacado_bairro = data.get('sacado_bairro')
    self.sacado_cep = data.get('sacado_cep')
    self.quantidade = data.get('quantidade')
    self.ios = data.get('ios')
    self.instrucoes = data.get('instrucoes')
    self.especie= data.get('especie')
    self.especie_documento = data.get('especie_documento')
    self.local_pagamento = data.get('local_pagamento')
    self.linha_digitavel = data.get('linha_digitavel')
    self.moeda = data.get('moeda')
    self.valor_documento = data.get('valor_documento')
    self.visualized = data.get('visualized')
    self.owner_id= data.get('owner_id')
    self.cliente_id= data.get('cliente_id')
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()


  #salvar boleto para o nosso banco de dados
  def save(self):
    db.session.add(self)
    db.session.commit()


  #atualizar o registro do nosso boleto no db
  def update(self, data):
    '''
      Atualizar um Boleto: Somente o usuário proprietário pode atualizar seu boleto
    '''
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()


 
  def delete(self):  #deletar o registro do nosso boleto no db
    '''
      Deletar um Boleto: Somente o usuário proprietário pode deletar seu boleto
    '''
    db.session.delete(self)
    db.session.commit()
  
 

  @staticmethod
  def get_all(): #obter todos os boletos do banco de dados
    '''
      Buscar todos os Boletos: Somente um administrador pode acessar esse filtro
    '''
    return BoletoModel.query.all()


  
  @staticmethod
  def get_all_boletos(owner_id): 
    '''
      Filtrar todos os Boletos por usuário
    '''
    return BoletoModel.query.filter_by(owner_id=owner_id).all()


  @staticmethod
  def get_boleto_by_linha_digitavel(line):
    '''
      Filtrar todos os Boletos por linha digitável
    '''
    return BoletoModel.query.filter_by(linha_digitavel=line).first()


  @staticmethod
  def get_one_boleto(id): #obter um único boleto do db usando campo primary_key
    '''
      Filtrar todos os Boletos por usuário: um boleto so pode ser acessado pelo seu proprietário
    '''
    return BoletoModel.query.get(id)
  

  @staticmethod
  def format_date_create(req_data):
    '''
      Formatar datas para salvar os registro no banco de dados
        Obs: data_vencimento já vem na request.
    '''
    req_data['data_processamento']= date.today()
    req_data['data_documento']= date.today()
    req_data['data_processamento'] = '{}/{}/{}'.format(req_data['data_processamento'].year, req_data['data_processamento'].month, req_data['data_processamento'].day)
    req_data['data_documento'] = '{}/{}/{}'.format(req_data['data_documento'].year, req_data['data_documento'].month, req_data['data_documento'].day)
    return req_data


  @staticmethod
  def format_date_boleto(data):
    '''
      Formatar datas para gerar o Boleto
    '''
    data['data_processamento']= date.today()
    data['data_documento']= date.today()
    data['data_processamento'] = '{}/{}/{}'.format(data['data_processamento'].year, data['data_processamento'].month, data['data_processamento'].day)
    data['data_documento'] = '{}/{}/{}'.format(data['data_documento'].year, data['data_documento'].month, data['data_documento'].day)

    data['data_vencimento']= datetime.datetime.strptime(data['data_vencimento'], "%Y/%m/%d").date()
    data['data_documento']= datetime.datetime.strptime(data['data_documento'], "%Y/%m/%d").date()
    data['data_processamento']= datetime.datetime.strptime(data['data_processamento'], "%Y/%m/%d").date()
    return data

  @staticmethod
  def format_date_view(data):
    '''
      Formatar datas para gerar o boleto.
        Obs: os campos de data vem do banco de dados
    '''
    data['data_vencimento']= datetime.datetime.strptime(data['data_vencimento'], "%Y-%m-%d").date()
    data['data_documento']= datetime.datetime.strptime(data['data_documento'], "%Y-%m-%d").date()
    data['data_processamento']= datetime.datetime.strptime(data['data_processamento'], "%Y-%m-%d").date()
    return data


  @staticmethod
  def generate_boleto(data_boleto, data_cliente, data_conta):
    '''
      FUNÇÃO para gerar o boleto.
      Nescessita dos dados recuperados em uma requeste e os dados já pré-cadastrados (Dados do cliente e as contas).
    
    '''
    codigo_banco= data_boleto['codigo_banco'] 
    data_cliente['logo_image']= data_cliente['logoboleto']
    #Instancia da classe do banco desejado
    ClasseBanco = bank.get_class_for_codigo(codigo_banco)
    d= ClasseBanco(data_cliente['logo_image'])
    #Se banco do Brasil, é nescessário passar como arg convenio e o nosso_numero para verificar o formato de ambos
    #Args:
    #    format_convenio: Formato do convenio 6, 7 ou 8
    #    format_nnumero: Formato nosso numero 1 ou 2
    if codigo_banco == '001':
      d= ClasseBanco(data_conta['convenio'], data_conta['nosso_numero'], data_cliente['logo_image'])
  
    d.codigo_banco= codigo_banco
    d.carteira = data_conta['carteira']
    d.nosso_numero = data_conta['nosso_numero']
    if data_boleto.get('numero_documento') is not None:
      d.numero_documento = data_boleto.get('numero_documento')
    d.convenio = data_conta['convenio']
    d.agencia_cedente = data_conta['agencia']
    d.conta_cedente = data_conta['conta']
    d.valor_documento = data_boleto['valor_documento']
    d.data_vencimento = data_boleto['data_vencimento']
    d.data_documento = data_boleto['data_documento']

    if data_boleto.get('aceite') is not None:
      d.aceite= data_boleto.get('aceite')
    #Dados do cedente está sem o prefixo ou sufixo 'cedente' no banco de dados
    d.cedente = data_cliente['name'] #cedente está como 'name' no banco de dados
    d.cedente_documento = data_cliente['documento']
    d.cedente_cidade= data_cliente['cidade']
    d.cedente_uf= data_cliente['uf']
    d.cedente_logradouro= data_cliente['logradouro']
    d.cedente_bairro= data_cliente['bairro']
    d.cedente_cep= data_cliente['cep']                 
    d.data_processamento = data_boleto['data_processamento']
    
    if data_boleto.get('sacado_bairro') is not None:
      d.sacado_bairro= data_boleto.get('sacado_bairro')
    if data_boleto.get('sacado_cep') is not None:
      d.sacado_cep= data_boleto.get('sacado_cep')
    if data_boleto.get('sacado_cidade') is not None:
      d.sacado_cidade= data_boleto.get('sacado_cidade')
    if data_boleto.get('sacado_documento') is not None:
      d.sacado_documento= data_boleto.get('sacado_documento')
    if data_boleto.get('sacado_endereco') is not None:
      d.sacado_endereco= data_boleto.get('sacado_endereco')
    if data_boleto.get('sacado_nome') is not None:
      d.sacado_nome= data_boleto.get('sacado_nome')
    if data_boleto.get('sacado_uf') is not None:
      d.sacado_uf= data_boleto.get('sacado_uf')
    
    if data_boleto.get('ios') is not None:
      d.ios= data_boleto['ios']
    if data_boleto.get('instrucoes') is not None:
      d.instrucoes= data_boleto['instrucoes'] 
    if data_boleto.get('demonstrativo') is not None:
      d.demonstrativo= data_boleto['demonstrativo']
    if data_boleto.get('quantidade') is not None:
      d.quantidade= data_boleto['quantidade']
    if data_boleto.get('especie') is not None:
      d.especie= data_boleto['especie']
    if data_boleto.get('especie_documento') is not None:
      d.especie_documento= data_boleto['especie_documento']
    if data_boleto.get('local_pagamento') is not None:
      d.local_pagamento= data_boleto['local_pagamento']
    if data_boleto.get('moeda') is not None:
      d.moeda= data_boleto['moeda']
    
    boleto_HTML = BoletoHTML('boleto.html') 
    boleto_HTML.drawBoleto(d)
    boleto_HTML.save() #salvar arquivo na pasta raiz com nome boleto.html
    html= boleto_HTML.html_()

    if data_boleto['format_boleto'] == 'html':
      if data_boleto['base_64'] == 'true':
        print("model base64")
        return base64.b64encode(html.encode('ascii','xmlcharrefreplace')).decode()
      print("nao base64")
      return html



 
  def __repr__(self):
    return '<id {}>'.format(self.id)



class BoletoSchema(Schema):
  """
  Boleto Schema
  """
  id = fields.Int(dump_only=True)
  aceite = fields.Str(required=False)
  codigo_banco = fields.Str(required=False)
  data_vencimento = fields.Date(required=True)
  data_documento= fields.Date(required=False)
  data_processamento= fields.Date(required=False)
  demonstrativo = fields.Str(required=False)
  numero_documento = fields.Str(required=False)
  sacado_nome = fields.Str(required=False)
  sacado_documento = fields.Str(required=False)
  sacado_cidade = fields.Str(required=False)
  sacado_uf = fields.Str(required=False)
  sacado_endereco = fields.Str(required=False)
  sacado_bairro = fields.Str(required=False)
  sacado_cep = fields.Str(required=False)
  quantidade = fields.Str(required=False)
  especie = fields.Str(required=False)
  ios = fields.Str(required=False)
  instrucoes = fields.Str(required=False)
  especie_documento = fields.Str(required=False)
  local_pagamento = fields.Str(required=False)
  linha_digitavel = fields.Str(required=True)
  moeda = fields.Str(required=False)
  valor_documento = fields.Str(required=True)
  view_boleto = fields.Str(required= True)
  format_boleto = fields.Str(required= True)
  base_64= fields.Str(required= True)
  owner_id = fields.Int(required=False)
  visualized = fields.Boolean(required=False)
  cliente_id = fields.Int(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
