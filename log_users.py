from api_communication import ApiCommunication
from pytz import timezone
import datetime
from datetime import datetime
import json
import time


# Classe responsável pela interação com o arquivo de log de usuários "log_users.txt"
class LogUsers:

    def __init__(self):
        # caminho que será gravado o arquivo de log do usuário
        # o caminho deve ser auterado para o mesmo do projeto
        self.PATH = "/home/pi/catraca_ifce_maracanau/"
        self.api = ApiCommunication()
        self.users_list = []

    # grava a lista de usuários que ainda não foram postados em um arquivo log_users
    # objetivo é garantir o log de usuários quando a comunicação com a api estiver com problemas
    def record_log_users_file(self):
        if len(self.users_list) > 0:
            log_file = open(self.PATH + "log_users.txt", 'a+')
            log_file.write(
                str(self.users_list).replace("[", "").replace("]", "").replace("}", "}\n").replace(", {", "{").replace(
                    "'", "\""))
            log_file.close()

    # posta na api o log de usuários do arquivo log_users
    # se requisição não funciona, mantem os dados do usuário no arquivo
    def post_log_users_file(self):
        read_log_users = open(self.PATH + "log_users.txt", 'r')
        lines = read_log_users.readlines()
        new_lines = lines.copy()
        for line in lines:
            json_user = json.loads(line)
            is_post_api_ok = self.api.post_user(json_user['numeroCatraca'], json_user['tipoMovimentacao'],
                                                json_user['cartao'],
                                                json_user['data_hora'])
            if is_post_api_ok:
                new_lines.remove(line)
        read_log_users.close()
        write_log_users = open(self.PATH + "log_users.txt", 'w')
        write_log_users.writelines(new_lines)
        write_log_users.close()

    # is_entrance -> true para entrada e false para saida
    # card_tag -> numero do cartao rfid
    # turnstile_number -> numero da catraca
    # responsável por enviar os dados da passagem do usuário para a api
    # caso api não funcione, grava os dados como json em users_list
    def post_or_record_user(self, card_tag, is_entrance, turnstile_number):
        current_date_time = datetime.now()
        sao_paulo_timezone = timezone("America/Sao_Paulo")
        sao_paulo_date_time = current_date_time.astimezone(sao_paulo_timezone)
        text_sao_paulo_date_time = sao_paulo_date_time.strftime("%d/%m/%Y %H:%M:%S")

        if is_entrance:
            movement_type = 1
        else:
            movement_type = 2
        is_post_api_ok = self.api.post_user(str(turnstile_number), str(movement_type), str(card_tag),
                                            str(text_sao_paulo_date_time))

        if not is_post_api_ok:
            user = {"numeroCatraca": str(turnstile_number), "tipoMovimentacao": str(movement_type),
                    "cartao": str(card_tag), "data_hora": str(text_sao_paulo_date_time)}
            json_user = json.loads(json.dumps(user))
            self.users_list.append(json_user)
