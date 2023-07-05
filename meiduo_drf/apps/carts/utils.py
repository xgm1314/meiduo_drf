# _*_coding : uft-8 _*_
# @Time : 2023/7/5 15:26
# @Author : 
# @File : utils
# @Project : meiduo_drf

import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    """
    cookies购物车合并到redis购物车
    Args:
        request: 传入的请求对象
        user:传入的用户对象
        response:传入的响应对象，用作删除cookies信息

    Returns:response 将响应对象返回

    """
    cart_str = request.COOKIES.get('cart')  # 获取cookies信息

    if cart_str is None:  # cookies信息不存在直接返回
        return

    else:
        cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

        redis_conn = get_redis_connection('cart')
        pipeline = redis_conn.pipeline()

        for sku_id in cart_dict.keys():  # 遍历字典的商品信息，获取sku
            pipeline.hset('cart_%s' % user.id, sku_id,
                          cart_dict[sku_id]['count'])  # 将商品的sku添加到hash内(如果redis中有该商品sku，则用cookies的count值覆盖redis内的hash值)

            if cart_dict[sku_id]['selected']:  # 判断传入的商品信息是否勾选(redis和cookies任意一方勾选则为勾选)
                pipeline.sadd('selected_%s' % user.id, sku_id)

        pipeline.execute()

        response.delete_cookie('cart')
        return response
