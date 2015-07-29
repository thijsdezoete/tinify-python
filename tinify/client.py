# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import platform
import requests
import requests.exceptions
import six
import traceback

from . import Tinify
from .errors import ConnectionError, Error

class Client(object):
    API_ENDPOINT = 'https://api.tinify.com'
    USER_AGENT = 'Tinify/{} {}/{}'.format(Tinify.VERSION, platform.python_implementation(), platform.python_version())

    def __init__(self, key, app_identifier=None):
      self.session = requests.sessions.Session()
      self.session.auth = ('api', key)
      self.session.headers = {
        'user-agent': self.USER_AGENT + ' ' + app_identifier if app_identifier else self.USER_AGENT,
      }
      self.session.verify = True

    def __enter__(self):
      return self

    def __exit__(self, *args):
      self.close()

    def close(self):
      self.session.close()

    def request(self, method, url, body=None, header={}):
      url = url if url.lower().startswith('https://') else self.API_ENDPOINT + url
      params = {}
      if isinstance(body, dict):
        params['json'] = body
      elif body:
        params['data'] = body

      try:
        response = self.session.request(method, url, **params)
      except requests.exceptions.Timeout as err:
        six.raise_from(ConnectionError('Timeout while connecting'), err)
      except Exception as err:
        six.raise_from(ConnectionError('Error while connecting: {}'.format(err)), err)

      count = response.headers.get('compression-count')
      if count:
        Tinify.compression_count = int(count)

      if response.ok:
        return response
      else:
        details = None
        try:
          details = response.json()
        except Exception as err:
          details = { 'message': 'Error while parsing response: {}'.format(err), 'error': 'ParseError' }
        raise Error.create(details.get('message'), details.get('error'), response.status_code)
