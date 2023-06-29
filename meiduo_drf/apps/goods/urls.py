from django.contrib import admin
from django.urls import path, re_path

from rest_framework_jwt.views import obtain_jwt_token

from . import views

from apps.users.serializers import CreateUserSerializer

# from meiduo_drf.apps.users.views import SMSCodeView

urlpatterns = [
    path('categories/<int:category_id>/skus/', views.SKUListAPIView.as_view()),
    path('categorys/<int:pk>/skus/', views.CategoryGenericAPIView.as_view()),
]
