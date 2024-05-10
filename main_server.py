import threading
from certificates.certifying_authority import *
from entities.registrar import *
from entities.administrator import *
from entities.validator import *
from entities.tallier import *
from entities.authority import *
from servers.reg_server import *
from servers.adm_server import *
from crypto.ciphers import *
#fromdata_base.old_code.electione.election import *

def main():
    aut = autorithy()
    reg = registrar()
    adm = administrator()
    val = validator()
    tal = tallier()
    
    autoridade_certificadora(aut, reg, adm, val, tal)

    #create_election()

    s_reg = server_reg(reg)
    s_adm = server_adm(adm)
    thread_reg = threading.Thread(target=s_reg.start_reg)
    thread_adm = threading.Thread(target=s_adm.start_adm)
    thread_reg.start()
    thread_adm.start()

main()