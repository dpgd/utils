from utils.api.Api import Api
from django.http import HttpResponse
from django.conf import settings


class AuthMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return HttpResponse('Unauthorized', status=401)

        jwt_token = request.META.get('HTTP_AUTHORIZATION', None)

        auth_api = Api(settings.CENTRAL_AUTH_API_URL)
        result = auth_api.get(
            'api/auth/',
            headers={
                'Authorization': jwt_token
            })

        if result.status_code == 200:
            return self.get_response(request)

        return HttpResponse(result.content, status=result.status_code)
