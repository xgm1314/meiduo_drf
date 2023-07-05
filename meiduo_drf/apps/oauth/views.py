from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from QQLoginTool.QQtool import OAuthQQ

from .models import OauthQQUser
from .serializers import OauthQQSerializer
from apps.carts.utils import merge_cart_cookie_to_redis

import logging

logger = logging.getLogger('django')


# Create your views here.
class QQOauthURLAPIView(APIView):
    """ 拼接QQ登录的url """

    def get(self, request):
        next = request.query_params.get('next') or '/'  # 提取前端的next对象，用作回调用

        # # QQ登录参数
        # # 我们申请的 客户端id
        # QQ_CLIENT_ID = '101474184'
        # # 我们申请的 客户端秘钥
        # QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
        # # 我们申请时添加的: 登录成功后回调的路径
        # QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)  # 利用QQ登录SDK
        login_url = oauth.get_qq_url()  # 创建QQ登录对象
        return Response({'login_url': login_url})
        # http://www.meiduo.site:8080/oauth_callback.html?code=D68272402EFC955CC843F43CA7A80C56&state=%2F


class OauthQQAPIView(APIView):

    def get(self, request):
        """ QQ用户回调 """
        code = request.query_params.get('code')
        # code = 'E7EAE71D3BF32EBFB31623BCB7F2380E'
        if not code:
            return Response({'message': '参数缺失'}, status=status.HTTP_400_BAD_REQUEST)
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI
        )
        try:
            access_token = oauth.get_access_token(code)  # 获取token
            openid = oauth.get_open_id(access_token)  # 获取openid
        except Exception as e:
            logger.info(e)  # 打印错误信息
            return Response({'message': 'qq服务器异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            oauth_qq = OauthQQUser.objects.get(openid=openid)
        except OauthQQUser.DoesNotExist:
            from .utils import generic_openid
            access_token_openid = generic_openid(openid)  # 将openid加密，响应给前端数据
            return Response({'access_token': access_token_openid})

        else:
            user = oauth_qq.user  # 获取登录用户的信息

            # 生成token数据
            from rest_framework_jwt.settings import api_settings
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # 生成载荷信息(payload),根据user的信息生成一个payload
            payload = jwt_payload_handler(user)
            # 根据payload和secret_key，采用HS256，生成token.
            token = jwt_encode_handler(payload)
            response=Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })

            merge_cart_cookie_to_redis(request,user,response)

            return response

    def post(self, request):
        """ openid绑定用户接口 """
        serializer = OauthQQSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # 生成token数据
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 生成载荷信息(payload),根据user的信息生成一个payload
        payload = jwt_payload_handler(user)
        # 根据payload和secret_key，采用HS256，生成token.
        token = jwt_encode_handler(payload)

        response = Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })

        merge_cart_cookie_to_redis(request, user, response)

        return response