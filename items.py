import scrapy

class AmazonItem(scrapy.Item):
    # 基础字段
    country = scrapy.Field()       # 国家代码
    asin = scrapy.Field()          # 商品唯一标识
    title = scrapy.Field()         # 商品标题（含颜色变体）
    
    # 价格信息
    price = scrapy.Field()         # 当前价格
    currency = scrapy.Field()      # 货币单位
    
    # 颜色变体信息
    color_name = scrapy.Field()    # 颜色名称
    color_asin = scrapy.Field()    # 颜色变体ASIN
    swatch_image = scrapy.Field()  # 颜色样本图URL
    
    # 图片信息
    main_image = scrapy.Field()    # 主图URL
    image_urls = scrapy.Field()    # 所有图片URL（用于下载）
    images = scrapy.Field()        # 下载结果（自动填充）
    
    # 来源信息
    source_url = scrapy.Field()    # 页面URL
    timestamp = scrapy.Field()     # 采集时间戳