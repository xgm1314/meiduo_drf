from django.contrib import admin
from django.urls import path, re_path

from rest_framework_jwt.views import obtain_jwt_token

from .views import CreateAPIView, UsernameAPIView, MobileAPIView

from apps.users.serializers import CreateUserSerializer

# from meiduo_drf.apps.users.views import SMSCodeView

urlpatterns = [
    # re_path(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', SMSCodeView.as_view()),  # 路由中设置正则
    path('users/', CreateAPIView.as_view(serializer_class=CreateUserSerializer)),  # 注册用户
    re_path(r'^users/(?P<username>\w{2,20})/count/$', UsernameAPIView.as_view()),  # 路由中设置正则
    # path('users/<username>/count/', UsernameAPIView.as_view()),  # 用户名校验
    re_path(r'mobiles/(?P<mobile>1[3-9]\d{9})/count/$', MobileAPIView.as_view()),  # 手机号校验
    # path('mobiles/<mobile>/count/', MobileAPIView.as_view()),  # 手机号校验

    # jwt登录
    path('jwtlogin/', obtain_jwt_token),

]
