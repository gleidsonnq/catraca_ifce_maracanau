from api_communication import ApiCommunication
import json


# Classe responsável pelo backup dos usuários
class Backup:

    def __init__(self):
        self.api = ApiCommunication()
        self.PATH = "/home/pi/catraca_ifce_maracanau/"

    # consulta a api para obter a lista de usuários
    # grava o o arquivo de backup dos usuários"backup_users.txt"
    # o arquivo apenas contem as tags dos cartões
    def make_users_backup(self):
        users = self.api.get_users()
        if users != "Error Exception":
            backup_file = open(self.PATH + "backup_users.txt", 'w')
            line = ""
            for i in range(len(users)):
                json_users = json.loads(json.dumps(users[i]))
                line += (str(json_users["clearcode"]) + "\n")  # pega o numero do cartao
            backup_file.write(line)
            backup_file.close()
            return True
        else:
            return False


backup = Backup()
backup.make_users_backup()


