#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
"""
Start the Meerschaum WebAPI with the `api` action.
"""

from __future__ import annotations
from meerschaum.utils.typing import SuccessTuple, Optional, List, Any

def api(
        action: Optional[List[str]] = None,
        sysargs: Optional[List[str]] = None,
        debug: bool = False,
        mrsm_instance: Optional[str] = None,
        **kw: Any
    ) -> SuccessTuple:
    """
    Send commands to a Meerschaum WebAPI instance.
    
    Usage:
        `api [commands] {options}`

    Examples:
        - `api [start, boot, init]`
            - Start the API server
            - **NOTE:** The command `start api` also starts the server.
        - `api show config`
            - Execute `show config` on the `main` api instance
        - `api main show config`
            - See above
    
    If command is `start`, launch the Meerschaum WebAPI. If command is an api connector label,
        connect to that label. Otherwise connect to `main` api connector.

    """
    from meerschaum.utils.warnings import warn, info
    from meerschaum.utils.formatting import print_tuple
    from meerschaum.utils.packages import attempt_import
    if action is None:
        action = []
    if sysargs is None:
        sysargs = []
    if len(action) == 0:
        info(api.__doc__)
        return False, "Please provide a command to excecute (see above)."

    boot_keywords = {'start', 'boot', 'init'}
    if action[0] in boot_keywords:
        return _api_start(action=action, mrsm_instance=mrsm_instance, debug=debug, **kw)

    from meerschaum.config import get_config
    from meerschaum.connectors import get_connector
    requests = attempt_import('requests')
    if debug:
        from meerschaum.utils.formatting import pprint
    api_configs = get_config('meerschaum', 'connectors', 'api', patch=True)

    api_label = "main"
    args_to_send = list(sysargs)
    ### remove `api`
    if 'api' in args_to_send:
        del args_to_send[0]
    if action[0] in api_configs:
        api_label = action[0]
        ### remove label from actions
        del action[0]
        if len(args_to_send) > 1:
            del args_to_send[0]
    kw['action'] = action
    kw['debug'] = debug
    kw['sysargs'] = args_to_send
    kw['yes'] = True
 
    api_conn = get_connector(type='api', label=api_label)
    
    if mrsm_instance is not None and str(mrsm_instance) == str(api_conn):
        warn(
            f"Cannot send Meerschaum instance keys '{mrsm_instance}' to itself. " +
            "Removing from arguments..."
        )
    elif mrsm_instance is not None:
        kw['mrsm_instance'] = str(mrsm_instance)

    success, message = api_conn.do_action(**kw)
    print_tuple((success, message), common_only=True)
    msg = f"Action " + ('succeeded' if success else 'failed') + " with message:\n" + str(message)
    return success, message

def _api_start(
        action: Optional[List[str]] = None,
        host: Optionsl[str] = None,
        port: Optional[int] = None,
        workers: Optional[int] = None,
        mrsm_instance: Optional[str] = None,
        no_dash: bool = False,
        no_auth: bool = False,
        debug: bool = False,
        nopretty: bool = False,
        production: bool = False,
        **kw: Any
    ) -> SuccessTuple:
    """Start the API server.
    
    Usage:
        `api start {options}`
    
    Options:
        - `-p, --port {number}`
            Port to bind the API server to.
    
        - `--host {address}`
            The address to bind to.
            Defaults to '0.0.0.0'.
    
        - `-w, --workers {number}`
            How many worker threads to run.
            Defaults to the number of CPU cores or 1 on Android.
    
        - `--production, --gunicorn`
            Start the API server with Gunicorn instead of Uvicorn.
            Useful for production deployments.

    Parameters
    ----------
    action: Optional[List[str]] :
         (Default value = None)
    host: Optionsl[str] :
         (Default value = None)
    port: Optional[int] :
         (Default value = None)
    workers: Optional[int] :
         (Default value = None)
    mrsm_instance: Optional[str] :
         (Default value = None)
    no_dash: bool :
         (Default value = False)
    no_auth: bool :
         (Default value = False)
    debug: bool :
         (Default value = False)
    nopretty: bool :
         (Default value = False)
    production: bool :
         (Default value = False)
    **kw: Any :
        

    Returns
    -------

    """
    from meerschaum.utils.packages import (
        attempt_import, venv_contains_package, pip_install, run_python_package
    )
    from meerschaum.utils.misc import is_int
    from meerschaum.utils.formatting import pprint, ANSI
    from meerschaum.utils.debug import dprint
    from meerschaum.utils.warnings import error, warn
    from meerschaum.config import get_config, _config
    from meerschaum.config._paths import (
        API_UVICORN_RESOURCES_PATH, API_UVICORN_CONFIG_PATH, CACHE_RESOURCES_PATH,
        PACKAGE_ROOT_PATH,
    )
    from meerschaum.config.static import _static_config, SERVER_ID
    from meerschaum.connectors.parse import parse_instance_keys
    from meerschaum.utils.pool import get_pool
    import shutil
    import os

    if action is None:
        action = []

    ### Uvicorn must be installed on the host because of multiprocessing reasons.
    uvicorn, gunicorn = attempt_import(
        'uvicorn', 'gunicorn', venv=None, lazy=False, check_update=True
    )

    uvicorn_config_path = API_UVICORN_RESOURCES_PATH / SERVER_ID / '.config.json'
    uvicorn_env_path = API_UVICORN_RESOURCES_PATH / SERVER_ID / '.env'

    api_config = get_config('system', 'api')
    cf = _config()
    uvicorn_config = api_config['uvicorn']
    if port is None:
        ### default
        port = uvicorn_config['port']
        if len(action) > 1:
            if is_int(action[1]):
                port = int(action[1])

    if host is None:
        host = uvicorn_config['host']

    pool = get_pool(workers=workers)
    if pool is None:
        workers = 1
    else:
        pool.close()
        pool.join()
    
    uvicorn_config['workers'] = workers
    uvicorn_config['debug'] = debug

    if mrsm_instance is None:
        mrsm_instance = get_config('meerschaum', 'api_instance', patch=True)

    ### Check if the API instance connector is another API
    instance_connector = parse_instance_keys(mrsm_instance, debug=debug)
    if instance_connector.type == 'api' and instance_connector.protocol != 'https':
        allow_http_parent = get_config(
            'system', 'api', 'permissions', 'chaining', 'insecure_parent_instance'
        )
        if not allow_http_parent:
            return False, (
                "Chaining Meerschaum API instances over HTTP is disabled!\n\n" +
                f"To use '{instance_connector}' as the Meerschaum instance for this API server, " +
                "please do one of the following:\n\n" +
                f"  - Ensure that '{instance_connector}' is available over HTTPS, " +
                "and with `edit config`,\n" +
                f"    change the `protocol` for '{instance_connector}' to 'https'.\n\n" +
                "  - Run `edit config system` and search for `permissions`.\n" +
                "    Under `api:permissions:chaining`, change the value of " +
                "`insecure_parent_instance` to `true`,\n" +
                "    then restart the API process."
            )

    uvicorn_config.update({
        'port': port,
        'host': host,
        'reload': debug,
        'env_file': str(uvicorn_env_path),
        'mrsm_instance': mrsm_instance,
        'no_dash': no_dash,
        'no_auth': no_auth,
    })
    if debug:
        uvicorn_config['reload_dirs'] = [str(PACKAGE_ROOT_PATH)]
    uvicorn_config['use_colors'] = (not nopretty) if nopretty else ANSI

    api_config['uvicorn'] = uvicorn_config
    cf['system']['api']['uvicorn'] = uvicorn_config

    custom_keys = ['mrsm_instance', 'no_dash', 'no_auth']

    ### write config to a temporary file to communicate with uvicorn threads
    import json, sys
    try:
        if uvicorn_config_path.exists():
            os.remove(uvicorn_config_path)
            assert(not uvicorn_config_path.exists())
    except Exception as e:
        error(e)
    uvicorn_config_path.parent.mkdir()
    with open(uvicorn_config_path, 'w+') as f:
        if debug:
            dprint(f"Dumping API config file to '{uvicorn_config_path}'", nopretty=nopretty)
            pprint(uvicorn_config, stream=sys.stderr, nopretty=nopretty)
        json.dump(uvicorn_config, f)

    env_dict = {
        _static_config()['environment']['id']: SERVER_ID,
        _static_config()['environment']['runtime']: 'api',
        _static_config()['environment']['config']: {'system': {'api': {'uvicorn': uvicorn_config}}},
    }
    env_text = ''
    for key, val in env_dict.items():
        value = json.dumps(json.dumps(val)) if isinstance(val, dict) else val
        env_text += f"{key}={value}\n"
    with open(uvicorn_env_path, 'w+') as f:
        if debug:
            dprint(f"Writing ENV file to '{uvicorn_env_path}'.")
        f.write(env_text)

    ### remove custom keys before calling uvicorn

    def _run_uvicorn():
        try:
            uvicorn.run(**{k: v for k, v in uvicorn_config.items() if k not in custom_keys})
        except KeyboardInterrupt:
            pass

    def _run_gunicorn():
        gunicorn_args = [
            'meerschaum.api:app', '--worker-class', 'uvicorn.workers.UvicornWorker',
            '--bind', host + f':{port}',
        ]
        for key, val in env_dict.items():
            gunicorn_args += ['--env', key + '=' + json.dumps(val)]
        if workers is not None:
            gunicorn_args += ['--workers', str(workers)]
        if debug:
            gunicorn_args += ['--log-level=debug', '--enable-stdio-inheritance', '--reload']
        try:
            run_python_package('gunicorn', gunicorn_args, debug=debug, venv='mrsm')
        except KeyboardInterrupt:
            pass


    _run_uvicorn() if not production else _run_gunicorn()

    ### Cleanup
    if uvicorn_config_path.parent.exists():
        shutil.rmtree(uvicorn_config_path.parent)

    return (True, "Success")
