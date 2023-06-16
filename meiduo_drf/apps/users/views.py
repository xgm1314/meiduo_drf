from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.generics import CreateAPIView,GenericAPIView
from .serializers import CreateUserSerializer
from .models import User


# Create your views here.

# class UserCreateAPIView(CreateAPIView):
#     """ 用户注册 """
#     serializer_class = CreateUserSerializer
class UserCreateAPIView(GenericAPIView):
    serializer_class = CreateUserSerializer
    queryset = User.objects.all().order_by('id')
