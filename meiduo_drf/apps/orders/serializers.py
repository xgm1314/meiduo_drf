# _*_coding : uft-8 _*_
# @Time : 2023/7/6 12:55
# @Author : 
# @File : serializers
# @Project : meiduo_drf
from rest_framework import serializers

from django.utils.datetime_safe import datetime
from django.db import transaction

from django_redis import get_redis_connection

from decimal import Decimal

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods


class CartSKUModelSerializer(serializers.ModelSerializer):
    """ 订单中的商品序列化器 """
    count = serializers.IntegerField(label='商品的购买数量', min_value=1)

    class Meta:
        model = SKU
        fields = ['id', 'name', 'default_image', 'price', 'count']


class OrderSettlementSerializer(serializers.Serializer):
    """ 订单序列化器 """
    skus = CartSKUModelSerializer(many=True)
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)


class CommitOrderModelSerializer(serializers.ModelSerializer):
    """ 保存订单序列化器 """

    class Meta:
        model = OrderInfo
        fields = ['address', 'pay_method', 'order_id']
        extra_kwargs = {
            'order_id': {'read_only': True},
            'address': {'write_only': True},
            'pay_method': {'write_only': True}
        }

    def create(self, validated_data):
        """ 保存订单 """

        user = self.context['request'].user  # 获取登录用户信息

        order_id = datetime.now().strftime('%Y%m%d%H%M%S%f') + '%06d' % user.id  # 生成订单ID
        address = validated_data.get('address')
        pay_method = validated_data.get('pay_method')
        status = (OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                  if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY']
                  else OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

        with transaction.atomic():
            point = transaction.savepoint()  # 事务开启点

            # import time
            # time.sleep(5)

            try:
                orderInfo = OrderInfo.objects.create(  # 保存订单信息
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0.00'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=status
                )

                # 获取redis购物车内的最新信息
                redis_conn = get_redis_connection('cart')
                cart_dict_redis = redis_conn.hgetall('cart_%s' % user.id)
                selected_ids = redis_conn.smembers('selected_%s' % user.id)

                for sku_id_bytes in selected_ids:  # 遍历购物车勾选的商品,避免查询集的惰性
                    for i in range(10):  # 循环十次下单，不成功退出循环
                        sku = SKU.objects.get(id=sku_id_bytes)

                        buy_count = int(cart_dict_redis[sku_id_bytes])  # 获取购物车该商品购买的数量

                        old_stock = sku.stock  # 获取原有的sku库存
                        old_sales = sku.sales  # 获取原有的sku销量

                        if buy_count > old_stock:
                            raise serializers.ValidationError('该商品库存不足')

                        new_stock = old_stock - buy_count  # 库存减少
                        new_sales = old_sales + buy_count  # 售量增加

                        # sku.stock = new_stock  # sku表数据保存
                        # sku.sales = new_sales
                        # sku.save()
                        result = SKU.objects.filter(stock=old_stock, id=sku_id_bytes).update(stock=new_stock,
                                                                                             sales=new_sales)
                        if result == 0:
                            continue

                        spu = sku.spu  # spu表数据保存
                        spu.sales = spu.sales + buy_count
                        spu.save()

                        OrderGoods.objects.create(  # 订单商品信息
                            order=orderInfo,
                            sku=sku,
                            count=buy_count,
                            price=sku.price
                        )

                        orderInfo.total_count += buy_count  # 计算总件数
                        orderInfo.total_amount += (buy_count * sku.price)  # 计算商品总价格

                        break

                orderInfo.total_amount += orderInfo.freight  # 计算总价格
                orderInfo.save()
            except Exception:
                transaction.savepoint_rollback(point)  # 报异常就回滚
                raise serializers.ValidationError('该商品库存不足')
            else:
                transaction.savepoint_commit(point)  # 事务提交

        pipeline = redis_conn.pipeline()  # 连接redis，清空购物车商品
        pipeline.hdel('carts_%s' % user.id, *selected_ids)
        pipeline.srem('selected_%s' % user.id, *selected_ids)
        pipeline.execute()

        return orderInfo
