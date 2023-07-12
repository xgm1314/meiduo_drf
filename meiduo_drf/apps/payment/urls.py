from django.contrib import admin
from django.urls import path, re_path

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from .views import PaymentAPIView

from apps.users.serializers import CreateUserSerializer

# from meiduo_drf.apps.users.views import SMSCodeView

urlpatterns = [
    path('orders/<int:order_id>/payment/', PaymentAPIView.as_view()),  # 注册用户
    path('payment/status/', PaymentAPIView.as_view()),  # 注册用户

]
