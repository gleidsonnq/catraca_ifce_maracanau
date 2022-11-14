# Catraca_ifce_maracanau

Sistema de Controle de Acesso das Catracas do IFCE de Maracanaú


## Descrição

- main.py
  - arquivo principal a ser executado
  - deve estar no crontab
- backup.py
  - arquivo para baixar o backup de usuários pela api
  - deve estar no crontab
- post_log_user.py
  - responsável por enviar o log de usuário local para a api
  - deve estar no crontab
- turnstile.py
  - responsável pelas funções que executam em threads
  - interação com os LEDs e os pinos do RPI
- turnstile_activation
  - herda da turnstile.py
  - contém a função principal que inicia as threads e interage com o leitor de rfid
- read_tag_serial.py
  - contém funções para conversão dos dados da tag
  - conexão com o módulo usbserial
- api_communication.py
  - responsável pela comunicação com a api
- log_users.py
  - responsável pelas funções de criar ou gravar o log de usuários
  - cria o arquivo log_users.txt


## Configuração no RPI


### git
- Instalar git: sudo apt-get install git 
- No diretório /home/pi do rpi
  - git clone https://gitlab.com/alke.io/catraca_ifce_maracanau.git


### pip3
- sudo apt-get update
- sudo apt install python3-pip


### requirements.txt
- Instalando os pacotes necessários para o projeto
- Dentro do diretorio /home/pi/catraca_ifce_maracanau/
  - pip3 install -r requirements.txt
  - verifique se foi instalado (não precisa executar esses comandos):
    - sudo pip3 install pytz
    - sudo pip3 install python-decouple
    - sudo apt-get install rpi.gpio
    - sudo pip3 install pyserial


### serial
- Para o pyserial funcionar deve realizar esses comandos abaixo:
  - sudo nano /boot/config.txt
    - acrescente no final a seguinte linha “enable_uart=1”
  - sudo systemctl stop serial-getty@ttyS0.service
  - sudo systemctl disable serial-getty@ttyS0.service
  - sudo nano /boot/cmdline.txt
    - remova a linha “console=serial0,115200”
    - salve o arquivo
    - realize o “Reboot” do RPI
- OBS: não consegue executar a serial rodando em uma virtualenv


### nodejs npm e forever
- sudo apt-get install nodejs npm
- sudo -i npm install forever -g


### .env
- Criar um arquivo .env no diretório /root para declarar as variáveis de ambiente
  - TURNSTILE_ID=id_catraca
  - API_USER='usuario_da_api'
  - API_KEY='senha_da_api'
  - API_URL='ip_ou_dns_da_api:porta' (porta=8000)
- O .env deve ser declarado no diretório onde o comando (script) é executado
  - não é necessáriamente o mesmo do projeto 
  - o crontab executa os scripts no /root
  - o forever normalmente executa no /
    - foi usado a opção --workingDir do forever para definir o diretório de execução
      - sudo forever --workingDir /root/ start -c python3 /home/pi/catraca_ifce_maracanau/dist/main.py
    - dessa forma o .env só precisa ser delcarado no /root 


### resolvconf
- Necessário instalar o resolvconf para solucionar problema com o endereço DNS da API
  - apt-get install resolvconf
- Necessário editar o arquivo head dentro do diretório resolv.conf.d/ 
  - sudo nano /etc/resolvconf/resolv.conf.d/head
  - escreva as seguintes linhas no arquivo
    - nameserver 10.50.11.20  #IP do servidor DNS
    - nameserver 8.8.8.8  #DNS do google
- Reiniciar o RPI para verificar se esses dados estão dentro do /etc/resolv.conf (pode fazer isso só no final da configuração se quiser)
  - sudo reboot 
  - sudo cat /etc/resolv.conf 


### crontab
- Configurando o crontab para iniciar o projeto no reboot do RPI
  - sudo crontab -e
    - na primeira vez, vai pedir pra selecionar o editor de texto, selecionamos a opção 1 (nano)
  - escreve no crontab os dados abaixo:
    - @reboot sudo forever --workingDir /root/ start -c python3 /home/pi/catraca_ifce_maracanau/main.py &
    - 0 0 \* \* \* sudo python3 /home/pi/catraca_ifce_maracanau/post_log_user.py &
    - 0 0 \* \* \* sudo python3 /home/pi/catraca_ifce_maracanau/backup.py &
- Reinicie o rpi e pronto!