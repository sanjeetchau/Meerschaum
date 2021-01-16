#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

### load metadata
from meerschaum.config import __version__
from meerschaum.config import __doc__

### TODO edit import_children to recursively lazy import submodules
### lazy import submodules
#  from meerschaum.utils.misc import import_children
from meerschaum.utils.packages import lazy_import
actions = lazy_import('meerschaum.actions')
connectors = lazy_import('meerschaum.connectors')
utils = lazy_import('meerschaum.utils')
config = lazy_import('meerschaum.config')
Pipe = lazy_import('meerschaum.Pipe').Pipe
Plugin = lazy_import('meerschaum.Plugin').Plugin
User = lazy_import('meerschaum.User').User
api = lazy_import('meerschaum.api')
get_pipes = utils._get_pipes.get_pipes
get_connector = connectors.get_connector
