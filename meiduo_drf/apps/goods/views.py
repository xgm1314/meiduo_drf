from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response

from apps.goods.models import SKU, GoodsCategory
from apps.goods.serializers import SKUModelSerializer, CategoryModelSerializer


# Create your views here.
class SKUListAPIView(ListAPIView):
    """ 商品列表数据查询 """

    filter_backends = [OrderingFilter]  # 指定过滤后端为排序过滤
    ordering_filter = ['create_time', 'price', 'sales']

    serializer_class = SKUModelSerializer

    def get_queryset(self):
        """如果当前视图中没有定义get/post方法，那么就没法定义一个参数用来接收正则组提取出来的url路径参数，可以利用视图对象的args或者kwargs属性去获取"""
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(is_launched=True, category_id=category_id)


class CategoryGenericAPIView(GenericAPIView):
    """ 商品列表面包屑展示 """
    queryset = GoodsCategory.objects.all()  # 查询集
    serializer_class = CategoryModelSerializer  # 序列化器

    def get(self, request, pk=None):
        # ret = dict(
        #     cat1='',
        #     cat2='',
        #     cat3=''
        # )
        ret = {
            'cat1': '',
            'cat2': '',
            'cat3': ''
        }
        category = self.get_object()
        if category.parent is None:  # 一级标题
            ret['cat1'] = self.serializer_class(category).data
        elif category.subs.count() == 0:  # 三级标题
            ret['cat3'] = self.serializer_class(category).data
            ret['cat2'] = self.serializer_class(category.parent).data
            ret['cat1'] = self.serializer_class(category.parent.parent).data
        else:  # 二级标题
            ret['cat2'] = self.serializer_class(category).data
            ret['cat1'] = self.serializer_class(category.parent).data
        return Response(ret)
