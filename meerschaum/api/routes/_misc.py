#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Miscellaneous routes
"""

import os
from meerschaum.api import app
from starlette.responses import FileResponse

@app.get('/favicon.ico')
def get_favicon() -> FileResponse:
    from meerschaum.config._paths import API_STATIC_PATH
    return FileResponse(os.path.join(API_STATIC_PATH, 'ico', 'logo.ico'))
