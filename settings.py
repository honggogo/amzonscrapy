BOT_NAME = 'amazon_scraper'

SPIDER_MODULES = ['amazon.spiders']
NEWSPIDER_MODULE = 'amazon.spiders'

# 基础配置
ROBOTSTXT_OBEY = False
LOG_LEVEL = 'INFO'
LOG_FILE = 'amazon.log'

REDIRECT_ENABLED = True  # 启用默认重定向处理
HTTPERROR_ALLOWED_CODES = [302]  # 允许处理302

# 下载控制
DOWNLOAD_DELAY = 2.5
AUTOTHROTTLE_ENABLED = True
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# 中间件配置
DOWNLOADER_MIDDLEWARES = {
    'amazon.middlewares.EnhancedMiddleware': 543,
}

# 管道配置
ITEM_PIPELINES = {
    'amazon.pipelines.ColorVariantPipeline': 200,
    'amazon.pipelines.CsvExportPipeline': 300,
    'amazon.pipelines.ImageDownloadPipeline': 800,
}

# 图片存储
IMAGES_STORE = 'images'
IMAGES_EXPIRES = 30  # 30天有效期

# 代理配置（需替换实际值）
PROXY_LIST = [
    'http://16ZRRDTX:754247@11828.5.tn.16yun.cn:6441',
    #'http://user:pass@proxy2:port'
]

# 调试日志
LOG_LEVEL = 'DEBUG'