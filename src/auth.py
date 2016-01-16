
"""

This module contains login handlers, which prepare a browser object
by logging into a website before other code uses its OpenSearch API.

To add a login handler, just create a new function and decorate it
with @login_handler. It should automatically appear in the configuration
widget.

"""

import inspect
import sys

from calibre.utils.logging import default_log
from mechanize._form import ControlNotFoundError

from . import config


def login_handler(fn):
    """
    Decorator for functions that can be used as a login handler.
    Sanity-checks that fn takes 3 arguments.
    :param fn: function object
    :return:
    """
    (args, varargs, keywords, defaults) = inspect.getargspec(fn)
    if len(args) != 3:
        raise Exception("login handler functions should take 3 arguments, but %s.%s does not" %
                        (fn.__module__, fn.__name__))
    fn._login_handler = True
    return fn


def is_login_handler(fn):
    return getattr(fn, '_login_handler', False)


def get_login_handler(name):
    """
    Finds a login handler function by name
    :param name: string
    :return: login handler function, or None
    """
    results = [item for item in get_all_login_handlers() if item.__name__ == name]
    if len(results) > 0:
        return results[0]
    return None


def get_all_login_handlers():
    """
    :return: list of function objects
    """
    this_module = sys.modules[__name__]
    members = [getattr(this_module, member) for member in dir(this_module)]
    return [member for member in members if is_login_handler(member)]


@login_handler
def default_login(browser, login, password):
    """
    Default login handler, which looks for fields commonly found on login forms
    and logs in.
    :param browser: browser object
    :param login:
    :param password:
    :return: boolean indicating whether login was successful
    """
    browser.open(config.get('auth_url'))

    # look for things common on login pages
    for form in browser.forms():
        browser.form = form
        login_populated, password_populated = False, False
        for possible_login_field in ['email', 'login']:
            try:
                browser[possible_login_field] = login
                login_populated = True
            except ControlNotFoundError, e:
                pass
            if login_populated:
                break
        try:
            browser['password'] = password
            password_populated = True
        except ControlNotFoundError, e:
            pass
        if login_populated and password_populated:
            response = browser.submit()
            break

    if "Logout" in response.read():
        default_log.debug("Login seemed successful")
        success = True
    else:
        success = False
        # subsequent requests using this browser will fail. oh well. :(
        # we can't do much about it here.
        default_log.error("Login seemed to fail on page %s" % (config.get('auth_url')))

    return success
