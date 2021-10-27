#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from pygithubapi import GithubApi
import mysql.connector
import argparse
from datetime import date

__version__ = "1.0.0"


DB = "github"
PORT = 3306
HOST = 'localhost'
URL = "https://api.github.com"
METHOD = "GET"

def GithubToMysqlVersion():
    return f"GithubToMysql version : {__version__}"

def createUserTable():
    usertable = "create table user ( id int primary key auto_increment, \
        name varchar(100) not null, \
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP) engine=innoDB;"
    return usertable

def createRepoTable():
    repotable = "create table repository ( id int primary key auto_increment, \
        name varchar(100) not null, \
        full_name varchar(200) not null, \
        description varchar(1000) not null, \
        url varchar(500) not null, \
        git_url varchar(500) not null, \
        ssh_url varchar(500) not null, \
        language varchar(100) not null default '', \
        private bool default false, \
        forks int not null default 0, \
        forks_count int not null default 0, \
        open_issues int not null default 0, \
        watchers int not null default 0, \
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP, \
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, \
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP) engine=innoDB;"
    return repotable
        
def createTrafficTable():
    traffictable = "create table traffic ( idrepo int, \
        ts varchar(20), \
        count int not null default 0, \
        uniques int not null default 0, \
        FOREIGN KEY (idrepo) \
      REFERENCES repository(id) \
      ON UPDATE CASCADE ON DELETE RESTRICT, \
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,  PRIMARY KEY(idrepo, ts) ) engine=innoDB;"
    return traffictable
                
def createDatabase(connection_params):
    with mysql.connector.connect(**connection_params) as dbm:
        with dbm.cursor() as c:
            c.execute(createUserTable())
            c.execute(createRepoTable())
            c.execute(createTrafficTable())
            dbm.commit()

def createUserRecord(connection_params, user):
    with mysql.connector.connect(**connection_params) as dbm:
        with dbm.cursor() as c:
            c.execute(f"select * from user where name = '{user}'")
            resultat = c.fetchall()
            if resultat == 0:
                c.execute(f"insert into user (name) values('{user}')")
                dbm.commit()

def createRepoRecord(connection_params, _repo):
    repo = _repo['name']
    full_name = _repo['full_name']
    description = _repo['description']
    url = _repo['url']
    git_url = _repo['git_url']
    ssh_url = _repo['ssh_url']
    language = _repo['language']
    private = _repo['private']
    forks = _repo['forks']
    forks_count = _repo['forks_count']
    open_issues = _repo['open_issues']
    watchers = _repo['watchers']
    created_at = _repo['created_at']
    updated_at = _repo['updated_at']
    if private == False:
        privatevalue = 0
    else:
        privatevalue = 1     
    #formatting datetime/timestamps
    mycreatedate = created_at.replace('T', ' ').replace('Z', '')           
    myupdatedate = updated_at.replace('T', ' ').replace('Z', '')           
    with mysql.connector.connect(**connection_params) as dbm:
        id = 0
        with dbm.cursor() as c:
            c.execute(f"select id from repository where name = '{repo}'")
            id = c.fetchall()
            if not id:
                c.execute(f"insert into repository (name, full_name, description, url, git_url, ssh_url, language, private, \
                    forks, forks_count, open_issues, watchers, created_at, updated_at) values('{repo}', '{full_name}', \
                        '{description}', '{url}', '{git_url}', '{ssh_url}', '{language}', {privatevalue}, {forks}, {forks_count}, \
                            {open_issues}, {watchers}, '{mycreatedate}', '{myupdatedate}')")
                dbm.commit()
                c.execute(f"select id from repository where name = '{repo}'")
                id = c.fetchall()
    return id              

def createTrafficRecord(connection_params, idrepo, clone):
    with mysql.connector.connect(**connection_params) as dbm:
        now = str(date.today()) + "T00:00:00Z"
        with dbm.cursor() as c:
            c.execute(f"select idrepo, ts from traffic where idrepo = '{idrepo}' and ts = '{clone['timestamp']}'")
            resultat = c.fetchall()
            if not resultat:
                c.execute(f"insert into traffic (idrepo, ts, count, uniques) values('{idrepo}', '{clone['timestamp']}', \
                         '{clone['count']}', '{clone['uniques']}')")
                dbm.commit()
                c.execute(f"select idrepo, ts from traffic where idrepo = {idrepo} and ts = '{clone['timestamp']}'")
                resultat = c.fetchall()
            #update because in the current day the count can be different
            else:
                c.execute(f"update traffic set count = {clone['count']}, uniques = {clone['uniques']} where \
                    idrepo = {idrepo} and ts = '{now}'")
                dbm.commit()
    return resultat      

def queryRepoClone(connection_params):
    with mysql.connector.connect(**connection_params) as dbm:
        with dbm.cursor() as c:
            c.execute("select idrepo, name, sum(count) from traffic, repository where id = idrepo group by idrepo order by sum(count) desc")
            resultat = c.fetchall()
            print("query resultat :")
            for repo in resultat:
                print(repo)

def main(args):
    #filling the empty parameters with default values
    if args.token == '':
        itoken = os.environ.get("GITHUB_TOKEN")
    else:
        itoken = args.token 
    if args.url == '':
        iurl = URL    
    else:
        iurl = args.url
    if args.user == '':
        user = os.environ.get("USER")
    else:
        user = args.user                                   
    mysql_user = os.environ.get("MYSQL_USER")
    if mysql_user == None:
        print("environment variable MYSQL_USER missing!")
        return
    mysql_pwd = os.environ.get("MYSQL_PASSWORD")
    if mysql_pwd == None:
        print("environment variable MYSQL_PASSWORD missing!")
        return
    connection_params = {
        'host': f'{HOST}',
        'port': PORT,
        'user': f'{mysql_user}',
        'password': f'{mysql_pwd}',
        'database': f'{DB}'
    }
    #github api to retrieve list of repos with all information
    api=f"/users/{user}/repos"
    message= GithubApi.runGithubApi(api=api, method=METHOD, url=iurl, user=user, token=itoken, json = "") 
    #print(message)
    if args.create == "yes":
        createDatabase(connection_params)
    createUserRecord(connection_params, user)
    for repo in message:
        #github api to retrieve the traffic infor for each repository
        api = f"/repos/{user}/{repo['name']}/traffic/clones"
        resultat = createRepoRecord(connection_params, repo)
        traffic = GithubApi.runGithubApi(api=api, method=METHOD, url=iurl, user=user, token=itoken, json = "") 
        #the result returned by Mysql is a tuple, needs to retrieve the first value : example (1,)
        tres = resultat[0]
        id = tres[0]
        for clone in traffic['clones']:
            #print(f"repo: {repo['name']}, timestamp : {clone['timestamp']}, count:  {clone['count']}, uniques: {clone['uniques']}")
            resultat = createTrafficRecord(connection_params, id, clone)
            #print(resultat)

    queryRepoClone(connection_params)            


if __name__== "__main__":
    parser = argparse.ArgumentParser(description="GithubToMysql is a python3 program that generates Mysql tables and store some github info to visualize later into Grafana")
    parser.add_argument('-V', '--version', help='Display the version of GithubToMysql', action='version', version=GithubToMysqlVersion())
    parser.add_argument('-c', '--create', help='create Mysql tables for storing repo, traffic info', default='no', choices=['yes', 'no'], required=False)
    parser.add_argument('-U', '--user', help='github user', default='', required=False)    
    parser.add_argument('-t', '--token', help='github token', default='', required=False)    
    parser.add_argument('-u', '--url', help='github url', default='', required=False)    
    args = parser.parse_args()
    main(args)


