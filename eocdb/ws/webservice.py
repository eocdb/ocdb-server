# The MIT License (MIT)
# Copyright (c) 2018 by EUMETSAT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import json
import logging
import os
import signal
import sys
import time
import traceback
from datetime import datetime
from typing import Optional

import tornado.options
import yaml
from tornado.ioloop import IOLoop
from tornado.log import enable_pretty_logging
from tornado.web import RequestHandler, Application

from .context import WsContext
from .defaults import DEFAULT_ADDRESS, DEFAULT_PORT, DEFAULT_CONFIG_FILE, DEFAULT_UPDATE_PERIOD, DEFAULT_LOG_PREFIX
from .reqparams import RequestParams
from ..core import UNDEFINED

_LOG = logging.getLogger('eocdb')


class WebService:
    """
    A web service that provides a remote API to some application.
    """

    def __init__(self,
                 application: Application,
                 address: str = DEFAULT_ADDRESS,
                 port: int = DEFAULT_PORT,
                 config_file: Optional[str] = None,
                 update_period: Optional[float] = DEFAULT_UPDATE_PERIOD,
                 log_file_prefix: str = DEFAULT_LOG_PREFIX,
                 log_to_stderr: bool = False) -> None:

        """
        Start a tile service.

        The *service_info_file*, if given, represents the service in the filesystem, similar to
        the ``/var/run/`` directory on Linux systems.

        If the service file exist and its information is compatible with the requested *port*, *address*, *caller*, then
        this function simply returns without taking any other actions.

        :param application: The Tornado web application
        :param address: the address
        :param port: the port number
        :param config_file: optional configuration file
        :param update_period: if not-None, time of idleness in seconds before service is updated
        :param log_file_prefix: Log file prefix, default is DEFAULT_LOG_PREFIX
        :param log_to_stderr: Whether logging should be shown on stderr
        :return: service information dictionary
        """
        log_dir = os.path.dirname(log_file_prefix)
        if log_dir and not os.path.isdir(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        options = tornado.options.options
        options.log_file_prefix = log_file_prefix or DEFAULT_LOG_PREFIX
        options.log_to_stderr = log_to_stderr
        enable_pretty_logging()

        self.config_file = os.path.abspath(config_file) if config_file else None
        self.config_mtime = None
        self.update_period = update_period
        self.update_timer = None
        self.config_error = None
        self.service_info = dict(port=port,
                                 address=address,
                                 started=datetime.now().isoformat(sep=' '),
                                 pid=os.getpid())
        self.ws_context = WsContext(base_dir=os.path.dirname(self.config_file or os.path.abspath('')))

        application.ws_context = self.ws_context
        application.time_of_last_activity = time.clock()
        self.application = application

        self.server = application.listen(port, address=address or 'localhost')
        # Ensure we have the same event loop in all threads
        asyncio.set_event_loop_policy(_GlobalEventLoopPolicy(asyncio.get_event_loop()))
        # Register handlers for common termination signals
        signal.signal(signal.SIGINT, self._sig_handler)
        signal.signal(signal.SIGTERM, self._sig_handler)
        self._maybe_load_config()
        self._maybe_install_update_check()

    def start(self):
        address = self.service_info['address']
        port = self.service_info['port']
        _LOG.info(f'web service running, listening on {address}:{port} (press CTRL+C to stop service)')
        if len(self.ws_context.config.get('databases', {})) == 0:
            _LOG.warning('no databases configured')
        IOLoop.current().start()

    def stop(self, kill=False):
        """
        Stops the Tornado web server.
        """
        if kill:
            sys.exit(0)
        else:
            IOLoop.current().add_callback(self._on_shut_down)

    def _on_shut_down(self):

        _LOG.info('stopping web service...')

        # noinspection PyUnresolvedReferences,PyBroadException
        try:
            self.update_timer.cancel()
        except Exception:
            pass

        # Shutdown services such as database drivers
        self.ws_context.dispose()

        if self.server:
            self.server.stop()
            self.server = None

        IOLoop.current().stop()

    # noinspection PyUnusedLocal
    def _sig_handler(self, sig, frame):
        _LOG.warning(f'caught signal {sig}')
        IOLoop.current().add_callback_from_signal(self._on_shut_down)

    def _maybe_install_update_check(self):
        if self.update_period is None or self.update_period <= 0:
            return
        IOLoop.current().call_later(self.update_period, self._maybe_check_for_updates)

    def _maybe_check_for_updates(self):
        self._maybe_load_config()
        self._maybe_install_update_check()

    def _maybe_load_config(self):
        config_file = self.config_file
        if config_file is None:
            if os.path.isfile(DEFAULT_CONFIG_FILE):
                config_file = DEFAULT_CONFIG_FILE
            else:
                return
        try:
            stat = os.stat(config_file)
        except OSError as e:
            if self.config_error is None:
                _LOG.error(f'configuration file {config_file!r}: {e}')
                self.config_error = e
            return
        if self.config_mtime != stat.st_mtime:
            self.config_mtime = stat.st_mtime
            try:
                with open(config_file) as stream:
                    # Reconfigure services such as database drivers
                    self.ws_context.configure(yaml.load(stream))
                self.config_error = None
                _LOG.info(f'configuration file {config_file!r} successfully loaded')
            except (yaml.YAMLError, OSError) as e:
                if self.config_error is None:
                    _LOG.error(f'configuration file {config_file!r}: {e}')
                    self.config_error = e
                return


# noinspection PyAbstractClass
class WsRequestHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(WsRequestHandler, self).__init__(application, request, **kwargs)
        self._header = WsRequestHeader(self)
        self._query = WsRequestQuery(self)
        self._cookie = WsRequestCookie(self)

    @property
    def ws_context(self) -> WsContext:
        return self.application.ws_context

    @property
    def base_url(self):
        return self.request.protocol + '://' + self.request.host

    @property
    def header(self) -> RequestParams:
        return self._header

    @property
    def query(self) -> RequestParams:
        return self._query

    @property
    def cookie(self) -> RequestParams:
        return self._cookie

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'PUT, DELETE, OPTIONS')

    def on_finish(self):
        """
        Store time of last activity so we can measure time of inactivity and then optionally auto-exit.
        """
        self.application.time_of_last_activity = time.clock()

    @classmethod
    def to_json(cls, obj) -> str:
        """Convert object *obj* to JSON string"""
        return json.dumps(obj, indent=2)

    def write_error(self, status_code, **kwargs):
        """
        Overwrite ``RequestHandler`` default behaviour. Our implementation writes a server error response as
        JSON object using the form {"error": {"code": *status_code*, ... }}.

        If the "serve_traceback" is set and *kwargs* contains a value for keyword "exc_info",
        it is expected to be a traceback object from an exception handler and the error object will also contain
        a field "traceback" containing the traceback text lines.
        """
        self.set_header('Content-Type', 'application/json')
        obj = dict(error=dict(code=status_code, message=self._reason))
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            traceback_lines = []
            for traceback_line in traceback.format_exception(*kwargs["exc_info"]):
                traceback_lines.append(traceback_line)
            obj['traceback'] = traceback_lines
        self.finish(self.to_json(obj))


class WsRequestHeader(RequestParams):
    def __init__(self, handler: RequestHandler):
        self.handler = handler

    def get_param(self, name: str, default: Optional[str] = UNDEFINED) -> Optional[str]:
        """
        Get query argument.
        :param name: Query argument name
        :param default: Default value.
        :return: the value or none
        :raise: WsBadRequestError
        """
        if default == UNDEFINED:
            return self.handler.request.headers.get(name)
        return self.handler.request.headers.get(name, default=default)


class WsRequestQuery(RequestParams):
    def __init__(self, handler: RequestHandler):
        self.handler = handler

    def get_param(self, name: str, default: Optional[str] = UNDEFINED) -> Optional[str]:
        """
        Get query argument.
        :param name: Query argument name
        :param default: Default value.
        :return: the value or none
        :raise: WsBadRequestError
        """
        if default == UNDEFINED:
            return self.handler.get_query_argument(name)
        return self.handler.get_query_argument(name, default=default)


class WsRequestCookie(RequestParams):
    def __init__(self, handler: RequestHandler):
        self.handler = handler

    def get_param(self, name: str, default: Optional[str] = UNDEFINED) -> Optional[str]:
        """
        Get query argument.
        :param name: Query argument name
        :param default: Default value.
        :return: the value or none
        :raise: WsBadRequestError
        """
        if default == UNDEFINED:
            return self.handler.get_cookie(name)
        return self.handler.get_cookie(name, default=default)


class _GlobalEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    """
    Event loop policy that has one fixed global loop for all threads.

    We use it for the following reason: As of Tornado 5 IOLoop.current() no longer has
    a single global instance. It is a thread-local instance, but only on the main thread.
    Other threads have no IOLoop instance by default.

    _GlobalEventLoopPolicy is a fix that allows us to access the same IOLoop
    in all threads.

    Usage::

        asyncio.set_event_loop_policy(_GlobalEventLoopPolicy(asyncio.get_event_loop()))

    """

    def __init__(self, global_loop):
        super().__init__()
        self._global_loop = global_loop

    def get_event_loop(self):
        return self._global_loop


def url_pattern(pattern: str):
    """
    Convert a string *pattern* where any occurrences of ``{{NAME}}`` are replaced by an equivalent
    regex expression which will assign matching character groups to NAME. Characters match until
    one of the RFC 2396 reserved characters is found or the end of the *pattern* is reached.

    The function can be used to map URLs patterns to request handlers as desired by the Tornado web server, see
    http://www.tornadoweb.org/en/stable/web.html

    RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
    the following reserved characters::

        reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" | "$" | ","

    :param pattern: URL pattern
    :return: equivalent regex pattern
    :raise ValueError: if *pattern* is invalid
    """
    name_pattern = '(?P<%s>[^\;\/\?\:\@\&\=\+\$\,]+)'
    reg_expr = ''
    pos = 0
    while True:
        pos1 = pattern.find('{', pos)
        if pos1 >= 0:
            pos2 = pattern.find('}', pos1 + 1)
            if pos2 > pos1:
                name = pattern[pos1 + 1:pos2]
                if not name.isidentifier():
                    raise ValueError('name in {name} must be a valid identifier, but got "%s"' % name)
                reg_expr += pattern[pos:pos1] + (name_pattern % name)
                pos = pos2 + 1
            else:
                raise ValueError('no matching "}" after "{" in "%s"' % pattern)

        else:
            reg_expr += pattern[pos:]
            break
    return reg_expr
