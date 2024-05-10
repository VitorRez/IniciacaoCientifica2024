import csv

def search_voter_file(id):
    with open("data_base/elections.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for i in csv_reader:
            if i['name'] == id:
                filename = i['voters']
                return filename
        return False
    
def search_candidate_file(id):
    with open("data_base/elections.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for i in csv_reader:
            if i['name'] == id:
                filename = i['candidates']
                return filename
        return False
    
def search_office_file(id):
    with open("data_base/elections.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for i in csv_reader:
            if i['name'] == id:
                filename = i['offices']
                return filename
        return False

def search_num_office(id):
    with open("data_base/elections.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for i in csv_reader:
            if i['name'] == id:
                filename = i['num_offices']
                return filename
        return False
    
def reg_voter(name, cpf, id):
    
    filename = search_voter_file(id)

    if filename == False:
        return False
    
    with open(filename, 'a') as csv_file:
        write_csv = csv.writer(csv_file)
        write_csv.writerow([name, cpf, id, "0", "0"])

def search_voter(cpf, id):
    filename = search_voter_file(id)

    if filename == False:
        return False
    
    with open(filename, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for i in csv_reader:
            if i['cpf'] == cpf and i['authenticated'] == '1':
                return True
        return False
    
def search_info(cpf, id):

    filename = search_voter_file(id)
    if filename == False:
        return False
    
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for line in csv_reader:
            if line['cpf'] == cpf:
                return True
            
        return False
    
def change_voter_status(cpf, id):
    
    filename = search_voter_file(id)
    if filename == False:
        print('cu')
        return False
    
    with open(filename, 'r+') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        count = 35
        offset = 0
        for line in csv_reader:
            if line['cpf'] == cpf:
                count += (len(line['name'])+len(line['cpf'])+len(line['id'])+len(line['authenticated'])+4)
                csv_file.seek(count+offset, 0)
                csv_file.write('1')
                return
            count += (len(line['name'])+len(line['cpf'])+len(line['id'])+len(line['authenticated'])+len(line['candidate'])+5)
            offset += 1

def list_offices(id):

    filename = search_office_file(id)
    if filename == False:
        return False
    
    offices = []
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for line in csv_reader:
            offices.append(line['name'])

def reg_candidate(name, cpf, id, office, campaignId):

    filename_v = search_voter_file(id)
    filename_c = search_candidate_file(id)

    if filename_v == False or filename_c == False:
        return False
    
    with open(filename_v, 'r+') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        count = 35
        offset = 0
        for line in csv_reader:
            if line['cpf'] == cpf:
                count += (len(line['name'])+len(line['cpf'])+len(line['id'])+len(line['authenticated'])+len(line['candidate'])+5)
                csv_file.seek(count+offset, 0)
                csv_file.write('1')
                with open(filename_c, 'a') as csv_file1:
                    csv_writer = csv.writer(csv_file1)
                    csv_writer.writerow([name, cpf, id, office, campaignId])
                return
            count += (len(line['name'])+len(line['cpf'])+len(line['id'])+len(line['authenticated'])+len(line['candidate'])+5)
            offset += 1