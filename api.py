from requests import Session
import json



def response_c_list():
    url = 'https://msfostockweb.pythonanywhere.com/api/v1/company_list'
    headers = {'Content-Type': 'application/json',
               'api-key': '11d83e79b6a8046c76344a07848ef16e28cb3c5cd04c37a97b7008dacad2'}
    session = Session()
    session.headers.update(headers)
    response = session.post(url)
    data = json.loads(response.text)
    return data['company_list']


def c_info(company_name, info):
    url = 'https://msfostockweb.pythonanywhere.com/api/v1/company_info'
    parameters = {'company_name': f'{company_name}', 'info': f'{info}'}
    headers = {'Content-Type': 'application/json',
               'api-key': '912fc1a1ad9851935056c236a37504c86624edeb0be98ee2f90a49e45486'}
    session = Session()
    session.headers.update(headers)
    response = session.post(url, json=parameters)
    data = json.loads(response.text)
    return data['info']

