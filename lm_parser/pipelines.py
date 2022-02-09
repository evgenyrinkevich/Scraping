# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib

import scrapy
from itemadapter import ItemAdapter
from scrapy.selector import Selector
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from scrapy.utils.python import to_bytes


class LmparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        client.drop_database('leroy0402')
        self.mongobase = client.leroy0402

    def process_item(self, item, spider):
        if item['details']:
            response = Selector(text=item['details'])
            keys = response.xpath("//div[@class='def-list__group']//dt/text()").getall()
            values = response.xpath("//div[@class='def-list__group']//dd/text()").getall()
            values = [val.strip() for val in values]
            item['details'] = dict(zip(keys, values))
        try:
            collection = self.mongobase[spider.name]
            collection.insert_one(item)
        except Exception as e:
            print(e)
        return item


class LmImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                img = img.replace('_82', '_1200')
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'{item.get("name")}/{image_guid}.jpg'
