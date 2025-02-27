#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Wrappers for requests.post
"""

from __future__ import annotations
from meerschaum.utils.typing import Optional, Dict, Any

def post(
        self,
        r_url : str,
        headers : Optional[Dict[str, Any]] = None,
        use_token : bool = True,
        debug : bool = False,
        **kw : Any
    ) -> requests.Response:
    """Wrapper for requests.post

    Parameters
    ----------
    r_url : str :
        
    headers : Optional[Dict[str :
        
    Any]] :
         (Default value = None)
    use_token : bool :
         (Default value = True)
    debug : bool :
         (Default value = False)
    **kw : Any :
        

    Returns
    -------

    """
    if debug:
        from meerschaum.utils.debug import dprint

    if headers is None:
        headers = {}

    if use_token:
        if debug:
            dprint(f"Checking token...")
        headers.update({ 'Authorization': f'Bearer {self.token}' })

    if debug:
        from meerschaum.utils.formatting import pprint
        dprint(f"Sending POST request to {self.url + r_url}")
        if headers:
            pprint(headers)
        pprint(kw)

    return self.session.post(
        self.url + r_url,
        headers = headers,
        **kw
    )
