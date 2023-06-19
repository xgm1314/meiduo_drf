import re

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CreateUserSerializer
from .models import User


# Create your views here.

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
