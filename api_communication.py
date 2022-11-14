import json
import requests
from decouple import config

# Classe resposavel pela comunicação da API
class ApiCommunication:
    def __init__(self):
        self.user = config('API_USER')
        self.key = config('API_KEY')
        self.url = config('API_URL')

    # autentica o cartão do usuário enviando o id do cartão para a api
    def authenticate_card(self, card_tag):
        url = self.url + "tag"
        querystring = {"cartao": str(card_tag),
                       "usuario": str(self.user),
                       "senha": str(self.key)}
        try:
            json_response = json.loads(json.dumps(requests.request("GET", url, params=querystring, timeout=1).json()))
            if str(json_response["autorizacao"]) == "1":
                return True
            elif str(json_response["autorizacao"]) == "0":
                return False
            else:
                return "Error authenticateCard"
        except Exception as e:
            print(e)
            return "Error Exception Authenticate"

    # posta os dados do usuario, quando o mesmo passa pela catraca
    # envia o numero da catraca, o tipo de movimentação (entrada/1 ou saida/2), a tag do cartão e a hora que ocorreu
    def post_user(self, turnstile_number, movement_type, card_tag, date_time):
        url = self.url + "inserirTransito"
        querystring = {"numeroCatraca": str(turnstile_number),
                       "tipoMovimentacao": str(movement_type),
                       "cartao": str(card_tag),
                       "data_hora": str(date_time),
                       "usuario": self.user,
                       "senha": self.key}
        try:
            json_response = json.loads(json.dumps(requests.request("POST", url, params=querystring, timeout=1).json()))
            if str(json_response["status"]) == "OK":
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    # retorna os dados de todos os usuários cadastrados
    def get_users(self):
        url = self.url + "backup"
        querystring = {"usuario": self.user,
                       "senha": self.key}
        try:
            json_response = json.loads(json.dumps(requests.request("GET", url, params=querystring).json()))
            return json_response
        except Exception as e:
            print(e)
            return "Error Exception"
