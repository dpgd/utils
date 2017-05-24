# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.generic import ListView
from django.middleware.csrf import rotate_token
from django.db.models.query import QuerySet
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from django.conf import settings
import json
import jwt


class JSONResponseMixin(ListView, APIView):
    """Summary.

    A mixin that can be used to render a JSON response.
    It can return JSON data, from post and get requests
    """

    authentication_classes = (TokenAuthentication,)
    message_error = 'El error no está definido'
    '''You can change this method in the model, as_json is the default one'''
    method_json = "as_json"
    parameter_method_json = None
    code = None

    def send_response(self, response):
        response = json.dumps(response, indent=4, separators=(',', ': '))
        return HttpResponse(
            response,
            content_type="application/json")

    def get_collection(self, query):
        response = [
            self.method_execute(obj)
            for obj in query
        ]
        return response

    def get(self, request, *args, **kwargs):
        # CSRF
        rotate_token(request)
        query = self.get_query(request, *args, **kwargs)
        if not isinstance(query, QuerySet):
            return self.error()
        # The Queryset is empty
        # if not query.exists():
        #     self.code = 204
            # Enhancement return this code and no data...
        response = self.get_collection(query)
        return self.send_response(response)

    def post(self, request):
        response = self.get_post(request.data)
        return self.check_response(response)
    """
            --- Hooks ---
    @get_query  >>> Filter the objects models and return a QuerySet Object
    #message_error      >>> String for render the error message

    """

    """
    Dont forget that @get_query method must return a QuerySet Object
    """

    def get_query(self, request=None, *args, **kwargs):
        return self.get_queryset()

    """
    You can change the message_error
    """

    def error(self):
        return HttpResponse(
            self.message_error,
            content_type="application/json",
            status=self.code)

    def method_execute(self, obj):
        method = getattr(obj, self.method_json)
        return method(self.parameter_method_json)


class JWTResponseMixin(JSONResponseMixin):

    def jwt_encoder(self, json):
        encoded = jwt.encode(
            json,
            settings.SECRET_JWT,
            settings.ALGORITHM
        )
        return encoded

    def jwt_decoder(self, jwt_encoded):
        decoded = jwt.decode(
            jwt_encoded, settings.SECRET_JWT, settings.ALGORITHM)
        return decoded

    def send_response(self, response):
        response = {'jwt_token': response}
        response = json.dumps(response, indent=4, separators=(',', ': '))
        return HttpResponse(response, content_type="application/json")

    def get(self, request=None, *args, **kwargs):
        query = self.get_query(request, *args, **kwargs)
        if not isinstance(query, QuerySet):
            return self.error()
        response = self.get_collection(query)
        response_json = {'status': 200, 'data': response}
        encoded = self.jwt_encoder(response_json)
        return self.send_response(encoded)

    def post(self, request):
        response = self.get_post(request.data)
        encoded = None
        if response:
            encoded = self.jwt_encoder(response)
        return self.send_response(encoded)
