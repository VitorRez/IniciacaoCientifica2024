from api.elections import *
from api.users import *
from api.credentials import *
from crypto.CryptoUtils.hash import *

password = '3684deug'
username = '12373075628'
name = 'Vítor Rezende Silva'

hash_pswd = create_hash(password)

create_user(username, name, hash_pswd, 1)