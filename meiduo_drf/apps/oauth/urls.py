from django.contrib import admin
from django.urls import path, re_path

from rest_framework_jwt.views import obtain_jwt_token

from . import views

from apps.users.serializers import CreateUserSerializer

# from meiduo_drf.apps.users.views import SMSCodeView

urlpatterns = [
    path('qq/oauth/', views.QQOauthURLAPIView.as_view()),
    path('qq/users/', views.OauthQQAPIView.as_view()),
]
