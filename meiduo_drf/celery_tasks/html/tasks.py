# _*_coding : uft-8 _*_
# @Time : 2023/6/28 15:59
# @Author : 
# @File : tasks
# @Project : meiduo_drf
import os
from django.template import loader
from django.conf import settings

from apps.goods.models import SKU
from celery_tasks.main import celery_app
from apps.goods.utils import get_categories


@celery_app.task(name='generate_static_list_search_html')
def generate_static_list_search_html():
    """ 生成静态文件的商品列表和搜索结果页html文件 """
    categories = get_categories()  # 商品分类菜单
    context = {  # 渲染模板，生成静态html文件
        'categories': categories
    }
    template = loader.get_template('list.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'list.html')
    with open(file_path, 'w') as f:
        f.write(html_text)


@celery_app.task(name='generate_static_sku_detail_html')
def generate_static_sku_detail_html(sku_id):
    """
    生成静态商品详情页面
    Args:
        sku_id:商品ksu id

    Returns:

    """
    categories = get_categories()  # 商品分类菜单

    sku = SKU.objects.get(id=sku_id)  # 获取当前sku的信息
    sku.images = sku.skuimage_set.all()

    goods = sku.category  # 面包屑导航信息的频道
    # goods.channel = goods.category1.cat1_spu.all()[0]
    goods.channel = goods.cat1_spu.all()

    # sku_specs = sku.skuspecification_set.order_by('spec_id')  # 构建当前商品规格键
    # sku_specs = sku.specs.order_by('spec_id')  # 构建当前商品规格键
    sku_specs = sku.specs.order_by('spec_id')  # 构建当前商品规格键
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)
    skus = goods.sku_set.all()  # 获取当前商品的所有SKU

    spec_sku_map = {}
    for s in skus:  # 获取sku的规格参数
        # s_specs = s.skuimage_set.order_by('spec_id')
        s_specs = s.specs.order_by('spec_id')
        key = []  # 用于形成规格参数 sku 字典的键
        for spec in s_specs:
            key.append(spec.option.id)
        spec_sku_map[tuple(key)] = s.id  # 向规格参数 sku 字典添加记录

    # specs = goods.goodsspecification_set.all()
    specs = goods.goodschannel_set.order_by('id')

    if len(sku_key) < len(specs):  # 如果当前sku信息不完整，则退出
        return
    for index, spec in enumerate(specs):
        key = sku_key[:]  # 复制当前sku的规格键
        options = spec.specificationoption_set.all()  # 该规格的选项
        for option in options:  # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))
        spec.options = options

    context = {  # 渲染模板，生成静态html文件
        'categories': categories,
        'goods': goods,
        'specs': specs,
        'sku': sku
    }
    template = loader.get_template('detail.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/' + str(sku_id) + '.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
