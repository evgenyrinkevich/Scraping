# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookParserItem(scrapy.Item):
    title = scrapy.Field()
    author_title = scrapy.Field()
    author = scrapy.Field()
    price = scrapy.Field()
    price_discount = scrapy.Field()
    rating = scrapy.Field()
    url = scrapy.Field()
    _id = scrapy.Field()
