from django.contrib import admin
from django.urls import path

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from . import views

from apps.users.serializers import CreateUserSerializer

# from meiduo_drf.apps.users.views import SMSCodeView

urlpatterns = [
    path('order/settlement/', views.OrderSettlementAPIView.as_view()),  # 去结算
    path('order/', views.CommitOrderCreateAPIView.as_view()),  # 订单提交
]

# router = DefaultRouter()
# router.register(prefix='areas', viewset=views.AreasReadOnlyModelViewSet, basename='areas')
# urlpatterns += router.urls
