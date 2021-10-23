# pygithubapi

python3 module to call github apis in command line or inside a module and export result into mysql and later Grafana.

## pygithubapi.py

It's a python module that you can include in your python module example with GithubToMysql.py

    python3 pygithubapi.py --help
    usage: pygithubapi.py [-h] [-V] [-U USER] [-t TOKEN] [-u URL] [-a API] [-m METHOD]
                        [-J JSONFILE]

    pygithubapi is a python3 program that call github apis in command line or imported as
    a module

    optional arguments:
    -h, --help            show this help message and exit
    -V, --version         Display the version of pygithubapi
    -U USER, --user USER  github user
    -t TOKEN, --token TOKEN
                            github token
    -u URL, --url URL     github url
    -a API, --api API     github api should start by a slash
    -m METHOD, --method METHOD
                            should contain one of the method to use : ['DELETE', 'GET',
                            'POST', 'PUT']
    -J JSONFILE, --jsonfile JSONFILE
                            json file needed for POST method

## GithubToMysql.py

It's to store in mysql some datas before using them into grafana

python3 GithubToMysql.py --help

    usage: GithubToMysql.py [-h] [-V] [-c {yes,no}] [-U USER] [-t TOKEN] [-u URL]

    GithubToMysql is a python3 program that generates Mysql tables and store some github
    info to visualize later into Grafana

    optional arguments:
    -h, --help            show this help message and exit
    -V, --version         Display the version of GithubToMysql
    -c {yes,no}, --create {yes,no}
                            create Mysql tables for storing repo, traffic info
    -U USER, --user USER  github user
    -t TOKEN, --token TOKEN
                            github token
    -u URL, --url URL     github url

Note that Mysql user and Mysql password are passed by environment variable for now.

    mysql_user = os.environ.get("MYSQL_USER")
    mysql_pwd = os.environ.get("MYSQL_PASSWORD")

## ideas to improve

    - working with no sql database like elasticsearch
    - automating the export to grafana using pygrafanaapi
