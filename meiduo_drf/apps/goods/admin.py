from django.contrib import admin

from . import models
from celery_tasks.html.tasks import generate_static_list_search_html


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


# Register your models here.
admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannelGroup)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Brand)
admin.site.register(models.SPU)
admin.site.register(models.SKU)
admin.site.register(models.SKUImage)
admin.site.register(models.SPUSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKUSpecification)
admin.site.register(models.GoodsVisitCount)
