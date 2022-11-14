from api_communication import ApiCommunication
import RPi.GPIO as gpio
import time
from log_users import LogUsers
import sys
import datetime
from datetime import datetime
import os
from decouple import config


class Turnstile:

    def __init__(self):
        # mata o processo da catraca se estiver aberto ainda
        os.system("kill -9 $(ps aux | grep -m 1 catraca | grep -w Tl | tr -s ' '| cut -d' ' -f2)")
        time.sleep(1)

        # definem as pinagens do RPI como constantes
        self.LED_GREEN_RELAY_EXIT = 21  # pino 40
        self.LED_GREEN_RELAY_ENTRANCE = 20  # pino 38
        self.LED_RGB_BLUE_ENTRANCE = 22  # pino 15
        self.LED_RGB_BLUE_EXIT = 27  # pino 13
        self.LED_RGB_RED_ENTRANCE = 6  # pino 31
        self.LED_RGB_RED_EXIT = 5  # pino 29
        self.LED_RGB_GREEN_ENTRANCE = 19  # pino 35
        self.LED_RGB_GREEN_EXIT = 13  # pino 33
        self.REED_SWITCH_ENTRANCE = 23  # pino 16
        self.REED_SWITCH_EXIT = 24  # pino 18
        self.RELAY_ENTRANCE = 12  # pino 32
        self.RELAY_EXIT = 16  # pino 36

        self.PATH = "/home/pi/catraca_ifce_maracanau/"
        self.SECOND_DEADLINE_CASE_ACCESS_NEGATED = 3  # segundos para aguardar apos acesso negado
        self.RECORD_TIME_FILE = 1800  # tempo de espera para gravar novamente no arquivo user_log
        self.TURNSTILE_ID = config('TURNSTILE_ID') # id da catraca passado como argumento
        self.entrance_data_tag = 0
        self.exit_data_tag = 0
        self.is_treads_run = False
        self.flag_entrance = True  # se false entao e saida
        self.timestamp = datetime.timestamp(datetime.now())
        self.counter = 0  # contador de tempo para a tread deadline case
        self.api = ApiCommunication()
        self.log_users = LogUsers()
        self.gpio_setup()

    def gpio_setup(self):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(self.REED_SWITCH_ENTRANCE, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.REED_SWITCH_EXIT, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(self.RELAY_EXIT, gpio.OUT)
        gpio.setup(self.RELAY_ENTRANCE, gpio.OUT)
        gpio.setup(self.LED_GREEN_RELAY_EXIT, gpio.OUT)
        gpio.setup(self.LED_GREEN_RELAY_ENTRANCE, gpio.OUT)
        gpio.setup(self.LED_RGB_BLUE_ENTRANCE, gpio.OUT)
        gpio.setup(self.LED_RGB_BLUE_EXIT, gpio.OUT)
        gpio.setup(self.LED_RGB_GREEN_ENTRANCE, gpio.OUT)
        gpio.setup(self.LED_RGB_GREEN_EXIT, gpio.OUT)
        gpio.setup(self.LED_RGB_RED_ENTRANCE, gpio.OUT)
        gpio.setup(self.LED_RGB_RED_EXIT, gpio.OUT)

        try:
            gpio.output(self.RELAY_ENTRANCE, gpio.HIGH)
            gpio.output(self.RELAY_EXIT, gpio.HIGH)
            gpio.output(self.LED_GREEN_RELAY_ENTRANCE, gpio.HIGH)
            gpio.output(self.LED_GREEN_RELAY_EXIT, gpio.HIGH)
            gpio.output(self.LED_RGB_BLUE_ENTRANCE, gpio.HIGH)
            gpio.output(self.LED_RGB_BLUE_EXIT, gpio.HIGH)
            gpio.output(self.LED_RGB_RED_ENTRANCE, gpio.LOW)
            gpio.output(self.LED_RGB_RED_EXIT, gpio.LOW)
            gpio.output(self.LED_RGB_GREEN_ENTRANCE, gpio.LOW)
            gpio.output(self.LED_RGB_GREEN_EXIT, gpio.LOW)
        except Exception as e:
            print(e)

    # pisca o led azul do rgb para indicar leitura no aquivo backup_users
    # pode representar falha na requisição ou na rede
    def __blink_led_rgb_blue(self, is_entrance):
        for i in range(2):
            if is_entrance:
                gpio.output(self.LED_RGB_BLUE_ENTRANCE, gpio.HIGH)
                time.sleep(0.125)
                gpio.output(self.LED_RGB_BLUE_ENTRANCE, gpio.LOW)
                time.sleep(0.125)
            else:
                gpio.output(self.LED_RGB_BLUE_EXIT, gpio.HIGH)
                time.sleep(0.125)
                gpio.output(self.LED_RGB_BLUE_EXIT, gpio.LOW)
                time.sleep(0.125)

    # faz requisição para autenticar o usuário
    # em caso de falha na requisição, consulta o arquivo backup_users.txt
    def __verify_tag_request(self, card_tag, is_entrance):
        request = self.api.authenticate_card(card_tag)
        if type(request) == bool:  # nao deu erro na requisicao
            return request
        else:  # se der erro na requisicao, nosso sistema continua funcionando de forma independente
            self.__blink_led_rgb_blue(is_entrance)
            with open(self.PATH + "backup_users.txt", "r") as my_file:
                lines = my_file.readlines()
                for i in range(len(lines)):
                    if int(lines[i]) == int(card_tag):
                        my_file.close()
                        return True
                my_file.close()
                return False

    # verifica se o usuário tem acesso
    # caso afirmativo seta "is_treads_run" para True
    # caso negativo acende o led indicador vermelho por 3s
    def validate_access(self, is_entrance, card_tag):
        # apaga led azul para indicar que está fazendo a requisição para api
        # o tempo do led apagado indica demora na resposta da api
        if is_entrance:
            gpio.output(self.LED_RGB_BLUE_ENTRANCE, gpio.LOW)
        else:
            gpio.output(self.LED_RGB_BLUE_EXIT, gpio.LOW)

        if self.__verify_tag_request(card_tag, is_entrance):
            if is_entrance:
                gpio.output(self.RELAY_ENTRANCE, gpio.LOW)
                gpio.output(self.LED_GREEN_RELAY_ENTRANCE, gpio.LOW)
                gpio.output(self.LED_RGB_BLUE_ENTRANCE, gpio.LOW)
                gpio.output(self.LED_RGB_RED_ENTRANCE, gpio.LOW)
                gpio.output(self.LED_RGB_GREEN_ENTRANCE, gpio.HIGH)
            else:
                gpio.output(self.RELAY_EXIT, gpio.LOW)
                gpio.output(self.LED_GREEN_RELAY_EXIT, gpio.LOW)
                gpio.output(self.LED_RGB_BLUE_EXIT, gpio.LOW)
                gpio.output(self.LED_RGB_RED_EXIT, gpio.LOW)
                gpio.output(self.LED_RGB_GREEN_EXIT, gpio.HIGH)
            self.is_treads_run = True
            self.flag_entrance = is_entrance
        else:
            if is_entrance:
                gpio.output(self.LED_RGB_BLUE_ENTRANCE, gpio.LOW)
                gpio.output(self.LED_RGB_GREEN_ENTRANCE, gpio.LOW)
                gpio.output(self.LED_RGB_RED_ENTRANCE, gpio.HIGH)
                time.sleep(self.SECOND_DEADLINE_CASE_ACCESS_NEGATED)
                gpio.output(self.LED_RGB_RED_ENTRANCE, gpio.LOW)
                gpio.output(self.LED_RGB_BLUE_ENTRANCE, gpio.HIGH)

            else:
                gpio.output(self.LED_RGB_BLUE_EXIT, gpio.LOW)
                gpio.output(self.LED_RGB_GREEN_EXIT, gpio.LOW)
                gpio.output(self.LED_RGB_RED_EXIT, gpio.HIGH)
                time.sleep(self.SECOND_DEADLINE_CASE_ACCESS_NEGATED)
                gpio.output(self.LED_RGB_RED_EXIT, gpio.LOW)
                gpio.output(self.LED_RGB_BLUE_EXIT, gpio.HIGH)

    # caso o usuário não gire a catraca
    # mantem a catraca liberada por 4 segundos
    def deadline_case_tread(self):
        while True:
            if self.is_treads_run:
                time.sleep(1)
                self.counter = self.counter + 1
                if self.counter >= self.SECOND_DEADLINE_CASE_ACCESS_NEGATED + 1:
                    if self.flag_entrance:
                        gpio.output(self.RELAY_ENTRANCE, gpio.HIGH)
                        gpio.output(self.LED_GREEN_RELAY_ENTRANCE, gpio.HIGH)
                        gpio.output(self.LED_RGB_GREEN_ENTRANCE, gpio.LOW)
                        gpio.output(self.LED_RGB_RED_ENTRANCE, gpio.LOW)
                        gpio.output(self.LED_RGB_BLUE_ENTRANCE, gpio.HIGH)
                    else:
                        gpio.output(self.RELAY_EXIT, gpio.HIGH)
                        gpio.output(self.LED_GREEN_RELAY_EXIT, gpio.HIGH)
                        gpio.output(self.LED_RGB_GREEN_EXIT, gpio.LOW)
                        gpio.output(self.LED_RGB_RED_EXIT, gpio.LOW)
                        gpio.output(self.LED_RGB_BLUE_EXIT, gpio.HIGH)
                    self.is_treads_run = False

            else:
                time.sleep(1)
                self.counter = 0

    # caso o usuário termine de passar pela catraca (gire a catraca)
    # após a passagem, o acesso é bloqueado novamente
    def turn_turnstile_case_tread(self):
        while True:
            if self.is_treads_run:
                time.sleep(0.05)
                if self.flag_entrance:
                    if gpio.input(self.REED_SWITCH_ENTRANCE) == 1:
                        gpio.output(self.RELAY_ENTRANCE, gpio.HIGH)
                        gpio.output(self.LED_GREEN_RELAY_ENTRANCE, gpio.HIGH)
                        gpio.output(self.LED_RGB_GREEN_ENTRANCE, gpio.LOW)
                        gpio.output(self.LED_RGB_RED_ENTRANCE, gpio.LOW)
                        gpio.output(self.LED_RGB_BLUE_ENTRANCE, gpio.HIGH)
                        self.log_users.post_or_record_user(self.entrance_data_tag, self.flag_entrance, self.TURNSTILE_ID)
                        self.is_treads_run = False
                else:
                    if gpio.input(self.REED_SWITCH_EXIT) == 1:
                        gpio.output(self.RELAY_EXIT, gpio.HIGH)
                        gpio.output(self.LED_GREEN_RELAY_EXIT, gpio.HIGH)
                        gpio.output(self.LED_RGB_GREEN_EXIT, gpio.LOW)
                        gpio.output(self.LED_RGB_RED_EXIT, gpio.LOW)
                        gpio.output(self.LED_RGB_BLUE_EXIT, gpio.HIGH)
                        self.log_users.post_or_record_user(self.exit_data_tag, self.flag_entrance, self.TURNSTILE_ID)
                        self.is_treads_run = False

            else:
                time.sleep(1)

    # caso a api não esteja funcionando
    # grava o log de usuários do users_list para o arquivo log_users.txt
    # só faz a gravação de 30 em 30 minutos
    def make_log_users_tread(self):
        while True:
            time.sleep(5)
            timestamp_now = datetime.timestamp(datetime.now())

            # passou 30 minutos e nao ha ninguem passandp na catraca, evita conflito na lista de usuarios
            if (timestamp_now - self.timestamp) > self.RECORD_TIME_FILE and (not self.is_treads_run):
                self.timestamp = timestamp_now
                self.log_users.record_log_users_file()
                self.log_users.users_list = []
