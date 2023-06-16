from random import randint
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django_redis import get_redis_connection

from libs.yuntongxun.sms import CCP

from . import constants
from celery_tasks.sms.tasks import send_sms_code

# Create your views here.

logger = logging.getLogger('django')


class SMSCodeView(APIView):
    """ 短信验证码 """

    def get(self, request, mobile):
        redis_conn = get_redis_connection('sms_codes')  # 连接数据库

        send_flag = redis_conn.get('send_flag_%s' % mobile)  # 判断是否有已发送短信的标记
        if send_flag:
            return Response({'message': '发送短信过于频繁'}, status=status.HTTP_400_BAD_REQUEST)

        # 随机生成4位随机数
        sms_code = '%04d' % randint(0, 9999)
        logger.info(sms_code)

        pl = redis_conn.pipeline()  # 创建管道
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)  # 将验证码保存到redis库中
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)  # 将验证码保存到redis库中
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)  # 标记该手机号是否已发送短信
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)  # 标记该手机号是否已发送短信
        pl.execute()  # 管道提交(管道执行)

        # 发送短信验证码
        # from meiduo_drf.meiduo_drf.libs.yuntongxun.sms import CCP
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
        # from time import sleep
        # sleep(5)
        send_sms_code.delay(mobile, sms_code)  # 触发异步任务

        return Response({'message': 'ok'})
