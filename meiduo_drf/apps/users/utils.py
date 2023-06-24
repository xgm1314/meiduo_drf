# _*_coding : uft-8 _*_
# @Time : 2023/6/19 15:39
# @Author : 
# @File : utils
# @Project : meiduo_drf
import re

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    重写JWT登录视图的构造响应数据函数
    @param token:
    @param user:
    @param request:
    @return:返回token和追加的user_id,username数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """
    通过传入的数据动态获取user模型对象
    @param account:前端传入的数据(手机号或者用户名)
    @return:返回user或者None
    """
    try:
        if re.match(r'^1[3-9]\d{9}', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None  # 没有查询到返回None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """ 修改Django的认证类，实现多账号登录 """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)  # 获取user
        if user and user.check_password(password):  # 判断当前前端传入的密码是否正确
            return user  # 返回user


from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData


def generic_openid(openid):
    """ 数据加密 """
    openid_serializer = TJWSSerializer(secret_key=settings.SECRET_KEY, expires_in=60 * 60 * 24)
    access_token = openid_serializer.dumps({'openid': openid})
    return access_token.decode()


def check_access_token(token):
    """ 解密数据 """
    openid_serializer = TJWSSerializer(secret_key=settings.SECRET_KEY, expires_in=60 * 60 * 24)
    try:
        access_token = openid_serializer.loads(token)
    except BadData:
        return None
    else:
        return access_token.get('openid')
