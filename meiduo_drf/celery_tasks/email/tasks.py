# _*_coding : uft-8 _*_
# @Time : 2023/6/21 17:12
# @Author : 
# @File : tasks
# @Project : meiduo_drf
from celery_tasks.main import celery_app
from django.core.mail import send_mail


@celery_app.task(name='send_verify_email')
def send_verify_email(subject, message, from_email, recipient_list, html_message):
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=html_message
    )
