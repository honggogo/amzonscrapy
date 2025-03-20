import scrapy
import yaml
from urllib.parse import urljoin
from amazon.items import AmazonItem

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    custom_settings = {
        'IMAGES_STORE': 'images',
        'DOWNLOAD_TIMEOUT': 30
    }

    def __init__(self, country='us', keyword='electronics', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country = country
        self.keyword = keyword
        self.site_config = self.load_config()
        
    def load_config(self):
        """加载国家配置文件"""
        with open('config/amazon_sites.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            site_config = config['countries'][self.country]
            
            # 确保配置中包含必要字段
            if 'lang' not in site_config:
                site_config['lang'] = 'en-US'  # 默认语言
            return site_config

    def start_requests(self):
        """初始请求"""
        search_url = f"{self.site_config['url']}/s?k={self.keyword}"
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'country': self.country}
        )

    def parse_search_results(self, response):
        """解析搜索结果页"""
        products = response.css('div[data-asin][data-component-type="s-search-result"]')
        
        for product in products:
            item = AmazonItem()
            item['country'] = self.country
            item['asin'] = product.attrib['data-asin']
            item['title'] = product.css('span.a-text-normal::text').get('').strip()[:200]
            item['source_url'] = response.urljoin(
                product.css('a.a-link-normal::attr(href)').get()
            )
            
            yield response.follow(
                item['source_url'],
                callback=self.parse_product_detail,
                meta={'item': item}
            )
        
        # 分页处理
        next_page = response.css('a.s-pagination-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_search_results)

    def parse_product_detail(self, response):
        """解析商品详情页"""
        item = response.meta['item']
        item['currency'] = self.site_config['currency']
        
        # 提取价格
        price_sel = response.css('span.a-price span.a-offscreen::text').get()
        if price_sel:
            item['price'] = price_sel.replace(item['currency'], '').strip()
        
        # 提取主图大图 URL
        main_image_url = response.css('#landingImage::attr(data-old-hires)').get()
        if not main_image_url:  # 确保 if 语句后的代码块正确缩进
            main_image_url = response.css('#landingImage::attr(src)').get()
        
        item['main_image'] = main_image_url
        
        # 处理颜色变体
        if self.has_color_variants(response):
            for variant in self.get_color_variants(response):
                variant_item = AmazonItem(item)
                variant_item.update({
                    'color_name': variant['color'],
                    'color_asin': variant['asin'],
                    'swatch_image': variant['image']
                })
                yield response.follow(
                    f"{self.site_config['url']}/dp/{variant['asin']}",
                    callback=self.parse_variant_detail,
                    meta={'item': variant_item}
                )
        else:
            yield item

    def has_color_variants(self, response):
        """检测颜色变体存在性"""
        return bool(response.css(
            'ul[data-asin-variations], select#color_name, div#variation_color_name'
        ))

    def get_color_variants(self, response):
        """提取颜色变体信息"""
        variants = []
        
        # 处理按钮式变体
        for li in response.css('ul[data-asin-variations] li[data-asin]'):
            variants.append({
                'asin': li.attrib['data-asin'],
                'color': li.css('img::attr(alt)').get() or li.css('span::text').get(),
                'image': li.css('img::attr(src)').get()
            })
        
        # 处理下拉菜单式变体
        for option in response.css('select#color_name option[value!=""]'):
            variants.append({
                'asin': option.attrib.get('data-asin', ''),
                'color': option.css('::text').get().split('-')[-1].strip(),
                'image': option.attrib.get('data-img', '')
            })
            
        return variants

    def parse_variant_detail(self, response):
        """解析颜色变体详情页"""
        item = response.meta['item']
        
        # 更新变体专属信息
        item['title'] = response.css('span#productTitle::text').get('').strip()
        item['source_url'] = response.url
        
        # 更新价格信息
        new_price = response.css('span.a-price span.a-offscreen::text').get()
        if new_price:
            item['price'] = new_price.replace(item['currency'], '').strip()
        
        yield item