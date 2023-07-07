from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView

from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.serializers import OrderSettlementSerializer, CommitOrderModelSerializer

from decimal import Decimal


class OrderSettlementAPIView(APIView):
    """ 去结算 """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        redis_conn = get_redis_connection('cart')  # 连接redis
        user = request.user  # 获取user对象
        cart_dict_redis = redis_conn.hgetall('cart_%s' % user.id)  # 或许hash值
        selected_redis = redis_conn.smembers('selected_%s' % user.id)  # 或许集合数据
        cart_cart = {}
        for sku_id_bytes in selected_redis:
            cart_cart[int(sku_id_bytes)] = int(cart_dict_redis[sku_id_bytes])

        skus = SKU.objects.filter(id__in=selected_redis)  # 把勾选的商品sku模型获取到

        for sku in skus:  # 遍历勾选的模型对象，给count属性赋值
            sku.count = cart_cart[sku.id]

        freight = Decimal('10.00')  # 运费

        data_dict = {'freight': freight, 'skus': skus}
        serializer = OrderSettlementSerializer(data_dict)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CommitOrderCreateAPIView(CreateAPIView):
    """ 订单提交 """
    permission_classes = [IsAuthenticated]
    serializer_class = CommitOrderModelSerializer
    queryset = ''
