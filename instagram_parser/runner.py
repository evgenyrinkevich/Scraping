from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from pymongo import MongoClient

from instagram_parser.spiders.igparser import IgparserSpider
from instagram_parser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    users_to_parse = ['django.python', 'pythontraininginpune', 'python.hub']
    process.crawl(IgparserSpider, users_to_parse=users_to_parse)

    process.start()

    client = MongoClient('localhost', 27017)
    db = client.ig1402

    for profile in users_to_parse:
        print('*' * 40)
        print(f'Список подписчиков {profile}:')
        for user in db[profile].find({'status': 'followee'}):
            print(user['username'])
