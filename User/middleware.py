from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
from rest_framework_jwt.settings import api_settings


class JwtTokenAuthenticationMiddleware(MiddlewareMixin):

    @staticmethod
    def process_request(request):
        white_list = ['', '/login', '/register', '/swagger', '/redoc']
        if request.path not in white_list:
            print(request.path, "need token Authentication")
            token = request.META.get('HTTP_AUTHORIZATION')
            try:
                # 这里要确保导入的是rest_framework_jwt.settings
                # 导入rest_framework.settings 会报错
                jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
                jwt_decode_handler(token)
            except ExpiredSignatureError:
                return HttpResponse("Token is expired")
            except InvalidTokenError:
                return HttpResponse("Token verification failed.")
            except PyJWTError:
                return HttpResponse("Token is exception")
        else:
            print(request.path, "not need token Authentication")
