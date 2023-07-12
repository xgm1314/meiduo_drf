from django.shortcuts import render
from django.conf import settings

import os

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from alipay import AliPay

from apps.orders.models import OrderInfo
from apps.payment.models import Payment


# Create your views here.
class PaymentAPIView(APIView):
    """ 生成支付连接 """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        user = request.user
        try:
            order_model = OrderInfo.objects.get(order_id=order_id, user=user,
                                                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单有误'}, status=status.HTTP_400_BAD_REQUEST)
        # 创建alipay SDK中需要提供的支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # alipay的id
            app_notify_url=None,  # 默认回调的url
            # 指定应用自己的私钥文件绝对路径
            app_private_key_string=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key/app_private_key.pem'),
            # 指定支付宝公钥文件绝对路径
            alipay_public_key_string=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  'key/alipay_public_key.pem'),
            sign_type='RSA',  # 加密方式RSA2或者RSA
            debug=settings.ALIPAY_DEBUG,  # 默认是False
        )

        # 调用SDK的方法得到支付连接后面的查询参数
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 支付的订单编号
            total_amount=str(order_model.total_amount),  # 支付的总金额，需要将Decimal转换为str或者浮点数
            subject='美多商城%s' % order_id,  # 标题
            return_url=settings.ALIPAY_RETURN_URL
        )

        # 拼接支付连接
        alipay_url = settings.ALIPAY_URL + '?' + order_string

        return Response({'alipay_url': alipay_url})


class PaymentStatusAPIView(APIView):
    """ 修改订单状态，保存支付宝交易号 """

    def put(self, request):
        query_dict = request.query_params  # 获取前端传入的数据
        data = query_dict.dict()  # 将数据转化为字典类型
        sign = data.pop('sign')  # 支付宝私钥加密数据
        # 创建alipay SDK中需要提供的支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # alipay的id
            app_notify_url=None,  # 默认回调的url
            # 指定应用自己的私钥文件绝对路径
            app_private_key_string=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key/app_private_key.pem'),
            # 指定支付宝公钥文件绝对路径
            alipay_public_key_string=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  'key/alipay_public_key.pem'),
            sign_type='RSA',  # 加密方式RSA2或者RSA
            debug=settings.ALIPAY_DEBUG,  # 默认是False
        )
        if alipay.verify(data, sign):  # 用verify方法校验数据是否是支付宝传出来的数据
            order_id = data.get('out_trade_no')  # 美多订单编号
            trade_no = data.get('trade_no')  # 支付宝交易号
            Payment.objects.create(  # 将订单编号和交易号保存到数据库中
                order_id=order_id,
                trade_id=trade_no
            )
            # 修改订单状态
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
        else:
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'trade_id': trade_no})
