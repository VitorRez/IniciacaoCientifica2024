import threading
from certificates.certifying_authority import *
from entities.registrar import *
from entities.administrator import *
from entities.validator import *
from entities.tallier import *
from entities.authority import *
from entities.election_manager import *
from reg_server import *
from adm_server import *
from election_server import *
from crypto.ciphers import *
#fromdata_base.old_code.electione.election import *

def main():
    aut = autorithy()
    reg = registrar()
    adm = administrator()
    val = validator()
    tal = tallier()
    election = election_manager()

    
    autoridade_certificadora(aut, reg, adm, val, tal)

    #create_election()

    s_reg = server_reg(reg)
    s_adm = server_adm(adm)
    s_election = server_election(election)
    thread_reg = threading.Thread(target=s_reg.start_reg)
    thread_adm = threading.Thread(target=s_adm.start_adm)
    thread_election = threading.Thread(target=s_election.start_election)
    thread_reg.start()
    thread_adm.start()
    thread_election.start()

main()