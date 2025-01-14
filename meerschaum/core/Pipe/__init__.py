#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Pipes are the primary metaphor of the Meerschaum system.
You can interact with pipe data via `meerschaum.Pipe` objects.

If you are working with multiple pipes, it is highly recommended that you instead use
`meerschaum.utils.get_pipes` (available as `meerschaum.get_pipes`)
to create a dictionary of Pipe objects.

```
>>> from meerschaum import get_pipes
>>> pipes = get_pipes()
```

# Examples
For the below examples to work, `sql:remote_server` must be defined (check with `edit config`)
with correct credentials, as well as a network connection and valid permissions.

## Manually Adding Data
---

```
>>> from meerschaum import Pipe
>>> ### Columns only need to be defined if you're creating a new pipe.
>>> pipe = Pipe('csv', 'energy', columns={'datetime': 'time', 'id': 'station_id'})
>>> 
>>> ### Create a Pandas DataFrame somehow,
>>> ### or you can use a dictionary of lists instead.
>>> df = pd.read_csv('data.csv')
>>> pipe.sync(df)
```

## Registering a Remote Pipe
---

```
>>> from meerschaum import Pipe
>>> pipe = Pipe('sql:remote_server', 'energy', parameters={
...     'fetch': {
...         'definition': 'SELECT * FROM energy_table',
...     },
...     'columns': {'datetime': 'time', 'id': 'station_id'}
... })
>>> 
>>> pipe.sync()
```

"""

from __future__ import annotations
from meerschaum.utils.typing import Optional, Dict, Any, Union, InstanceConnector, List

class Pipe:
    """
    Access Meerschaum pipes via Pipe objects.
    
    Pipes are identified by the following:

    1. Connector keys (e.g. `'sql:main'`)
    2. Metric key (e.g. `'weather'`)
    3. Location (optional; e.g. `None`)
    
    A pipe's connector keys correspond to a data source, and when the pipe is synced,
    its `fetch` definition is evaluated and executed to produce new data.
    
    Alternatively, new data may be directly synced via `pipe.sync()`:
    
    ```
    >>> from meerschaum import Pipe
    >>> pipe = Pipe('csv', 'weather')
    >>>
    >>> import pandas as pd
    >>> df = pd.read_csv('weather.csv')
    >>> pipe.sync(df)
    ```
    """

    from ._fetch import fetch
    from ._data import get_data, get_backtrack_data, get_rowcount
    from ._register import register
    from ._attributes import (
        attributes,
        parameters,
        columns,
        get_columns,
        get_columns_types,
        tags,
        get_id,
        id,
        get_val_column,
        parents,
    )
    from ._show import show
    from ._edit import edit, edit_definition
    from ._sync import sync, get_sync_time, exists, filter_existing
    from ._delete import delete
    from ._drop import drop
    from ._clear import clear
    from ._bootstrap import bootstrap

    def __init__(
        self,
        connector: str,
        metric: str,
        location: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        columns: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        mrsm_instance: Optional[Union[str, InstanceConnector]] = None,
        instance: Optional[Union[str, InstanceConnector]] = None,
        cache: bool = False,
        debug: bool = False,
        location_key: Optional[str] = None,
    ):
        """
        Parameters
        ----------
        connector: str
            Keys for the pipe's source connector, e.g. `'sql:main'`.

        metric: str
            Label for the pipe's contents, e.g. `'weather'`.

        location: str, default None
            Label for the pipe's location. Defaults to `None`.

        parameters: Optional[Dict[str, Any]], default None
            Optionally set a pipe's parameters from the constructor,
            e.g. columns and other attributes.
            You can edit these parameters with `edit pipes`.

        columns: Optional[Dict[str, str]], default None
            Subset of parameters for ease of use.
            If `parameters` is also provided, this dictionary is added under the `'columns'` key.

        mrsm_instance: Optional[Union[str, InstanceConnector]], default None
            Connector for the Meerschaum instance where the pipe resides.
            Defaults to the preconfigured default instance (`'sql:main'`).

        instance: Optional[Union[str, InstanceConnector]], default None
            Alias for `mrsm_instance`. If `mrsm_instance` is supplied, this value is ignored.

        cache: bool, default False
            If `True`, cache fetched data into a local database file.
            Defaults to `False`.
        """
        if location_key in ('[None]', 'None'):
            location_key = None

        from meerschaum.utils.warnings import error
        from meerschaum.config.static import _static_config
        negation_prefix = _static_config()['system']['fetch_pipes_keys']['negation_prefix']
        for k in (connector, metric, location, *(tags or [])):
            if str(k).startswith(negation_prefix):
                error(f"A pipe's keys and tags cannot start with the prefix '{negation_prefix}'.")

        self.connector_keys = str(connector)
        self.connector_key = self.connector_keys ### Alias
        self.metric_key = metric
        self.location_key = location

        ### only set parameters if values are provided
        if parameters is not None:
            self._parameters = parameters

        if columns is not None:
            if self.__dict__.get('_parameters', None) is None:
                self._parameters = {}
            self._parameters['columns'] = columns

        if tags is not None:
            if self.__dict__.get('_parameters', None) is None:
                self._parameters = {}
            self._parameters['tags'] = tags

        ### NOTE: The parameters dictionary is {} by default.
        ###       A Pipe may be registered without parameters, then edited,
        ###       or a Pipe may be registered with parameters set in-memory first.
        from meerschaum.config import get_config
        _mrsm_instance = mrsm_instance if mrsm_instance is not None else instance
        if _mrsm_instance is None:
            _mrsm_instance = get_config('meerschaum', 'instance', patch=True)
        if not isinstance(_mrsm_instance, str):
            self._instance_connector = _mrsm_instance
            self.instance_keys = str(_mrsm_instance)
        else: ### NOTE: must be SQL or API Connector for this work
            self.instance_keys = _mrsm_instance

        self._cache = cache and get_config('system', 'experimental', 'cache')

    @property
    def meta(self):
        """Simulate the MetaPipe model without importing FastAPI."""
        refresh = False
        if '_meta' not in self.__dict__:
            refresh = True

        if refresh:
            self._meta = {
                'connector_keys' : self.connector_keys,
                'metric_key'     : self.metric_key,
                'location_key'   : self.location_key,
                'instance'       : self.instance_keys,
            }
        return self._meta

    @property
    def instance_connector(self) -> Union[InstanceConnector, None]:
        """
        The connector to where this pipe resides.
        May either be of type `meerschaum.connectors.sql.SQLConnector` or
        `meerschaum.connectors.api.APIConnector`.
        """
        if '_instance_connector' not in self.__dict__:
            from meerschaum.connectors.parse import parse_instance_keys
            conn = parse_instance_keys(self.instance_keys)
            if conn:
                self._instance_connector = conn
            else:
                return None
        return self._instance_connector

    @property
    def connector(self) -> Union[meerschaum.connectors.Connector, None]:
        """
        The connector to the data source.
        May be of type `'sql'`, `'api`', `'mqtt'`, or `'plugin'`.
        """
        if '_connector' not in self.__dict__:
            from meerschaum.connectors.parse import parse_instance_keys
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                try:
                    conn = parse_instance_keys(self.connector_keys)
                except Exception as e:
                    conn = None
            if conn:
                self._connector = conn
            else:
                return None
        return self._connector

    @property
    def cache_connector(self) -> Union[meerschaum.connectors.sql.SQLConnector, None]:
        """
        If the pipe was created with `cache=True`, return the connector to the pipe's
        SQLite database for caching.
        """
        if not self._cache:
            return None

        if '_cache_connector' not in self.__dict__:
            from meerschaum.connectors import get_connector
            from meerschaum.config._paths import DUCKDB_RESOURCES_PATH, SQLITE_RESOURCES_PATH
            _resources_path = SQLITE_RESOURCES_PATH
            self._cache_connector = get_connector(
                'sql', '_cache_' + str(self),
                flavor='sqlite',
                database=str(_resources_path / ('_cache_' + str(self) + '.db')),
            )

        return self._cache_connector

    @property
    def cache_pipe(self) -> Union['meerschaum.Pipe', None]:
        """
        If the pipe was created with `cache=True`, return another `meerschaum.Pipe` used to
        manage the local data.
        """
        if self.cache_connector is None:
            return None
        if '_cache_pipe' not in self.__dict__:
            from meerschaum import Pipe
            from meerschaum.config._patch import apply_patch_to_config
            from meerschaum.utils.sql import sql_item_name
            _parameters = self.parameters.copy()
            _fetch_patch = {
                'fetch': ({
                    'definition': (
                        f"SELECT * FROM {sql_item_name(str(self), self.instance_connector.flavor)}"
                    ),
                }) if self.instance_connector.type == 'sql' else ({
                    'connector_keys': self.connector_keys,
                    'metric_key': self.metric_key,
                    'location_key': self.location_key,
                })
            }
            _parameters = apply_patch_to_config(_parameters, _fetch_patch)
            self._cache_pipe = Pipe(
                self.instance_keys,
                (self.connector_keys + '_' + self.metric_key + '_cache'),
                self.location_key,
                mrsm_instance=self.cache_connector,
                parameters=_parameters,
                cache=False,
            )

        return self._cache_pipe

    @property
    def sync_time(self) -> Union['datetime.datetime', None]:
        """
        Convenience function to get the pipe's latest datetime.
        Use `meerschaum.Pipe.get_sync_time()` instead.
        """
        return self.get_sync_time()

    def __str__(self):
        """
        The Pipe's SQL table name. Converts the `':'` in the `connector_keys` to an `'_'`.
        """
        name = f"{self.connector_keys.replace(':', '_')}_{self.metric_key}"
        if self.location_key is not None:
            name += f"_{self.location_key}"
        return name

    def __eq__(self, other):
        try:
            return (
                isinstance(self, type(other))
                and self.connector_keys == other.connector_keys
                and self.metric_key == other.metric_key
                and self.location_key == other.location_key
                and self.instance_keys == other.instance_keys
            )
        except Exception as e:
            return False

    def __hash__(self):
        ### Using an esoteric separator to avoid collisions.
        sep = "[\"']"
        return hash(
            str(self.connector_keys) + sep
            + str(self.metric_key) + sep
            + str(self.location_key) + sep
            + str(self.instance_keys) + sep
        )

    def __repr__(self):
        return str(self)

    def __getstate__(self):
        """
        Define the state dictionary (pickling).
        """
        state = {
            'connector_keys' : self.connector_keys,
            'metric_key' : self.metric_key,
            'location_key' : self.location_key,
            'parameters' : self.parameters,
            'mrsm_instance' :  self.instance_keys,
        }
        return state

    def __setstate__(self, _state : dict):
        """
        Read the state (unpickling).
        """
        self.__init__(**_state)
