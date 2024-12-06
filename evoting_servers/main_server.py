import threading
from adm_server import *
from reg_server import *
from certificates.certifying_authority import *

def main():
    reg = registrar_server()
    adm = administrator_server()

    thread_reg = threading.Thread(target=reg.start)
    thread_adm = threading.Thread(target=adm.start)

    thread_reg.start()
    thread_adm.start()

main()