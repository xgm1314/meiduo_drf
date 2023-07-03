from django.contrib import admin
from django.urls import path, re_path

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from .views import CreateAPIView, UsernameAPIView, MobileAPIView, UserRetrieveAPIView, UserUpdateAPIView, \
    EmailVerifyAPIView, AddressGenericViewSet, UserBrowserHistoryCreateAPIView

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

    # path('user/', UserRetrieveAPIView.as_view()),  # 查询详情视图 不接PK
    path('users/<pk>/', UserRetrieveAPIView.as_view()),  # 查询详情视图
    # path('email/', UserRetrieveAPIView.as_view()),  # 修改邮箱视图 不接PK
    path('emails/<int:pk>/', UserUpdateAPIView.as_view()),  # 修改邮箱视图
    path('emails/verification/', EmailVerifyAPIView.as_view()),  # 修改邮箱视图
    path('browser_history/', UserBrowserHistoryCreateAPIView.as_view()),  # 用户浏览记录
]

router = DefaultRouter()
router.register(prefix='address', viewset=AddressGenericViewSet, basename='address')
urlpatterns += router.urls
