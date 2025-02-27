#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Copyright 2021 Bennett Meares

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from meerschaum.config import __version__
from meerschaum._internal.docs import index as __doc__
from meerschaum.core.Pipe import Pipe
from meerschaum.utils import get_pipes
from meerschaum.connectors import get_connector
from meerschaum.plugins import Plugin

__pdoc__ = {'gui': False, 'api': False, 'core': False,}
__all__ = ("Pipe", "get_pipes", "get_connector", "Plugin",)
