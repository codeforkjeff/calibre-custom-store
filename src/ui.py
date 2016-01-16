
import base64
import functools
import urlparse

from calibre import browser
from calibre.gui2.store.basic_config import BasicStoreConfig
from calibre.gui2.store.search_result import SearchResult
from calibre.utils.logging import default_log

from .opensearch import ModifiedOpenSearchOPDSStore
from . import config, auth

REQUIRES_LOGIN = True

# singleton browser object, so we only login once per Calibre session
_browser = None
_browser_init_success = False


# shamelessly copied from https://wiki.python.org/moin/PythonDecoratorLibrary
def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            default_log.debug("memoize cache miss")
            cache[key] = obj(*args, **kwargs)
        else:
            default_log.debug("memoize cache hit")
        return cache[key]
    return memoizer


@memoize
def create_browser(auth_required, login, password, login_handler):
    """
    Creates a browser and logs into website or service, if auth is required.

    This fn is memoized, so same browser object is returned on subsequent calls
    with the same args.

    :param auth_required: boolean
    :param login_handler: function
    :param login: string
    :param password: string
    :return:
    """

    global _browser, _browser_init_success

    default_log.debug("creating browser object...")
    _browser = browser()
    if auth_required:
        default_log.debug("logging in...")
        login_handler(_browser, login, password)

    return _browser


def _base_url(url):
    """
    Returns a URL with path and parameters stripped out.
    :param url: string
    :return:
    """
    parts = urlparse.urlparse(url)
    return urlparse.urlunparse([parts[0], parts[1], '', '', '', ''])


class CustomStoreImpl(BasicStoreConfig, ModifiedOpenSearchOPDSStore):

    open_search_url = config.get("opensearch_url")
    web_url = _base_url(open_search_url) if open_search_url else "http://localhost/"

    def search(self, query, max_results=10, timeout=60):
        # Note! Not all results returned from this request get shown by Calibre:
        # it filters down results by looking for search keywords
        # in the different fields according to what user entered in the UI.

        try:
            for s in ModifiedOpenSearchOPDSStore.search(self, query, max_results, timeout, create_browser=self.create_browser):
                s.price = '$0.00'
                s.drm = SearchResult.DRM_UNLOCKED
                yield s
        except Exception, e:
            default_log.error("Error executing search request (maybe bad login credentials?): %s" % (e,))

    def create_browser(self):
        """
        This method is called by the download code.
        :return: browser object
        """
        auth_required = config.get('auth_required')
        login = config.get('login')
        password = base64.b64decode(config.get('password'))
        login_handler = auth.get_login_handler(config.get('login_handler'))
        return create_browser(auth_required, login, password, login_handler)

    def is_customizable(self):
        return True

    def config_widget(self):
        from .widget import CustomStoreConfigWidget
        return CustomStoreConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
