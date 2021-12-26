import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def getDoctor():
    date = json.dumps({'date':'23.12.2021','token':''})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    r = requests.post('https://145.255.5.76:55550/API/get_doctor_time', data = date, headers = headers, verify=False)  
    if r.status_code == 200:
        print(r.content.decode('utf-8'))
    else:
        print(r.content.decode('utf-8'))

def createDocument():
    date = json.dumps({'date':'23.12.2021','token':'',
                       'numberAmo':'13','doctor':'Алимгулова Г.У.','time':'8:15','customer':'123','tel':'89276369413','gender':'921291','DateofBirth':'18.12.2021'})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    r = requests.post('https://145.255.5.76:55550/API/cretate_document', data = date, headers = headers, verify=False)  
    if r.status_code == 200:
        print(r.content)


print('request 1 doctor, 2 documet')
rezult  = int(input())
if rezult == 1:
    getDoctor()
elif rezult == 2:
    createDocument()    
