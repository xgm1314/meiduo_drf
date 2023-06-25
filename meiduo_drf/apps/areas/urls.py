from django.contrib import admin
from django.urls import path

from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from . import views

from apps.users.serializers import CreateUserSerializer

# from meiduo_drf.apps.users.views import SMSCodeView

urlpatterns = [
    # path('areas/', views.AreasListAPIView.as_view()),  # 查询所有省
    # path('areas/<int:pk>/', views.AreasDetailAPIView.as_view()),  # 查询所有省
]

router = DefaultRouter()
router.register(prefix='areas', viewset=views.AreasReadOnlyModelViewSet, basename='areas')
urlpatterns += router.urls
