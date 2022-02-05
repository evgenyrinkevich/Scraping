import scrapy
from scrapy.http import HtmlResponse
from book_parser.items import BookParserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    page = 1
    start_urls = [f'https://book24.ru/search/page-{page}/?q=%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8%D0%B2']

    def parse(self, response: HtmlResponse, **kwargs):
        Book24Spider.page += 1
        next_page = f'https://book24.ru/search/page-{Book24Spider.page}/?q=%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8' \
                    f'%D0%B2 '
        if not response.xpath("//div[@class='not-found page-wrap__inner']"):
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[contains(@class, 'product-card__image-link')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    @staticmethod
    def book_parse(response: HtmlResponse):
        author_title = response.xpath("//h1/text()").get()
        price_discount = response.xpath("//meta[@itemprop='price']/@content").get()
        price = response.xpath("//span[@class='app-price product-sidebar-price__price-old']/text()").get() or price_discount
        rating = response.xpath("//span[@class='rating-widget__main-text']/text()").get()
        url = response.url
        yield BookParserItem(author_title=author_title,
                             url=url,
                             price_discount=price_discount,
                             price=price,
                             rating=rating)
