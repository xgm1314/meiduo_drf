# # _*_coding : uft-8 _*_
# # @Time : 2023/6/26 21:11
# # @Author :
# # @File : fdfs_storage
# # @Project : meiduo_drf
# from django.core.files.storage import Storage
# from django.conf import settings
#
# from fdfs_client.client import Fdfs_client
#
#
# class FastDFSStorage(Storage):
#     """ 自定义文件存储系统类 """
#
#     def __init__(self, client_path=None, base_url=None):
#         self.client_path = client_path or settings.FDFS_CLIENT_CONF  # fastDFS客户端配置文件路径
#         self.base_url = base_url or settings.BASE_DIR  # storage服务器ip:端口
#
#     def _open(self, name, mode='rb'):
#         """
#         用来打开文件的，但是我们自定义文件存储系统的目的是为了实现储存到远程的FastDFS服务器，不需要打开文件，所以此方法重写后什么也不做，pass
#         Args:
#             name: 要打开的文件名
#             mode: 打开文件的模式   read bytes类型
#
#         Returns:None
#
#         """
#         pass
#
#     def _save(self, name, content):
#         """
#         文件存储时调用此方法，但是此方法是向本地存储，在此方法做实现文件存储到远程的FastDFS服务器
#         Args:
#             name:要上传的文件名
#             content:以rb模式打开的文件对象，将来通过content.read()就可以读取到文件的二进制数据
#
#         Returns:file_id
#
#         """
#         # client = Fdfs_client('utils.fastdfs.client.conf')  # 创建FdastDFS客户端
#         client = Fdfs_client(self.client_path)  # 创建FdastDFS客户端
#         # 通过客户端调用上传文件的方法上传到fastDFS服务器
#         # client.upload_by_filename('写上传文件的绝对路径')  # 只能通过文件绝对路径进行上传  此方式上传的文件会有后缀
#         # upload_by_buffer  # 可以通过文件二进制数据进行上传    上传后的文件没有后缀
#         ret = client.upload_by_buffer(content.read())
#
#         if ret.get('Status') != 'Upload successed.':  # 判断是否上传成功，不成功抛出异常
#             raise Exception('Upload file failed')
#
#         file_id = ret.get('Remote file_id')  # 获取file_id
#         return file_id  # 返回数据
#
#     def exists(self, name):
#         """
#         当要进行上传时都调用此方法判断文件是否已上传，如果没有上传才会调用save方法进行上传
#         Args:
#             name:要上传的文件名
#
#         Returns:True(表示文件已存在，不需要上传) False(文件不存在，需要上传)
#
#         """
#         return False
#
#     def url(self, name):
#         """
#         当要访问图片时，就会调用此方法获取图片文件的绝对路径
#         Args:
#             name:要访问图片的file_id
#
#         Returns:完整的图片访问路径 ：storage_server IP:8888 + file_id
#
#         """
#         # return 'http://虚拟机IP:8888/' + name
#         return self.base_url + name
