from fake_useragent import UserAgent
import random
import logging

class EnhancedMiddleware:
    """增强型反爬中间件集合"""

    def __init__(self, proxy_list):
        # UA配置
        self.ua = UserAgent()
        self.custom_ua = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X)...',
            'Mozilla/5.0 (Linux; Android 13; SM-S901U)...'
        ]
        
        # 代理配置
        self.proxy_list = proxy_list
        self.proxy_index = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_list=crawler.settings.get('PROXY_LIST')
        )

    def process_request(self, request, spider):
        """处理请求头"""
        # 获取语言配置，如果未定义则使用默认值
        lang = getattr(spider, 'site_config', {}).get('lang', 'en-US')
        
        # 随机UA策略
        if random.random() < 0.7:
            ua = self.ua.random
        else:
            ua = random.choice(self.custom_ua)
        
        # 更新请求头
        request.headers.update({
            'User-Agent': ua,
            'Accept-Language': lang,  # 使用配置中的语言
            'Referer': spider.site_config.get('url', 'https://www.amazon.com')
        })
        
        # 代理设置
        if self.proxy_list:
            proxy = self.proxy_list[self.proxy_index]
            request.meta['proxy'] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
            logging.debug(f"Using proxy: {proxy}")

    def process_response(self, request, response, spider):
        """处理异常响应"""
        if response.status in [403, 429]:
            spider.logger.warning(f'触发反爬机制: {response.url}')
            return self._retry_request(request, spider)
        return response
 ##新增       
 #  def process_response(self, request, response, spider):    
 #        lang = spider.site_config.get('lang', 'en-US')
 #        spider.logger.debug(f"Using language: {lang}")
 #        spider.logger.debug(f"Request headers: {request.headers}")
#新增
    def _retry_request(self, request, spider):
        """重试策略"""
        retryreq = request.copy()
        retryreq.dont_filter = True
        return retryreq
