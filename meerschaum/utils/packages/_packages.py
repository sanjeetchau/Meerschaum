#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Directory of necessary packages

packages dictionary is structured in the following schema:
    {
        <group> : {
            <import_name> : <install_name>
        }
    }
"""

packages = {
    'required' : {
    
    },
    '_required' : {
        'wheel'            : 'wheel',
        'virtualenv'       : 'virtualenv',
        'imphook'          : 'imphook',
        'dateutil'         : 'python-dateutil',
        'yaml'             : 'PyYAML>=5.3.1',
        'cascadict'        : 'cascadict',
        'pprintpp'         : 'pprintpp',
        'requests'         : 'requests',
        'pyvim'            : 'pyvim',
        'colorama'         : 'colorama',
        'rich'             : 'rich>=9.8.0',
        'more_termcolor'   : 'more-termcolor',
        'aiofiles'         : 'aiofiles',
        'cmd2'             : 'cmd2',
        'python-multipart' : 'multipart',
        'packaging'        : 'packaging',
        'prompt_toolkit'   : 'prompt-toolkit',
    },
    'iot' : {
        'paho' : 'paho-mqtt',
    },
    'drivers' : {
        'psycopg2' : 'psycopg2-binary',
        'pymysql'  : 'pymysql',
    },
    'cli' : {
        'pgcli'   : 'pgcli',
        'mycli'   : 'mycli',
        'litecli' : 'litecli',
    },
    'stack' : {
        'docker'  : 'docker',
        'compose' : 'docker-compose',
    },
}
packages['sql'] = {
    'pandas'     : 'pandas',
    'sqlalchemy' : 'sqlalchemy',
    'databases'  : 'databases',
    'aiosqlite'  : 'aiosqlite',
    'asyncpg'    : 'asyncpg',
    
}
packages['sql'].update(packages['drivers'])
packages['api'] = {
    'uvicorn'       : 'uvicorn',
    'websockets'    : 'websockets',
    'fastapi'       : 'fastapi',
    'jinja2'        : 'jinja2',
    'passlib'       : 'passlib',
    'fastapi_login' : 'fastapi-login',
}
packages['api'].update(packages['sql'])

all_packages = dict()
for group, import_names in packages.items():
    all_packages.update(import_names)

