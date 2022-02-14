# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class InstagramParserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        client.drop_database('ig1402')
        self.mongobase = client.ig1402

    def process_item(self, item, spider):
        try:
            collection = self.mongobase[item['profile_username']]
            collection.insert_one(item)
        except Exception as e:
            print(e)
        return item
