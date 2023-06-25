# _*_coding : uft-8 _*_
# @Time : 2023/6/24 20:40
# @Author : 
# @File : serializers
# @Project : meiduo_drf
from rest_framework import serializers

from .models import Area

"""
查询所有省时用的是AreasModelSerializer

在查询单一省时，SubsModelSerializer代表单个省，AreasModelSerializer代表省下面的所有市
在查询单一市时，SubsModelSerializer代表单个市，AreasModelSerializer代表市下面的所有区县
"""


class AreasModelSerializer(serializers.ModelSerializer):
    """ 省序列化器 """

    class Meta:
        model = Area
        fields = ['id', 'name']


class SubsModelSerializer(serializers.ModelSerializer):
    """ 详情视图序列化器 """
    subs = AreasModelSerializer(many=True)

    # subs = serializers.PrimaryKeyRelatedField()  # 只会序列化出id
    # subs = serializers.StringRelatedField()  # 序列化时模型中str方法返回值

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
