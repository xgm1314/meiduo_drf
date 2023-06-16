from django.contrib import admin
from django.urls import path, re_path

from .views import CreateAPIView

# from meiduo_drf.apps.users.views import SMSCodeView

urlpatterns = [
    # re_path(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', SMSCodeView.as_view()),  # 路由中设置正则
    path('users/', CreateAPIView.as_view()),  # 注册用户
]
