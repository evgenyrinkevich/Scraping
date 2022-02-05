import scrapy
from scrapy.http import HtmlResponse
from book_parser.items import BookParserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8%D0%B2/?order=relevance'
                  '&way=back&display=cover&paperbooks=1&available=1&preorder=1&wait=1&no=1&price_min=600'
                  '&price_max=',
                  'https://www.labirint.ru/search/%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8%D0%B2/?order=relevance'
                  '&way=back&display=cover&paperbooks=1&available=1&preorder=1&wait=1&no=1&price_min=450'
                  '&price_max=600',
                  'https://www.labirint.ru/search/%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8%D0%B2/?order=relevance'
                  '&way=back&display=cover&paperbooks=1&available=1&preorder=1&wait=1&no=1&price_min=350'
                  '&price_max=450 '
                  ]

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath("//a[@class= 'pagination-next__text']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@class= 'cover']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    @staticmethod
    def book_parse(response: HtmlResponse):
        author_title = response.xpath("//h1/text()").get()
        price = response.xpath("//span[@class='buying-priceold-val-number']/text()").get() or \
                response.xpath("//span[contains(@class, 'buying-price-val-number')]/text()").get()
        price_discount = response.xpath("//span[@class='buying-pricenew-val-number']/text()").get() or price
        rating = response.xpath("//div[@id='rate']/text()").get()
        url = response.url
        yield BookParserItem(author_title=author_title,
                             url=url,
                             price_discount=price_discount,
                             price=price,
                             rating=rating)
