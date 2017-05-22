import requests


class Api():
    __url = ''

    def __init__(self, url):
        self.__url = url

    def __call(self, path='', method='GET', data=None, **kwargs):
        params = kwargs

        if method in ['POST', 'PUT', 'PATCH']:
            params['data'] = data

        call = getattr(requests, method.lower())

        path_con_barra = path if path.endswith('/') else path + '/'

        return call(self.__url + path_con_barra, **params)

    def get(self, path='', data=None, **kwargs):
        return self.__call(path, 'GET', data, **kwargs)

    def post(self, path='', data=None, **kwargs):
        return self.__call(path, 'POST', data, **kwargs)

    def put(self, path='', data=None, **kwargs):
        return self.__call(path, 'PUT', data, kwargs)
