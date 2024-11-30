import json, uuid

from django.contrib.auth import logout
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework_jwt.settings import api_settings
from User.models import UserModel, UserSerializer
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

def home(request):
    return render(request, 'home.html')


def custom_jwt_payload_handler(user):
    return {
        'UID': str(user.UID),
        'name': user.name,
        'password': user.password,
        'email': user.email,
        'role': user.role,
        # 添加其他需要的字段
    }


# class TestView(View):
#
#     @staticmethod
#     def get(request):
#         token = request.META.get('HTTP_AUTHORIZATION')
#         if token is not None and token != '':
#             question_list = QuestionsModel.objects.all()
#             question_json_list = list(question_list.values())
#             return JsonResponse({'code': 200, 'msg': 'ok', 'data': question_json_list}, status=200)
#         else:
#             return JsonResponse({'code': 401, 'msg': 'token illegal'}, status=401)
#
#
# class JwtView(View):
#
#     @staticmethod
#     def get(request):
#         user = UserModel.objects.get(name='aaaa')
#         payload = custom_jwt_payload_handler(user)
#         token = api_settings.JWT_ENCODE_HANDLER(payload)
#         return JsonResponse({'code': 200, 'token': token}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):

    @staticmethod
    def post(request):
        # 路由传参
        # nickname = request.GET.get('nickname')
        # password = request.GET.get('password')
        # json传参

        if not request.body:
            return JsonResponse({'code': 400, 'info': 'Request body is empty!'}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'info': 'Invalid JSON format!'}, status=400)

        name = data.get('name')
        password = data.get('password')

        print('name:', name, 'password:', password)
        try:
            user = UserModel.objects.get(name=name, password=password)
            payload = custom_jwt_payload_handler(user)
            token = api_settings.JWT_ENCODE_HANDLER(payload)

        except Exception as e:
            print(e)
            return JsonResponse({'code': 500, 'info': 'name or password error'}, status=500)
        # return JsonResponse(
        #     {'code': 200, 'token': token, 'info': 'login successfully', 'data': UserSerializer(user).data}, status=200)
        return JsonResponse(
            {'code': 200, 'info': 'login successfully',
             'data': {
                 'User': UserSerializer(user).data,
                 'token': token
             }}, status=200)


class RegisterView(View):

    @staticmethod
    def post(request):

        if not request.body:
            return JsonResponse({'code': 400, 'info': 'request body is empty!'}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'info': 'Invalid JSON format!'}, status=400)

        new_name = data.get('name')
        new_password = data.get('password')
        new_email = data.get('email')
        new_role = data.get('role')

        if new_name is None or new_password is None or new_email is None or new_role is None:
            return JsonResponse({'code': 400, 'info': 'error: Please provide all required fields.'}, status=400)

        if UserModel.objects.filter(name=new_name).exists():
            return JsonResponse({'code': 401, 'info': 'error: name already exists.'}, status=401)

        if UserModel.objects.filter(email=new_email).exists():
            return JsonResponse({'code': 402, 'info': 'error: Email already exists.'}, status=402)

        rand_uuid = uuid.uuid4()
        uuid_str = str(rand_uuid).replace('-', '')

        new_user = UserModel(
            UID=uuid_str,
            name=new_name,
            password=new_password,
            email=new_email,
            role=new_role,
        )

        new_user.save()

        return JsonResponse(
            {'code': 200, 'info': 'New user created successfully.',
             'data': UserSerializer(new_user).data
             }, status=200)


class ProfileView(View):

    @staticmethod
    def get(request):
        # if not request.body:
        #     return JsonResponse({'code': 400, 'info': 'request body is empty!'}, status=400)
        # try:
        #     data = json.loads(request.body)
        # except json.JSONDecodeError:
        #     return JsonResponse({'code': 400, 'info': 'Invalid JSON format!'}, status=400)

        name = request.GET.get('name')
        if not name:
            return JsonResponse({'code': 400, 'info': 'name field is empty!'}, status=400)

        try:
            user = UserModel.objects.get(name=name)
        except UserModel.DoesNotExist:
            return JsonResponse({'code': 500, 'info': 'user does not exist!'}, status=500)

        return JsonResponse({'code': 200, 'info': 'user profile get successfully',
                             'data': UserSerializer(user).data}, status=200)

    @staticmethod
    def post(request):
        if not request.body:
            print(f"{'code': 400, 'info': 'request body is empty!'}")
            return JsonResponse({'code': 400, 'info': 'request body is empty!'}, status=400)
        try:
            data = json.loads(request.body)
            print(f'data: {data}')
        except json.JSONDecodeError:
            print(f"{'code': 400, 'info': 'Invalid JSON format!'}")
            return JsonResponse({'code': 400, 'info': 'Invalid JSON format!'}, status=400)

        name = data.get('name')
        try:
            user = UserModel.objects.get(name=name)
        except UserModel.DoesNotExist:
            print(f"{'code': 500, 'info': 'user does not exist!'}")
            return JsonResponse({'code': 500, 'info': 'user does not exist!'}, status=500)
        uid = user.UID

        new_name = data.get('newname')
        new_password = data.get('newpassword')
        new_email = data.get('newemail')

        try:
            user = UserModel.objects.get(UID=uid)
        except UserModel.DoesNotExist:
            print(f"{'code': 501, 'info': 'user does not exist!'}")
            return JsonResponse({'code': 501, 'info': 'user does not exist!'}, status=501)

        if new_name is None and new_password is None and new_email is None:
            print(f"{'code': 200, 'info': 'Nothing happen'}")
            return JsonResponse({'code': 200, 'info': 'Nothing happen'}, status=200)
        else:
            if new_name is not None:
                if len(new_name) == 0:
                    print(f"{'code': 400, 'info': 'error: new name is empty!'}")
                    return JsonResponse({'code': 400, 'info': 'error: new name is empty!'}, status=400)
                if UserModel.objects.exclude(UID=uid).filter(name=new_name).exists():
                    print(f"{'code': 401, 'info': 'error: name already exists.'}")
                    return JsonResponse({'code': 401, 'info': 'error: name already exists.'}, status=401)
                else:
                    user.name = new_name

            if new_password is not None:
                if len(new_password) == 0:
                    print(f"{'code': 400, 'info':'error: new password is empty!'}")
                    return JsonResponse({'code': 400, 'info':'error: new password is empty!'}, status=400)
                user.password = new_password

            if new_email is not None:
                if len(new_email) == 0:
                    print(f"{'code': 400, 'info':'error: new email is empty!'}")
                    return JsonResponse({'code': 400, 'info':'error: new email is empty!'}, status=400)
                if UserModel.objects.exclude(UID=uid).filter(email=new_email).exists():
                    print(f"{'code': 402, 'info': 'error: Email already exists.'}")
                    return JsonResponse({'code': 402, 'info': 'error: Email already exists.'}, status=402)
                else:
                    user.email = new_email

            user.save()
            return JsonResponse({'code': 200, 'info': 'user profile modify successfully',
                                 'data': UserSerializer(user).data}, status=200)


def user_logout(request):
    if request.method == 'POST':
        # 登出用户并清除会话数据
        logout(request)
        return JsonResponse({'code': 200, 'info': 'user logout successfully.'}, status=200)
    else:
        return JsonResponse({'code': 405, 'info': 'only accept POST'}, status=405)
