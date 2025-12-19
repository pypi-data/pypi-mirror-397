from AioSpider.middleware import DownloadMiddleware


# create your middleware here

# class DomeMiddleware(DownloadMiddleware):
#
#     # 可以通过owner指定哪些爬虫能经过该中间件
#     owner = ['domeSpider']
#
#     def process_request(self, request):
#         """
#         处理请求
#         @params:
#             request: HttpRequest 对象
#         @return:
#             Request: 交由引擎重新调度该Request对象
#             Response: 交由引擎重新调度该Response对象
#             None: 正常，继续往下执行 穿过下一个中间件
#             False: 丢弃该Request或Response对象
#         """
#         return None
#
#     def process_response(self, response):
#         """
#         处理响应
#         @params:
#             response: Response 对象
#         @return:
#             Request: 交由引擎重新调度该Request对象
#             Response: 交由引擎重新调度该Response对象
#             None: 正常，继续往下执行 穿过下一个中间件
#             False: 丢弃该Request或Response对象
#         """
#         return None
