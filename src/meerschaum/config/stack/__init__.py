#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Docker Compose stack configuration goes here
"""

import yaml, os
#  from meerschaum.config._read_yaml import config as cf
try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources
from meerschaum.config._paths import GRAFANA_DATASOURCE_PATH, GRAFANA_DASHBOARD_PATH
from meerschaum.config._paths import STACK_COMPOSE_PATH, STACK_ENV_PATH, STACK_COMPOSE_FILENAME

#  db_port = cf['meerschaum']['connectors']['sql']['main']['port']
db_port = "MRSM{meerschaum:connectors:sql:main:port}"

#  db_user = cf['meerschaum']['connectors']['sql']['main']['username']
db_user = "MRSM{meerschaum:connectors:sql:main:username}"

#  db_pass = cf['meerschaum']['connectors']['sql']['main']['password']
db_pass = "MRSM{meerschaum:connectors:sql:main:password}"

#  db_base = cf['meerschaum']['connectors']['sql']['main']['database']
db_base = "MRSM{meerschaum:connectors:sql:main:database}"

### default localhost, meerschaum_db for docker network
db_host = "meerschaum_db"

#  api_port = cf['meerschaum']['connectors']['api']['main']['port']
api_port = "MRSM{meerschaum:connectors:api:main:port}"

api_host = "meerschaum_api"

env_text = (f"""
### Edit environment variables with `edit stack env`
COMPOSE_PROJECT_NAME="meerschaum_stack"
TIMESCALEDB_VERSION="latest-pg12"
POSTGRES_USER="{db_user}"
POSTGRES_PASSWORD="{db_pass}"
POSTGRES_DB="{db_base}"
MEERSCHAUM_DB_HOSTNAME="{db_host}"
MEERSCHAUM_API_HOSTNAME="{api_host}"
ALLOW_IP_RANGE='0.0.0.0/0'
"""
"""
MEERSCHAUM_API_CONFIG='{"meerschaum":{"connectors":{"sql":{"meta":{"host":"${MEERSCHAUM_DB_HOSTNAME}"}}}}}'
MEERSCHAUM_API_CONFIG_RESOURCES=/usr/local/lib/python3.8/site-packages/meerschaum/config/resources/
"""
)
compose_header = """
##############################################################
#                                                            #
#                   DO NOT EDIT THIS FILE!                   #
#                                                            #
# Instead, you can change this file's configuration with     #
# `edit config` under the stack:docker-compose.yaml section. #
# under the stack:docker-compose.yaml section.               #
#                                                            #
##############################################################
"""

volumes = {
    'meerschaum_api_config_resources' : '${MEERSCHAUM_API_CONFIG_RESOURCES}',
    'meerschaum_db_data' : '/var/lib/postgresql/data',
    'grafana_storage' : '/var/lib/grafana',
}
networks = {
    'frontend' : None,
    'backend' : None,
}

default_docker_compose_config = {
    'version' : '3.8',
    'services': {
        'meerschaum_db' : {
            'environment' : [
                'TIMESCALEDB_TELEMETRY=off',
                'POSTGRES_USER=${POSTGRES_USER}',
                'POSTGRES_DB=${POSTGRES_DB}',
                'POSTGRES_PASSWORD=${POSTGRES_PASSWORD}',
                'ALLOW_IP_RANGE=${ALLOW_IP_RANGE}',
            ],
            'image' : 'timescale/timescaledb:${TIMESCALEDB_VERSION}',
            'ports' : [
                f'{db_port}:{db_port}'
            ],
            'hostname' : '${MEERSCHAUM_DB_HOSTNAME}',
            'volumes' : [
                'meerschaum_db_data' + ':' + volumes['meerschaum_db_data']
            ],
            'networks' : [
                'backend'
            ],
        },
        'meerschaum_api' : {
            'image' : 'bmeares/meerschaum:latest',
            'ports' : [f'{api_port}:{api_port}'],
            'hostname' : f'{api_host}',
            'networks' : [
                'frontend',
                'backend'
            ],
            'command' : 'api start',
            'environment' : [
                'MEERSCHAUM_CONFIG=${MEERSCHAUM_API_CONFIG}' 
            ],
            'depends_on' : [
                'meerschaum_db'
            ],
            'volumes' : [
                'meerschaum_api_config_resources' + ':' + volumes['meerschaum_api_config_resources']
            ],
        },
        'grafana' : {
            'image' : 'grafana/grafana:latest',
            'ports' : [
                '3000:3000'
            ],
            'networks' : [
                'frontend',
                'backend'
            ],
            'volumes' : [
                'grafana_storage' + ':' + volumes['grafana_storage'],
                f'{GRAFANA_DATASOURCE_PATH.parent}:/etc/grafana/provisioning/datasources',
                f'{GRAFANA_DASHBOARD_PATH.parent}:/etc/grafana/provisioning/dashboards',
            ],
        },
    },
}
default_docker_compose_config['networks'] = networks
default_docker_compose_config['volumes'] = {}
for key in volumes:
    default_docker_compose_config['volumes'][key] = None

default_stack_config = dict()
default_stack_config[STACK_COMPOSE_FILENAME] = default_docker_compose_config
default_stack_config['.env'] = env_text
from meerschaum.config.stack.grafana import default_grafana_config
default_stack_config['grafana'] = default_grafana_config

### check if configs are in sync
from meerschaum.config._paths import CONFIG_PATH, STACK_ENV_PATH, STACK_COMPOSE_PATH
from meerschaum.config._paths import STACK_COMPOSE_FILENAME, STACK_ENV_FILENAME
from meerschaum.config._paths import GRAFANA_DATASOURCE_PATH, GRAFANA_DASHBOARD_PATH
from meerschaum.config._sync import sync_configs
sync_configs(CONFIG_PATH, ['stack', STACK_COMPOSE_FILENAME], STACK_COMPOSE_PATH)

def get_necessary_files():
    from meerschaum.config._paths import STACK_ENV_PATH, STACK_COMPOSE_PATH, GRAFANA_DATASOURCE_PATH, GRAFANA_DASHBOARD_PATH
    from meerschaum.config._paths import STACK_ENV_FILENAME, STACK_COMPOSE_FILENAME
    from meerschaum.config import config
    return {
        STACK_ENV_PATH : config['stack'][STACK_ENV_FILENAME],
        STACK_COMPOSE_PATH : (config['stack'][STACK_COMPOSE_FILENAME], compose_header),
        GRAFANA_DATASOURCE_PATH : config['stack']['grafana']['datasource'],
        GRAFANA_DASHBOARD_PATH : config['stack']['grafana']['dashboard'],
    }


def write_stack(
        debug : bool = False 
    ):
    from meerschaum.config._edit import general_write_config
    """
    Write Docker Compose configuration files
    """
    return general_write_config(get_necessary_files(), debug=debug)
   
def edit_stack(
        action : list = [''],
        debug : bool = False,
        **kw
    ):
    """
    Open docker-compose.yaml or .env for editing
    """
    from meerschaum.config._edit import general_edit_config
    files = {
        'compose' : STACK_COMPOSE_PATH,
        'docker-compose' : STACK_COMPOSE_PATH,
        'docker-compose.yaml' : STACK_COMPOSE_PATH,
        'env' : STACK_ENV_PATH,
        'environment' : STACK_ENV_PATH,
        '.env' : STACK_ENV_PATH,
    }
    return general_edit_config(action=action, files=files, default='compose', debug=debug)
