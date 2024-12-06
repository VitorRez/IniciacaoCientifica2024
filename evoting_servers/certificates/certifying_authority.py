from crypto.CryptoUtils.certificate import *
from crypto.PyNTRU.NTRU import *
import datetime



#gera as requests e os certificados das principais entidade da etapa de pre eleição
def certifying_authority(aut, reg, adm, val, tal):
    current_time = datetime.datetime.now()

    aut_req = request(current_time.minute, 'certifying authority', aut.key['public_key'])
    reg_req = request(current_time.minute, 'registrar', reg.key['public_key'])
    adm_req = request(current_time.minute, 'administrator', adm.key['public_key'])
    val_req = request(current_time.minute, 'validator', val.key['public_key'])
    tal_req = request(current_time.minute, 'tallier', tal.key['public_key'])

    signed_aut_req = sign(aut.key['private_key'], aut.key['public_key'], aut_req)
    signed_reg_req = sign(aut.key['private_key'], aut.key['public_key'], reg_req)
    signed_adm_req = sign(aut.key['private_key'], aut.key['public_key'], adm_req)
    signed_val_req = sign(aut.key['private_key'], aut.key['public_key'], val_req)
    signed_tal_req = sign(aut.key['private_key'], aut.key['public_key'], tal_req)

    create_certificate(current_time.minute, 'certifying authority', 'certifying authority', aut.key['public_key'], 'SHA256WithNTRUEncrypt', 'BR', 'MG', 'aut', 'certificates/', signed_aut_req)
    create_certificate(current_time.minute, 'certifying authority', 'registrar', reg.key['public_key'], 'SHA256WithNTRUEncrypt', 'BR', 'MG', 'reg', 'certificates/', signed_reg_req)
    create_certificate(current_time.minute, 'certifying authority', 'administrator', adm.key['public_key'], 'SHA256WithNTRUEncrypt', 'BR', 'MG', 'adm', 'certificates/', signed_adm_req)
    create_certificate(current_time.minute, 'certifying authority', 'validator', val.key['public_key'], 'SHA256WithNTRUEncrypt', 'BR', 'MG', 'val', 'certificates/', signed_val_req)
    create_certificate(current_time.minute, 'certifying authority', 'tallier', reg.key['public_key'], 'SHA256WithNTRUEncrypt', 'BR', 'MG', 'tal', 'certificates/', signed_tal_req)