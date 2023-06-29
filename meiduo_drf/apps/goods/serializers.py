# _*_coding : uft-8 _*_
# @Time : 2023/6/28 20:41
# @Author : 
# @File : serializers
# @Project : meiduo_drf
from rest_framework import serializers

from .models import SKU, GoodsCategory


class SKUModelSerializer(serializers.ModelSerializer):
    """ sku序列化器 """

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'comments', 'default_image', 'sales', 'create_time']


class CategoryModelSerializer(serializers.ModelSerializer):
    """ 商品类别序列化器 """

    class Meta:
        model = GoodsCategory
        fields = ['name']
