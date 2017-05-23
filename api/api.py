import requests
from django.core.cache import cache
from django.conf import settings


class Api():
    __url = ''
    __needs_auth = False

    def __init__(self, url, needs_auth=False):
        self.__url = url
        self.__needs_auth = needs_auth

    def __call(self, path='', method='GET', data=None, **kwargs):
        params = kwargs

        if method in ['POST', 'PUT', 'PATCH']:
            params['data'] = data

        if self.__needs_auth:
            params['headers'] = dict(
                (params['headers'] if 'headers' in params else {}).items() +
                ({
                    'Authorization': cache.get(settings.CACHE_SESSION_TOKEN_NAME)
                }).items()
            )

        call = getattr(requests, method.lower())

        with_slash = path if path.endswith('/') else path + '/'

        result = call(self.__url + with_slash, **params)

        if result.status_code == '401':
            print 'Unauthorized'

        return result

    def __re_login(self):
        pass

    def get(self, path='', data=None, **kwargs):
        return self.__call(path, 'GET', data, **kwargs)

    def post(self, path='', data=None, **kwargs):
        return self.__call(path, 'POST', data, **kwargs)

    def put(self, path='', data=None, **kwargs):
        return self.__call(path, 'PUT', data, **kwargs)
