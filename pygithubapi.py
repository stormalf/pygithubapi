#!/usr/bin/python3
# -*- coding: utf-8 -*-
from cryptography.fernet import Fernet
import requests
from json import loads as jsonload
import argparse
import os


'''
pygithubapi.py is to be used by other python modules to automate github api usage.
it could be called in command line.
Examples : 
List of repos :  without any parameters returns the result of "/users/{user}/repos"
    
    python3 pygithubapi.py
    [{'id': 999999999, 'node_id': 'ZZZwZZJlcZZzaZZvcnkzZZZwZZZyZzz=', 'name': 'ansible_modules_customs', 'full_name': 'stormalf/ansible_modules_customs',...}]
Creating a hook : 
    
    POST /repos/{owner}/{repo}/hooks
    python3 pygithubapi.py -J github_hook.json -m POST -a /repos/stormalf/ansible_modules_customs/hooks
    {'type': 'Repository', 'id': 999999999, 'name': 'web', 'active': True, 'events': ['pull_request', 'push'], \
        'config': {'content_type': 'json', 'insecure_ssl': '0', 'url': 'https://example.com/webhook'}...
Checking contexts
    
    PUT /repos/{owner}/{repo}/branches/{branch}/protection/required_status_checks/contexts
    python3 pygithubapi.py -m PUT -a /repos/stormalf/ansible_modules_customs/branches/main/protection/required_status_checks/contexts
    {'message': 'Branch not protected', 'documentation_url': 'https://docs.github.com/rest/reference/repos#set-status-check-contexts'}
Creating an environment: 
    PUT /repos/{owner}/{repo}/environments/{environment_name}    
    python3 pygithubapi.py -m PUT -a /repos/stormalf/ansible_modules_customs/environments/test
    {'id': 999999999, 'node_id': 'ZZ_kwZZZwZZZc9ZZsyZ', 'name': 'test',...}   
Deleting an environment: 
    DELETE /repos/{owner}/{repo}/environments/{environment_name}
    python3 pygithubapi.py -m DELETE -a /repos/stormalf/ansible_modules_customs/environments/test
    {}
List of forks: 
    GET /repos/{owner}/{repo}/forks  
    python3 pygithubapi.py -a /repos/stormalf/ansible_modules_customs/forks
    []
'''

__version__ = "1.0.3"

ALLOWED_METHODS = ["DELETE", "GET", "POST", "PUT"]
URL = "https://api.github.com"
NO_CONTENT = 204
def pyGithubApiVersion():
    return f"pygithubapi version : {__version__}"


class GithubApi():
    def __init__(self, api, method, url, user, token, jsonfile):
        self.api = api
        self.method = method
        self.json = jsonfile
        self.url = url
        self.user = user
        self.token = GithubApi.crypted(token)

    def __repr__(self):
        return (f"GithubApi api: {self.api}, method: {self.method}, url: {self.url}")

    #return the encrypted password/token
    @classmethod
    def crypted(cls, token):
        cls.privkey = Fernet.generate_key()        
        cipher_suite = Fernet(cls.privkey)
        ciphered_text = cipher_suite.encrypt(token.encode())
        cls.token = ciphered_text
        return cls.token

    #return the decrypted password/token
    @classmethod
    def decrypted(cls, token):
        cls.token = token
        cipher_suite = Fernet(cls.privkey)
        decrypted_text = cipher_suite.decrypt(cls.token)
        decrypted_text = decrypted_text.decode()
        return decrypted_text

    #execute the github api using a temp instance
    @staticmethod
    def runGithubApi(api, method, url, user, token, json):
        if token == None:
            response = jsonload('{"message": "Error : token missing!"}')
            return response 
        tempgithub = GithubApi(api, method, url, user, token, json)
        response = tempgithub.githubAuthentication()
        tempgithub = None
        return response       


    #call private function
    def githubAuthentication(self):
        response = self.__githubTokenAuth()
        return response

    #internal function that formats the url and calls the github apis
    def __githubTokenAuth(self):
        apiurl = self.url + self.api  
        header = {}
        header['Accept'] = 'application/vnd.github.v3+json'
        header['Content-Type'] = 'application/json'
        header['Authorization'] = "token " + GithubApi.decrypted(self.token)  
        response = self.__githubDispatch(apiurl, header)
        return response

    #internal function that calls the requests
    def __githubDispatch(self, apiurl, header):
        try:
            if self.method == "POST":
                contents = open(self.json, 'rb')
                response = requests.post(apiurl, data=contents,headers=header)
                contents.close()
            elif self.method == "GET":
                response = requests.get(apiurl, headers=header)
            elif self.method == "PUT":
                if self.json == '':
                    response = requests.put(apiurl, headers=header)
                else:
                    contents = open(self.json, 'rb')
                    response = requests.put(apiurl, data=contents, headers=header)
                    contents.close()
            elif self.method == "DELETE":
                response = requests.delete(apiurl, headers=header)  
            try:                
                response = response.json()                
            except:
                response = "{}"                
        except requests.exceptions.RequestException as e:  
            raise SystemExit(e)   
        return response
def pygithubapi(args):
    message = ''
    if args.user == '':
        user = os.environ.get("USER")
    else:
        user = args.user  
    if args.token == '':
        itoken = os.environ.get("GITHUB_TOKEN")
    else:
        itoken = args.token               
    if args.api == '':
        api=f"/users/{user}/repos"
    else:
        api=args.api    
    if args.url == '':
        iurl = URL
    else:
        iurl = args.url        
    method = args.method     
    if "POST" in method and args.jsonfile == "":
        print("Json file required with method POST!")
        return
    json = args.jsonfile        
    message= GithubApi.runGithubApi(api=api, method=method, url=iurl, user=user, token=itoken, json=json ) 
    return message


if __name__== "__main__":
    helpmethod = f"should contain one of the method to use : {str(ALLOWED_METHODS)}"
    parser = argparse.ArgumentParser(description="pygithubapi is a python3 program that call github apis in command line or imported as a module")
    parser.add_argument('-V', '--version', help='Display the version of pygithubapi', action='version', version=pyGithubApiVersion())
    parser.add_argument('-U', '--user', help='github user', default='', required=False)    
    parser.add_argument('-t', '--token', help='github token', default='', required=False)    
    parser.add_argument('-u', '--url', help='github url', default='', required=False)    
    parser.add_argument('-a', '--api', help='github api should start by a slash', default='', required=False)    
    parser.add_argument('-m', '--method', help = helpmethod, default="GET", required=False)   
    parser.add_argument('-J', '--jsonfile', help='json file needed for POST method', default='', required=False)
    args = parser.parse_args()
    message = pygithubapi(args)
    print(message)