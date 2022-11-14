import serial
import time
import turnstile
from read_tag_serial import ReadTagSerial
import threading


class TurnstileActivation(turnstile.Turnstile):

    def __init__(self):
        super(TurnstileActivation, self).__init__()
        self.read_tag_serial = ReadTagSerial()
        self.rpi_serial_port = serial.Serial('/dev/ttyS0', 9600, timeout=1)  # ttyACM1 for Arduino board
        self.usb_serial_port = self.read_tag_serial.usb_serial_connect()

    def activate_turnstile(self):
        try:
            t = threading.Thread(target=self.deadline_case_tread)
            t.start()
            t2 = threading.Thread(target=self.turn_turnstile_case_tread)
            t2.start()
            t3 = threading.Thread(target=self.make_log_users_tread)
            t3.start()
        except Exception as e:
            print(e)
        while True:
            try:
                self.read_usb_serial_port()  # leitura serial por usb usado para SAIDA
                self.read_rpi_serial_port()  # leitura serial do rpi usado para ENTRADA
            except Exception as e:
                print(e)
                time.sleep(0.5)
                self.usb_serial_port = self.read_tag_serial.usb_serial_connect()
                pass

    # leitura serial pela usb usado para SAIDA
    def read_usb_serial_port(self):
        usb_tag = []
        usb_read_byte = self.usb_serial_port.read()
        if usb_read_byte == b'\x02':
            for counter in range(12):
                usb_read_byte = self.usb_serial_port.read()
                usb_tag.append(str(usb_read_byte))
            self.exit_data_tag = self.read_tag_serial.hex_to_wiegand(usb_tag)
            if self.exit_data_tag != "00000000":
                self.validate_access(False, self.exit_data_tag)
            while self.is_treads_run:
                time.sleep(0.1)
        self.usb_serial_port.flushInput()

    # leitura serial do rpi usado para ENTRADA
    def read_rpi_serial_port(self):
        tag = []
        read_byte = self.rpi_serial_port.read()
        if read_byte == b'\x02':
            for Counter in range(12):
                read_byte = self.rpi_serial_port.read()
                tag.append(str(read_byte))
            self.entrance_data_tag = self.read_tag_serial.hex_to_wiegand(tag)
            if self.entrance_data_tag != "00000000":
                self.validate_access(True, self.entrance_data_tag)
            while self.is_treads_run:
                time.sleep(0.1)
        self.rpi_serial_port.flushInput()
