# _*_coding : uft-8 _*_
# @Time : 2023/6/15 21:24
# @Author : 
# @File : serializers
# @Project : meiduo_drf
from rest_framework import serializers
from .models import User
import re
from django_redis import get_redis_connection


class CreateUserSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password2 = serializers.CharField(label='确认密码', write_only=True, max_length=32)
    sms_code = serializers.CharField(label='验证码', write_only=True, max_length=4)
    allow = serializers.CharField(label='同意协议', write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
        extra_kwargs = {  # 修改字段
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {  # 自定义校验出错后的错误信息提示
                    'min_length': '用户名字不能少于5个字符',
                    'max_length': '用户名字不能大余20个字符',
                }
            },
            'password': {
                'min_length': 16,
                'max_length': 32,
                'error_messages': {  # 自定义校验出错后的错误信息提示
                    'min_length': '密码不能少于16个字符',
                    'max_length': '密码不能大余32个字符',
                }
            },
        }

    def validate_mobile(self, value):
        """ 验证手机号 """
        result = re.match('1[345789]\d{9}', value)
        if not result:
            raise serializers.ValidationError('手机号格式不正确')
        return value

    def validate_allow(self, value):
        """ 验证是否同意协议 """
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        """ 校验密码是否相同 """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 校正验证码
        redis_conn = get_redis_connection('sms_codes')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('验证码错误')
        if attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('验证码错误')

        return attrs

    def create(self, validated_data):
        """ 重写保存 """
        # 删除不需要保存的字段
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        password = validated_data.pop('password')  # 取出密码
        user = User(**validated_data)  # 创建用户模型,给模型中的username和mobile属性赋值
        user.set_password(password)  # 密码加密之后保存
        user.save()  # 保存
        return user
