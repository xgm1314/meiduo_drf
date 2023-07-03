# _*_coding : uft-8 _*_
# @Time : 2023/6/15 21:24
# @Author : 
# @File : serializers
# @Project : meiduo_drf
from rest_framework import serializers
from .models import User, Address
import re
from django_redis import get_redis_connection
from django.conf import settings

from ..areas.models import Area
from ..goods.models import SKU


class CreateUserSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password2 = serializers.CharField(label='确认密码', write_only=True, max_length=32)
    sms_code = serializers.CharField(label='验证码', write_only=True, max_length=4)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='token', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow', 'token']
        extra_kwargs = {  # 修改字段
            'username': {
                'min_length': 2,
                'max_length': 20,
                'error_messages': {  # 自定义校验出错后的错误信息提示
                    'min_length': '用户名字不能少于2个字符',
                    'max_length': '用户名字不能大余20个字符',
                }
            },
            'password': {
                'min_length': 6,
                'max_length': 32,
                "write_only": True,
                'error_messages': {  # 自定义校验出错后的错误信息提示
                    'min_length': '密码不能少于6个字符',
                    'max_length': '密码不能大余32个字符',
                }
            },
        }

    def validate_username(self, value):
        # 验证是否以字母开头
        if not value[0].isalpha():
            raise serializers.ValidationError('名字以字母开始')
        return value

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

        # 生成token数据
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 生成载荷信息(payload),根据user的信息生成一个payload
        payload = jwt_payload_handler(user)
        # 根据payload和secret_key，采用HS256，生成token.
        token = jwt_encode_handler(payload)
        # print(token)
        # 将token信息传递给用户信息
        user.token = token

        return user


class UserRetrieveModelSerializer(serializers.ModelSerializer):
    """ 详情用户展示序列化器 """

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']
        extra_kwargs = {
            'email': {
                'required': True
            }
        }


class UserUpdateModelSerializer(serializers.ModelSerializer):
    """ 修改email序列化器 """

    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        # 重写修改方法，方便发送激活邮箱
        instance.email = validated_data.get('email')
        instance.save()

        # 发送邮件
        email = instance.email
        subject = 'fyq_love_xgm'  # 主题
        message = 'fyq_love_xgm'  # 邮件内容
        from_email = settings.EMAIL_HOST_USER  # 发件人
        recipient_list = [email]  # 收件人列表

        # 生成激活链接
        # # 方式一：传参
        # from apps.users.utils import generic_openid
        # token_id = generic_openid(instance.id)

        # 方式二：利用模型类
        token_id = instance.generate_email_verify_url()

        verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token=%s" % token_id
        # verify_url = "http://127.0.0.1:8001/email/verification/?token=%s" % token_id # 测试用

        # 4.2 组织我们的激活邮件
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        # 使用celery异步发送邮件
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message)

        return instance


class UserAddressModelSerializer(serializers.ModelSerializer):
    """ 用户地址序列化器 """

    # province = serializers.StringRelatedField(read_only=True)
    # city = serializers.StringRelatedField(read_only=True)
    # district = serializers.StringRelatedField(read_only=True)
    # # province_id = serializers.IntegerField(label='省ID', read_only=True)
    # city_id = serializers.IntegerField(label='市ID', read_only=True)
    # district_id = serializers.IntegerField(label='区县ID', read_only=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """ 验证手机号 """
        if not re.match('1[345789]\d{9}', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value

    def create(self, validated_data):
        user = self.context['request'].user  # 获取用户模型对象
        validated_data['user'] = user  # 将用户模型对象保存到字典中
        return Address.objects.create(**validated_data)


class TitleModelSerializer(serializers.ModelSerializer):
    """ 标题修改序列化器 """

    class Meta:
        model = Address
        fields = ['title']


class UserBrowserHistorySerializer(serializers.Serializer):
    """ 保存商品历史浏览记录序列化器 """
    sku_id = serializers.IntegerField(label='商品sku_id', min_value=1)

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品信息不存在')
        return value

    def create(self, validated_data):
        sku_id = validated_data.get('sku_id')
        sku = self.context['request'].user  # 获取当前用户的模型对象
        redis_conn = get_redis_connection('history')  # 连接数据库
        pipeline = redis_conn.pipeline()  # 创建redis管道
        pipeline.lrem('history_%s' % sku.id, 0, sku_id)  # 去重
        pipeline.lpush('history_%s' % sku.id, sku_id)  # 添加到表头
        pipeline.ltrim('history_%s' % sku.id, 0, 4)  # 截取前五个元素
        pipeline.execute()  # 执行管道
        return validated_data


class SKUModelSerializer(serializers.ModelSerializer):
    """ 用户浏览记录序列化器 """

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image', 'comments']
