# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramParserItem(scrapy.Item):
    profile_username = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    pic = scrapy.Field()
    status = scrapy.Field()
    data = scrapy.Field()
    _id = scrapy.Field()
