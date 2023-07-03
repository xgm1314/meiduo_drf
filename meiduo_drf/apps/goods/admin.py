from django.contrib import admin

from . import models
from celery_tasks.html.tasks import generate_static_list_search_html, generate_static_sku_detail_html


class GoodsCategoryAdmin(admin.ModelAdmin):
    """ 商品类别模型站点管理 """

    def save_model(self, request, obj, form, change):
        """
        当点击admin中的保存按钮时会来调用此方法
        Args:
            request: 保存时本次请求对象
            obj: 本次要保存的模型对象
            form: admin中表单
            change: 是否更改    True
        """
        obj.save()
        # 重新生成新的列表静态界面
        generate_static_list_search_html.delay()

    def delete_model(self, request, obj):
        """ 当点击admin中被删除按钮时会来调用次方法 """
        obj.delete()
        # 重新生成新的列表静态界面
        generate_static_list_search_html.delay()


class SKUAdmin(admin.ModelAdmin):
    """ 商品类别模型站点管理类 """

    def save_model(self, request, obj, form, change):
        """

        Args:
            request: 保存时本次请求对象
            obj: 本次要保存的模型对象
            form: admin中表单
            change: 是否更改    True

        Returns:

        """
        obj.save()
        generate_static_sku_detail_html.delay(obj.id)  # 启用celery异步生成详情界面

    def delete_model(self, request, obj):
        """

        Args:
            request:
            obj:

        Returns:

        """
        obj.delete()
        generate_static_sku_detail_html.delay(obj.id)


@admin.register(models.SKUImage)
class SKUImageAdmin(admin.ModelAdmin):
    """ 商品图片站点管理类 """

    def save_model(self, request, obj, form, change):
        """

        Args:
            request:
            obj:图片模型对象
            form:
            change:

        Returns:

        """
        obj.save()
        sku = obj.sku  # 通过外键获取图片模型对象所关联的sku模型的id
        if not sku.default_image:
            sku.default_image = obj.image  # obj.image.url图片路径  obj.image图片
            sku.save()
        generate_static_sku_detail_html.delay(sku.id)

    def delete_model(self, request, obj):
        obj.delete()
        sku = obj.sku
        generate_static_sku_detail_html.delay(sku.id)


# Register your models here.
admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannelGroup)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Brand)
admin.site.register(models.SPU)
admin.site.register(models.SKU, SKUAdmin)
# admin.site.register(models.SKUImage, SKUImageAdmin)   等同于 @admin.register(models.SKUImage)
admin.site.register(models.SPUSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKUSpecification)
admin.site.register(models.GoodsVisitCount)
