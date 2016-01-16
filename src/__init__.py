#!/usr/bin/python2.7

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import os.path
import traceback

from calibre.customize import StoreBase
from calibre.utils.logging import default_log
from calibre.utils.config import JSONConfig, plugin_dir

store_version = 1  # Needed for dynamic plugin loading

DEBUG = True

if DEBUG:
    default_log.filter_level = default_log.DEBUG

# use config file with static name instead of one named after the plugin
# b/c our name is variable
config = JSONConfig('plugins/custom_store')

_defaults = {
    'name': 'Custom Store',
    'description': 'My Custom Store',
    'opensearch_url': 'http://example.com/opensearch.xml',
    'auth_required': True,
    'auth_url': 'http://example.com/login',
    'login': 'bob@example.com',
    'password': '',
    'login_handler': 'default_login',
}

for key in _defaults.keys():
    if key not in config:
        config[key] = _defaults[key]

# awful hack to ensure that calibre always creates this plugin
# as "Custom Store.zip" instead of using the changeable name in plugin class
name = config.get('name')
if "calibre-customize" in traceback.format_stack()[0] or \
        not os.path.exists(os.path.join(plugin_dir, 'Custom Store.zip')):
    name = 'Custom Store'


class CustomStore(StoreBase):
    name = name
    description = config.get('description')
    author = 'the interwebs'
    version = (1, 0, 0)
    actual_plugin = 'calibre_plugins.custom_store.ui:CustomStoreImpl'
    # do we need this?
    # formats = ['PDF', 'EPUB', 'MOBI', 'TXT']
    affiliate = False
