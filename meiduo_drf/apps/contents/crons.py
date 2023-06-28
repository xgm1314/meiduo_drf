# _*_coding : uft-8 _*_
# @Time : 2023/6/27 16:35
# @Author : 
# @File : crons
# @Project : meiduo_drf
from collections import OrderedDict
from django.conf import settings
from django.template import loader
import os
import time

from apps.goods.models import GoodsChannel, GoodsChannelGroup

from .models import ContentCategory


def generate_static_index_html():
    """ 生成静态的主页html文件 """
    print('%s:generate_static_index_html' % time.ctime())
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

    # 广告内容
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 渲染模板
    context = {
        'categories': categories,  # 商品频道数据
        'contents': contents  # 广告数据
    }
    # 加载模板文件
    template = loader.get_template('index.html')
    # 渲染模板
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
