import re

from django.shortcuts import render, HttpResponse

# Create your views here.
from django.shortcuts import render
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import CreateUserSerializer, UserRetrieveModelSerializer, UserUpdateModelSerializer
from .models import User

# Create your views here.
from .utils import check_access_token


class UserCreateAPIView(CreateAPIView):
    """ 用户注册 """
    """
    {
    "username":"hzml05",
    "password":"123456",
    "password2":"123456",
    "mobile":"17854157513",
    "sms_code":"3664",
    "allow":"true"
    }
    """
    serializer_class = CreateUserSerializer


# class UserCreateAPIView(GenericAPIView):
#     serializer_class = CreateUserSerializer
#     queryset = User.objects.all().order_by('id')
#
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(data=serializer.data, status=status.HTTP_201_CREATED)
class UsernameAPIView(APIView):
    """ 判断用户名是否被注册 """

    def get(self, request, username):
        # if len(username) < 2:
        #     return Response('用户名不能少于2个字节')
        # if len(username) > 20:
        #     return Response('用户名不能大于20个字节')
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data, status=status.HTTP_200_OK)


class MobileAPIView(APIView):
    """ 判断手机号是否被注册 """

    def get(self, request, mobile):
        # if len(mobile) != 11:
        #     return Response('手机号格式不正确')
        # if not re.match(r'1[3-9]\d{9}', mobile):
        #     return Response('手机号格式不正确')
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data, status=status.HTTP_200_OK)


# class UserRetrieveAPIView(RetrieveAPIView):
#     """ 查询详情视图 不接PK """
#     serializer_class = UserRetrieveModelSerializer  # 序列化器类
#     # queryset = User.objects.all()
#     permission_classes = [IsAuthenticated]  # 权限
#
#     def get_object(self):
#         """ 重写此方法，返回要展示的用户模型类 不加pk写法"""
#         return self.request.user

class UserRetrieveAPIView(RetrieveAPIView):
    """ 查询详情视图 """
    serializer_class = UserRetrieveModelSerializer  # 序列化器类
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]  # 权限
    # def get_object(self):
    #     return self.request


# class UserUpdateAPIView(UpdateAPIView):
#     """ 修改Email 不接PK """
#     serializer_class = UserUpdateModelSerializer  # 序列化器类
#     # queryset = User.objects.all()
#     permission_classes = [IsAuthenticated]  # 权限
#
#     def get_object(self):
#         """ 重写此方法，返回要展示的用户模型类 不加pk写法"""
#         return self.request.user

class UserUpdateAPIView(UpdateAPIView):
    """ 修改Email """
    serializer_class = UserUpdateModelSerializer  # 序列化器类
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]  # 权限
    # def get_object(self):
    #     """ 重写此方法，返回要展示的用户模型类 不加pk写法"""
    #     return self.request.user


class EmailVerifyAPIView(APIView):
    """ 激活用户邮箱 """

    def get(self, request):
        token = request.query_params.get('token')
        # token = '?token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTY4NzU5MjU5OSwiZXhwIjoxNjg3Njc4OTk5fQ.eyJ1c2VyX2lkIjoxMiwiZW1haWwiOiIxNzc4MTgzOTZAcXEuY29tIn0.wWKYY_zQOJNSlNxFyMVUt_5LJWIW3Ptwlw3Ieeym-BZs6-kq_X60qddMkqehX3So6vrJ6tPRlz42pnmwet9mkg'
        # user = check_access_token(token)
        if not token:
            return Response({'message': '参数缺失'})
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '激活失败'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()
        return Response({'message': 'ok'})
        # return HttpResponse({'message': 'ok'})
