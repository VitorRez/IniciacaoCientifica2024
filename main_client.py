from clients.adm_client import *
from clients.reg_client import *
from crypto.ciphers import *
from crypto.sign import *
from crypto.PBKDF import *

nome = 'vitor'
cpf = "12373075628"
unidade = "1"
cargo = "presidente"
id = "13"
option = 0
while option != 1:
    option = int(input('[REGISTER: 0, APPLYING: 1, QUIT: 2]'))
    if option == 0:
        info = input('Digite nome, cpf e identificador da eleição: ')
        info = info.split()
        send_to_reg(info[0], info[1], info[2])
    if option == 1:
        info = input('Digite nome, cpf, identificador da eleição, cargo e número de campanha: ')
        info = info.split()
        send_to_adm(info[0], info[1], info[2], info[3], info[4])