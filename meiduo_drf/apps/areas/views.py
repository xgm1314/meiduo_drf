from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from apps.areas.models import Area
from apps.areas.serializers import AreasModelSerializer, SubsModelSerializer


# Create your views here.
# class AreasListAPIView(APIView):
#     """ 查询所有省 """
#
#     def get(self, request):
#         province = Area.objects.filter(parent=None)
#         serializer = AreasModelSerializer(instance=province, many=True)
#         return Response(data=serializer.data, status=status.HTTP_200_OK)
class AreasListAPIView(ListAPIView):
    """ 查询所有省 """
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreasModelSerializer


# class AreasDetailAPIView(APIView):
#     """ 查询单一省或市 """
#
#     def get(self, request, pk):
#         try:
#             sub = Area.objects.get(id=pk)  # 根据pk查询出指定的省或市
#         except Area.DoesNotExist:
#             return Response({'message': '查询的数据不存在'}, status=status.HTTP_400_BAD_REQUEST)
#         serializer = SubsModelSerializer(instance=sub)
#         return Response(data=serializer.data, status=status.HTTP_200_OK)
class AreasDetailAPIView(RetrieveAPIView):
    """ 查询单一省或市 """
    queryset = Area.objects.all()
    serializer_class = SubsModelSerializer


class AreasReadOnlyModelViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """ 查询视图集 """
    # pagination_class = None  # 禁用分页,不可用

    # CacheResponseMixin设置缓存
    def get_queryset(self):
        # 重写查询集方法
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        # 重写序列化器方法
        if self.action == 'list':
            return AreasModelSerializer
        else:
            return SubsModelSerializer
