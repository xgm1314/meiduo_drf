# _*_coding : uft-8 _*_
# @Time : 2023/6/20 16:39
# @Author : 
# @File : serializers
# @Project : meiduo_drf
from rest_framework import serializers

from django_redis import get_redis_connection

from .utils import check_access_token
from apps.users.models import User
from apps.oauth.models import OauthQQUser


class OauthQQSerializer(serializers.Serializer):
    """ openid绑定用户序列化器 """
    access_token = serializers.CharField(label='openid')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=32, min_length=6)
    sms_code = serializers.CharField(label='验证码', max_length=6)

    def validate(self, attrs):
        # 验证openid
        access_token = attrs.pop('access_token')
        openid = check_access_token(access_token)
        if openid is None:
            raise serializers.ValidationError('openid已过期')
        attrs['openid'] = openid  # 将openid数据添加到attrs字典中
        # 验证验证码
        redis_conn = get_redis_connection('sms_codes')
        mobile = attrs.get('mobile')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None or attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('验证码错误')
        # 验证手机号
        try:
            users = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            if users.check_password(attrs['password']) is False:
                raise serializers.ValidationError('密码错误')
            else:
                attrs['user'] = users
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        if user is None:
            user = User.objects.create(  # 如果用户不存在，则创建用户
                username='MD_%s' % validated_data.get('mobile'),  # 名字第一个为字母
                mobile=validated_data.get('mobile')
            )
            user.set_password(validated_data.get('password'))
            user.save()

        OauthQQUser.objects.create(
            openid=validated_data.get('openid'),
            user=user
        )
        return user
