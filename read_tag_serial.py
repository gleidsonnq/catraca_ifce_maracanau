import serial
import time


class ReadTagSerial:

    def __init__(self):
        self.is_usb0 = False  #indica se o modulo usbserial está na '/dev/ttyUSB0'

    # tenta se conectar com modulo usbserial
    # verifica se o modulo está na '/dev/ttyUSB0' ou na '/dev/ttyUSB1'
    def usb_serial_connect(self):
        try:
            if self.is_usb0:
                self.is_usb0 = False
                usb_serial = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
            else:
                self.is_usb0 = True
                usb_serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            return usb_serial
        except Exception as e:
            print(e)
            time.sleep(2)
            return self.usb_serial_connect()

    # metodo para converter hexadecimal para decimal
    # recebe um "value" que pode ser o facility ou o card_code, ambos contidos na tag do cartão
    def __hex_to_dec(self, value):
        i = int(value, 16)
        return str(i)

    def hex_to_wiegand(self, tag_hex):
        facility = ""
        card_code = ""

        facility += str(tag_hex[4])
        facility += str(tag_hex[5])
        card_code += str(tag_hex[6])
        card_code += str(tag_hex[7])
        card_code += str(tag_hex[8])
        card_code += str(tag_hex[9])

        facility = facility.replace("b", "").replace("'", "")
        card_code = card_code.replace("b", "").replace("'", "")

        facility = self.__hex_to_dec(facility)
        card_code = self.__hex_to_dec(card_code)

        while len(facility) < 3:
            facility = "0" + facility
        while len(card_code) < 5:
            card_code = "0" + card_code

        return facility + card_code
