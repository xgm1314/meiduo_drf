from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

from itsdangerous import TimedJSONWebSignatureSerializer as TJWSerializer, BadData


# Create your models here.
class User(AbstractUser):
    mobile = models.CharField(verbose_name='手机号', max_length=11, unique=True)
    email_active = models.BooleanField(verbose_name='邮箱激活状态', default=False)

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_email_verify_url(self):
        # 生成token_id,拼接激活链接
        serializer = TJWSerializer(secret_key=settings.SECRET_KEY, expires_in=60 * 60 * 24)
        data = {'user_id': self.id, 'email': self.email}
        token_id = serializer.dumps(data).decode()
        return token_id

    @staticmethod  # 调用静态方法
    def check_verify_email_token(token):
        serializer = TJWSerializer(secret_key=settings.SECRET_KEY, expires_in=60 * 60 * 24)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            id = data.get('user_id')
            email = data.get('email')
            try:
                user = User.objects.get(id=id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user
