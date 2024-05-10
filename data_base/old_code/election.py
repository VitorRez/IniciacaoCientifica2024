import csv
import os

def create_election():

    names = ['reg_client.py', 
             'adm_client.py',
             'adm_client.cpython-310.pyc',
             'reg_client.cpython-310.pyc']

    current_dir = os.getcwd()
    print(current_dir)
    for root, dirs, files in os.walk('clients'):
        for name in files:
            path = os.path.join(root, name)
            if os.path.isfile(path):
                if name not in names:
                    print(name)
                    os.remove(path)

    for root, dirs, files in os.walk('data_base/candidates'):
        for name in files:
            path = os.path.join(root, name)
            if os.path.isfile(path):
                if name not in names:
                    print(name)
                    os.remove(path)

    for root, dirs, files in os.walk('data_base/offices'):
        for name in files:
            path = os.path.join(root, name)
            if os.path.isfile(path):
                if name not in names:
                    print(name)
                    os.remove(path)

    for root, dirs, files in os.walk('data_base/voters'):
        for name in files:
            path = os.path.join(root, name)
            if os.path.isfile(path):
                if name not in names:
                    print(name)
                    os.remove(path)


    cont = 1
    with open("data_base/elections.csv", 'w') as arquivo_csv:
        escreve_csv = csv.writer(arquivo_csv)
        escreve_csv.writerow(["name", "voters","candidates","num_offices"])
        num_offices = int(input("Quantos cargos? Digite 0 para encerrar: "))
        while num_offices != 0:
            offices = []
            num_digitos = 2
            for i in range(num_offices):
                txt = input("Digite o nome do cargo: ")
                offices.append(txt)
            escreve_csv.writerow([str(cont), f"data_base/voters/voters_{cont}.csv", f"data_base/candidates/candidates_{cont}.csv", num_offices, f"data_base/offices/offices_{cont}.csv"])
            with open(f"data_base/voters/voters_{cont}.csv", "w") as arquivo_eleitor:
                escreve_e = csv.writer(arquivo_eleitor)
                escreve_e.writerow(["name","cpf","id","authenticated","candidate"])
            with open(f"data_base/candidates/candidates_{cont}.csv", "w") as arquivo_candidato:
                escreve_c = csv.writer(arquivo_candidato)
                escreve_c.writerow(["name","cpf","id","office","campaignId"])
            with open(f"data_base/offices/offices_{cont}.csv", "w") as arquivo_offices:
                escreve_ca = csv.writer(arquivo_offices)
                escreve_ca.writerow(["name","digit_num"])
                for i in offices:
                    escreve_ca.writerow([i, str(num_digitos)])
                    num_digitos += 1
            cont += 1
            num_offices = int(input("Quantos cargos? Digite 0 para encerrar: "))


        
     

