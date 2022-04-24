#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Functions for fetching new data into the Pipe
"""

from __future__ import annotations
from meerschaum.utils.typing import Optional, Any

def fetch(
        self,
        begin: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        sync_chunks: bool = False,
        deactivate_plugin_venv: bool = True,
        debug: bool = False,
        **kw: Any
    ) -> 'pd.DataFrame or None':
    """
    Fetch a Pipe's latest data from its connector.

    Parameters
    ----------
    begin: Optional[datetime.datetime], default None:
        If provided, only fetch data newer than or equal to `begin`.

    end: Optional[datetime.datetime], default None:
        If provided, only fetch data older than or equal to `end`.

    sync_chunks: bool, default False
        If `True` and the pipe's connector is of type `'sql'`, begin syncing chunks while fetching
        loads chunks into memory.

    deactivate_plugin_venv: bool, default True
        If `True` and the pipe's connector is of type `'plugin'`, deactivate the plugin's
        virtual environment after retrieving the dataframe.
        Not intended for general use.

    debug: bool, default False
        Verbosity toggle.

    Returns
    -------
    A `pd.DataFrame` of the newest unseen data.

    """
    if 'fetch' not in dir(self.connector):
        from meerschaum.utils.warnings import warn
        warn(f"No `fetch()` function defined for connector '{self.connector}'")
        return None

    from meerschaum.utils.debug import dprint, _checkpoint
    if self.connector.type == 'plugin':
        from meerschaum.plugins import Plugin
        from meerschaum.utils.packages import activate_venv, deactivate_venv
        connector_plugin = Plugin(self.connector.label)
        connector_plugin.activate_venv(debug=debug)
    
    _chunk_hook = kw.pop('chunk_hook') if 'chunk_hook' in kw else None

    df = self.connector.fetch(
        self,
        begin = begin,
        end = end,
        chunk_hook = (
            self.sync if sync_chunks and _chunk_hook is None
            else _chunk_hook
        ),
        debug = debug,
        **kw
    )
    if self.connector.type == 'plugin' and deactivate_plugin_venv:
        connector_plugin.deactivate_venv(debug=debug)
    ### Return True if we're syncing in parallel, else continue as usual.
    if sync_chunks:
        return True
    return df