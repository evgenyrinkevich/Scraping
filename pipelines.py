# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookParserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        client.drop_database('books0402')
        self.mongobase = client.books0402

    def process_item(self, item, spider):
        author, title = self.process_author_title(item.get('author_title'))
        item['author'] = author
        item['title'] = title
        del item['author_title']
        # converting prices and rating to int
        # max rating on labirint.ru is 10, on book24.ru - 5
        # to normalize rating on book24.ru is multiplied by 2
        if item['price']:
            item['price'] = int(''.join(filter(str.isdigit, item['price'])))
        if item['price_discount']:
            item['price_discount'] = int(item['price_discount'])
        item['rating'] = float(item['rating']) if spider.name == 'labirint' \
            else float(item['rating'].strip().replace(',', '.')) * 2
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    @staticmethod
    def process_author_title(author_title):
        try:
            author = author_title.split(':')[0]
            title = author_title.split(':')[1]
            return author, title
        except IndexError:
            return '', author_title

