import scrapy
from scrapy.http import HtmlResponse
from lm_parser.items import LmparserItem
from scrapy.loader import ItemLoader


class LmRuSpider(scrapy.Spider):
    name = 'lm_ru'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://leroymerlin.ru/']
    page = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = kwargs.get("search")
        self.start_urls = [f'https://leroymerlin.ru/search/?q={self.search}&page={self.page}']

    def parse(self, response: HtmlResponse, **kwargs):
        self.page += 1
        next_page = f'https://leroymerlin.ru/search/?q={self.search}&page={self.page}'
        if response.xpath("//a[@data-qa-pagination-item = 'right']"):
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='product-image']")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    @staticmethod
    def parse_ads(response: HtmlResponse):
        loader = ItemLoader(item=LmparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('photos', "//img[@slot='thumbs']/@src")
        loader.add_xpath('details', "//dl")
        loader.add_value('url', response.url)
        yield loader.load_item()
