# _*_coding : uft-8 _*_
# @Time : 2023/6/20 15:38
# @Author : 
# @File : utils
# @Project : meiduo_drf
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData


def generic_openid(openid):
    """ 数据加密 """
    openid_serializer = TJWSSerializer(secret_key=settings.SECRET_KEY, expires_in=60 * 60)
    access_token = openid_serializer.dumps({'openid': openid})
    return access_token.decode()


def check_access_token(token):
    """ 解密数据 """
    openid_serializer = TJWSSerializer(secret_key=settings.SECRET_KEY, expires_in=60 * 60)
    try:
        access_token = openid_serializer.loads(token)
    except BadData:
        return None
    else:
        return access_token.get('openid')
