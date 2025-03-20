import scrapy
import csv
from datetime import datetime
from scrapy.exporters import CsvItemExporter
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import logging

class CsvExportPipeline:
    """CSV导出管道"""
    
    def __init__(self):
        self.exporter = None
    
    def open_spider(self, spider):
        file = open(f'amazon_{spider.country}.csv', 'wb')
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = [
            'country', 'asin', 'title', 'price', 
            'currency', 'color_name', 'source_url'
        ]
        self.exporter.start_exporting()
    
    def process_item(self, item, spider):
        # 添加时间戳
        item['timestamp'] = datetime.now().isoformat()
        self.exporter.export_item(item)
        return item
    
    def close_spider(self, spider):
        self.exporter.finish_exporting()

class ColorVariantPipeline:
    """颜色变体去重"""
    
    def __init__(self):
        self.seen_asins = set()
    
    def process_item(self, item, spider):
        if item['asin'] in self.seen_asins:
            raise DropItem(f"重复ASIN: {item['asin']}")
        self.seen_asins.add(item['asin'])
        return item

class ImageDownloadPipeline(ImagesPipeline):
    """图片下载管道（仅下载首张主图大图）"""

    def get_media_requests(self, item, info):
        """生成图片下载请求"""
        # 仅下载首张主图大图
        main_image_url = item.get('main_image')
        if main_image_url:
            # 调试日志：打印图片 URL
            logging.debug(f"Downloading main image for ASIN: {item['asin']}")
            logging.debug(f"Main image URL: {main_image_url}")
            
            # 生成图片下载请求
            yield scrapy.Request(main_image_url, meta={'item': item})

    def file_path(self, request, response=None, info=None, *, item=None):
        """定义图片存储路径"""
        item = request.meta['item']
        filename = f"{item['asin']}_main.jpg"  # 文件名格式：ASIN_main.jpg
        path = f"{item['country']}/{filename}"
        
        # 调试日志：打印图片存储路径
        logging.debug(f"Saving main image to: {path}")
        return path

    def item_completed(self, results, item, info):
        """图片下载完成后的处理"""
        # 检查下载结果
        for success, result in results:
            if not success:
                logging.error(f"Failed to download main image: {result['url']}")
                raise DropItem(f"Failed to download main image: {result['url']}")
        
        # 调试日志：打印下载成功信息
        logging.debug(f"Successfully downloaded main image for ASIN: {item['asin']}")
        return item
        