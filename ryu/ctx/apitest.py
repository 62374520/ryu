import requests
from requests.auth import HTTPBasicAuth


def addFlow():
    url = 'http://127.0.0.1:8080/stats/flowentry/add'
    headers = {'Content-Type': 'application/json'}
    json = open('./ryu_timeout.json').read()
    response = requests.post(url, data=json, headers=headers)
    print(response.content)

# def delFlow():
#     url = 'http://127.0.0.1:8080/stats/flowentry/delete'
#     headers = {'Content-Type': 'application/json'}
#     json = open('./ryu_timeout.json').read()
#     print(response.content)



if __name__ == '__main__':
    addFlow()