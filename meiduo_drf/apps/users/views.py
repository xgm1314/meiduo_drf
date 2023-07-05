import re

from django.shortcuts import render, HttpResponse

# Create your views here.
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin

from django_redis import get_redis_connection

from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_jwt.settings import api_settings

from datetime import datetime

from .serializers import CreateUserSerializer, UserRetrieveModelSerializer, UserUpdateModelSerializer, \
    UserAddressModelSerializer, TitleModelSerializer, UserBrowserHistorySerializer, SKUModelSerializer
from .models import User, Address

# Create your views here.
from .utils import check_access_token
from ..goods.models import SKU
from apps.carts.utils import merge_cart_cookie_to_redis


class UserCreateAPIView(CreateAPIView):
    """ 用户注册 """
    """
    {
    "username":"hzml05",
    "password":"123456",
    "password2":"123456",
    "mobile":"17854157513",
    "sms_code":"3664",
    "allow":"true"
    }
    """
    serializer_class = CreateUserSerializer


# class UserCreateAPIView(GenericAPIView):
#     serializer_class = CreateUserSerializer
#     queryset = User.objects.all().order_by('id')
#
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(data=serializer.data, status=status.HTTP_201_CREATED)
class UsernameAPIView(APIView):
    """ 判断用户名是否被注册 """

    def get(self, request, username):
        # if len(username) < 2:
        #     return Response('用户名不能少于2个字节')
        # if len(username) > 20:
        #     return Response('用户名不能大于20个字节')
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data, status=status.HTTP_200_OK)


class MobileAPIView(APIView):
    """ 判断手机号是否被注册 """

    def get(self, request, mobile):
        # if len(mobile) != 11:
        #     return Response('手机号格式不正确')
        # if not re.match(r'1[3-9]\d{9}', mobile):
        #     return Response('手机号格式不正确')
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data, status=status.HTTP_200_OK)


# class UserRetrieveAPIView(RetrieveAPIView):
#     """ 查询详情视图 不接PK """
#     serializer_class = UserRetrieveModelSerializer  # 序列化器类
#     # queryset = User.objects.all()
#     permission_classes = [IsAuthenticated]  # 权限
#
#     def get_object(self):
#         """ 重写此方法，返回要展示的用户模型类 不加pk写法"""
#         return self.request.user

class UserRetrieveAPIView(RetrieveAPIView):
    """ 查询详情视图 """
    serializer_class = UserRetrieveModelSerializer  # 序列化器类
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]  # 权限
    # def get_object(self):
    #     return self.request


# class UserUpdateAPIView(UpdateAPIView):
#     """ 修改Email 不接PK """
#     serializer_class = UserUpdateModelSerializer  # 序列化器类
#     # queryset = User.objects.all()
#     permission_classes = [IsAuthenticated]  # 权限
#
#     def get_object(self):
#         """ 重写此方法，返回要展示的用户模型类 不加pk写法"""
#         return self.request.user

class UserUpdateAPIView(UpdateAPIView):
    """ 修改Email """
    serializer_class = UserUpdateModelSerializer  # 序列化器类
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]  # 权限
    # def get_object(self):
    #     """ 重写此方法，返回要展示的用户模型类 不加pk写法"""
    #     return self.request.user


class EmailVerifyAPIView(APIView):
    """ 激活用户邮箱 """

    def get(self, request):
        token = request.query_params.get('token')
        # token = '?token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTY4NzU5MjU5OSwiZXhwIjoxNjg3Njc4OTk5fQ.eyJ1c2VyX2lkIjoxMiwiZW1haWwiOiIxNzc4MTgzOTZAcXEuY29tIn0.wWKYY_zQOJNSlNxFyMVUt_5LJWIW3Ptwlw3Ieeym-BZs6-kq_X60qddMkqehX3So6vrJ6tPRlz42pnmwet9mkg'
        # user = check_access_token(token)
        if not token:
            return Response({'message': '参数缺失'})
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '激活失败'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()
        return Response({'message': 'ok'})
        # return HttpResponse({'message': 'ok'})


class AddressGenericViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """ 用户收货地址的增删改查 """
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressModelSerializer

    # queryset = Address.objects.all()

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request):
        """ 展示用户所有地址 """
        queryset = self.get_queryset()
        serializer = self.get_serializer(instance=queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'address': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request):
        """ 新增地址 """
        """
        {
            "title": "活在梦里",
            "receiver":"吱吱吱吱在",
            "province_id":110000,
            "city_id":110100,
            "district_id":110101,
            "place":"zxcvbn",
            "mobile":13112345678
        }
        """
        user = request.user
        # count = user.addresses.all().count()  # 根据用户查询出所有的地址
        count = Address.objects.filter(user=user, is_deleted=False).count()  # 根据关联查询，查出所有地址
        if count > 20:  # 设置收货数量的上限
            return Response({'message': '收货数量达到上限'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)  # 序列化器进行反序列化
        serializer.is_valid(raise_exception=True)  # 校验
        data = serializer.save()  # 保存

        if count == 0:  # 如果添加的是第一个地址，则设置为是默认地址
            user = User.objects.get(id=request.user.id)
            user.default_address_id = data.id
            user.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        """ 删除地址 """
        address = self.get_object()
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """ 修改标题 """
        address = self.get_object()
        serializer = TitleModelSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """ 设置默认地址 """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'ok'}, status=status.HTTP_200_OK)


class UserBrowserHistoryCreateAPIView(CreateAPIView):
    """ 用户商品浏览记录 """
    serializer_class = UserBrowserHistorySerializer
    permission_classes = [IsAuthenticated]
    queryset = ''

    def get(self, request):
        """ 查询商品浏览记录 """
        user = request.user  # 获取当前请求用户
        redis_conn = get_redis_connection('history')  # 连接redis数据库
        sku_ids = redis_conn.lrange('history_%s' % user.id, 0, -1)  # 获取redis中当前用户的浏览记录
        sku_list = []
        for sku_id in sku_ids:  # 循环获取列表中的数据
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)
        serializer = SKUModelSerializer(instance=sku_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class LoginObtainJSONWebToken(ObtainJSONWebToken):
    """ 自定义账号密码登录视图，实现购物车登录合并 """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)

            merge_cart_cookie_to_redis(request, user, response)

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
