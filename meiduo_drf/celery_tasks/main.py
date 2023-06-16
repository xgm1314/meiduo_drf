# _*_coding : uft-8 _*_
# @Time : 2023/6/15 13:10
# @Author : 
# @File : main
# @Project : meiduo_drf
from celery import Celery

celery_app = Celery('meiduo')  # 创建celery实例对象
celery_app.config_from_object('celery_tasks.config')  # 加载配置文件
celery_app.autodiscover_tasks(['celery_tasks.sms'])  # 自动注册异步任务
