# _*_coding : uft-8 _*_
# @Time : 2023/6/28 15:54
# @Author : 
# @File : utils
# @Project : meiduo_drf
from collections import OrderedDict
from .models import GoodsChannel


def get_categories():
    """
    获取商城商品分类菜单
    Returns:分类菜单字典

    """
    categories = OrderedDict()  # 创建有序字典
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        group_id = channel.group_id  # 当前组
        if group_id not in categories:
            categories[group_id] = {'channel': [], 'sequence': []}
        cat1 = channel.category  # 当前频道的类别
        # 追加当前频道组
        categories[group_id]['channel'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 构建当前类别的子类别
        for cat2 in cat1.goodschannel_set.all():
            categories[group_id]['sequence'].append(cat2)
    return categories
