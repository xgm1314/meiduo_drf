from django.contrib import admin
from django.urls import path

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from . import views

from apps.users.serializers import CreateUserSerializer

# from meiduo_drf.apps.users.views import SMSCodeView

urlpatterns = [
    path('carts/', views.CartsAPIView.as_view()),  # 购物车增删改查
    path('carts/selection/', views.CartSelectedAllAPIView.as_view()),  # 购物车全选
]

# router = DefaultRouter()
# router.register(prefix='areas', viewset=views.AreasReadOnlyModelViewSet, basename='areas')
# urlpatterns += router.urls
