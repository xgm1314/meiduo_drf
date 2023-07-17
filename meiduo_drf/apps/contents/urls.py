from django.contrib import admin
from django.urls import path

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from . import crons

from apps.users.serializers import CreateUserSerializer

# from meiduo_drf.apps.users.views import SMSCodeView

urlpatterns = [
    # path('html/', crons.generate_static_index_html()),  # 查询所有省
]


