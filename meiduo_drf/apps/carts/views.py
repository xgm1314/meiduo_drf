import base64
import pickle

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django_redis import get_redis_connection

from .serializers import CartsSerializer, SKUCartsModelSerializer, CartDeleteSerializer, CartSelectedAllSerializer
from apps.goods.models import SKU


# Create your views here.
class CartsAPIView(APIView):
    """ 购物车增删改查 """

    def perform_authentication(self, request):
        """ 重写此方法，直接pass，让JWT认证成为懒加载 可以延后认证 延后到第一次通过request.user或request.auth才去认证   """
        pass

    def post(self, request):
        """ 新增购物车 """
        """
        测试数据
        {
        "sku_id": 1,
        "count":2,
        "selected":"False"
        }
        保存的数据类型
        {
        "sku_id":{"count":1,"selected":True},
        "sku_id":{"count":1,"selected":True}
        }
        """
        serializer = CartsSerializer(data=request.data)  # 创建序列化器进行反序列化
        serializer.is_valid(raise_exception=True)  # 校验
        # 获取校验后的数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        response = Response(data=serializer.data, status=status.HTTP_201_CREATED)  # 创建响应对象

        try:  # 尝试获取user的值
            user = request.user
        except:
            user = None

        if user and user.is_authenticated:  # 判断是否是登录用户  is_authenticated:判断用户是否通过认证
            redis_conn = get_redis_connection('cart')
            pipeline = redis_conn.pipeline()
            pipeline.hincrby('cart_%s' % user.id, sku_id, count)  # 如果要添加的sku_id在hash字典中不存在，则是新增；如果存在就会自动做增量计算再存储
            if selected:  # 判断是否勾选
                pipeline.sadd('selected_%s' % user.id, sku_id)
            pipeline.execute()  # 执行管道
            # return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        else:  # 未登录的用户
            cart_str = request.COOKIES.get('cart')  # 获取cookies购物车数据
            if cart_str:  # 判断cookies购物车是否有商品
                cart_str_bytes = cart_str.encode()  # 将字符串转化为bytes类型数据
                cart_bytes = base64.b64decode(cart_str_bytes)  # 将bytes的字符串转化为bytes类型
                cart_dict = pickle.loads(cart_bytes)  # 将bytes类型转化为字典
            else:
                cart_dict = {}

            if sku_id in cart_dict:  # 如果购物车中有添加的商品，则做累加计算
                count_old = cart_dict[sku_id]['count']
                count += count_old

            cart_dict[sku_id] = {  # 将商品添加到购物车
                'count': count,
                'selected': selected
            }
            cart_bytes = pickle.dumps(cart_dict)  # 将字典转化为bytes数据类型
            cart_str_bytes = base64.b64encode(cart_bytes)  # 将bytes类型转化为bytes字符串
            cart_str = cart_str_bytes.decode()  # 将bytes字符串转化为字符串

            # response = Response(data=serializer.data, status=status.HTTP_201_CREATED)  # 创建响应对象
            response.set_cookie('cart', cart_str, expires=3600 * 24)  # 设置cookies 一天有效
        return response

    def get(self, request):
        """ 查询所有 """
        try:
            user = request.user
        except:
            user = None

        if user and user.is_authenticated:  # 登录用户
            redis_conn = get_redis_connection('cart')
            cart_redis_dict = redis_conn.hgetall('cart_%s' % user.id)  # 获取hash数据
            selecteds = redis_conn.smembers('selected_%s' % user.id)  # 获取集合数据

            # 将redis数据转化为cookies类型数据
            cart_dict = {}
            for sku_id_bytes, count_bytes in cart_redis_dict.items():
                cart_dict[int(sku_id_bytes)] = {
                    'count': int(count_bytes),
                    'selected': sku_id_bytes in selecteds
                }

        else:  # 未登录用户
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_bytes)
            else:
                return Response({'message': '购物车数据不存在'}, status=status.HTTP_400_BAD_REQUEST)

        sku_ids = cart_dict.keys()  # 根据sku_id查询sku模型
        skus = SKU.objects.filter(id__in=sku_ids)  # 查询出所有sku模型返回查询集
        for sku in skus:  # 给模型定义属性
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']
        serializer = SKUCartsModelSerializer(instance=skus, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """ 修改 """
        """
        测试数据
        {
        "sku_id": 1,
        "count":2,
        "selected":"False"
        }
        """
        serializer = CartsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        try:
            user = request.user
        except:
            user = None

        # try:
        #     count = int(count)
        # except:
        #     count = 1

        response = Response(serializer.data, status=status.HTTP_200_OK)

        if user and user.is_authenticated:  # 登录用户修改redis
            redis_conn = get_redis_connection('cart')
            pipeline = redis_conn.pipeline()
            pipeline.hset('cart_%s' % user.id, sku_id, count)  # 设置hash值
            if selected:  # 设置集合
                pipeline.sadd('selected_%s' % user.id, sku_id)
            else:
                pipeline.srem('selected_%s' % user.id, sku_id)
            pipeline.execute()

            # return Response(data=serializer.data,status=status.HTTP_200_OK)

        else:  # 未登录用户修改cookies
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({'message': '购物车商品不存在'}, status=status.HTTP_400_BAD_REQUEST)
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # response = Response(serializer.data, status=status.HTTP_200_OK)
            response.set_cookie('cart', cart_str, expires=3600 * 24)
        return response

    def delete(self, request):
        """ 删除 """
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        # sku_id = 11  # 测试

        try:
            user = request.user
        except:
            user = None
        response = Response(status=status.HTTP_204_NO_CONTENT)
        if user and user.is_authenticated:  # 登录用户
            redid_conn = get_redis_connection('cart')
            pipeline = redid_conn.pipeline()
            pipeline.hdel('cart_%s' % user.id, sku_id)  # 删除hash数据
            pipeline.srem('selected_%s' % user.id, sku_id)  # 删除集合数据
            pipeline.execute()

        else:  # 未登录用户
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({'message': '购物车商品不存在'}, status=status.HTTP_400_BAD_REQUEST)

            if sku_id in cart_dict:  # 如果要删除的商品id在购物车内，则删除
                del cart_dict[sku_id]

            if len(cart_dict.keys()):  # 如果还有商品，则将字典转化为字符串
                cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie('cart', cart_str, expires=3600 * 24)
            else:  # 如果商品不存在，则将cookies删除
                response.delete_cookie('cart')
        return response


class CartSelectedAllAPIView(APIView):
    """ 购物车全选 """

    def perform_authentication(self, request):
        """ 重写此方法，直接pass，让JWT认证成为懒加载 可以延后认证 延后到第一次通过request.user或request.auth才去认证   """
        pass

    def put(self, request):
        serializer = CartSelectedAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data.get('selected')

        try:
            user = request.user
        except:
            user = None

        response = Response(data=serializer.data, status=status.HTTP_200_OK)

        if user and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            cart_redis_dict = redis_conn.hgetall('cart_%s' % user.id)  # 获取hash字典中的数据
            sku_id = cart_redis_dict.keys()  # 获取hash字典中所有的key

            if selected:  # 传入的是True
                redis_conn.sadd('selected_%s' % user.id, *sku_id)
            else:  # 传入的是False
                redis_conn.srem('selected_%s' % user.id, *sku_id)

        else:
            cart_str = request.COOKIES.get('cart')

            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return Response({'message': '商品信息不存在'}, status=status.HTTP_400_BAD_REQUEST)

            for sku_id in cart_dict:
                cart_dict[sku_id]['selected'] = selected

            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cart_str, expires=3600 * 24)
        return response
