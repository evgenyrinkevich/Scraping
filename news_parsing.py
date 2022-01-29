from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36'}

client = MongoClient('127.0.0.1', 27017)
db = client['news_db']
news_collection = db.news_collection
news_collection.drop()
# news_collection.create_index('link', name='link_index', unique=True)


def get_lenta_news():
    url = 'https://lenta.ru/'
    response = requests.get(url, headers=headers)

    dom = html.fromstring(response.text)
    items = dom.xpath('//div/a[contains(@class,"card-") and contains(@class,"_topnews")]')

    news_list = []
    for item in items:
        title = item.xpath('.//*[contains(@class,"_title")]/text()')[0]
        link = url + item.get('href')
        date = '.'.join([s for s in item.get('href').split('/') if s.isdigit()])
        source = 'lenta.ru'
        news = {
            'title': title,
            'link': link,
            'date': date,
            'source': source
        }
        news_list.append(news)
        try:
            news_collection.insert_one(news)
        except:
            pass

    return news_list


def get_mailru_news():
    url = 'https://news.mail.ru/'
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)

    news_list = []

    top_news = dom.xpath('//tr/td/div/a/@href')
    list_news = dom.xpath('//ul/li/a/@href')
    news = set(top_news)
    news.update(set(list_news))
    for url in news:
        response = requests.get(url, headers=headers)
        dom = html.fromstring(response.text)
        news_el = dom.xpath('//div[contains(@class, "js-article")]')[0]
        date = news_el.xpath('.//span[@datetime]/@datetime')[0][:10].replace('-', '.')
        source = news_el.xpath('.//a/span/text()')[0]
        title = news_el.xpath('.//h1/text()')[0]
        news_list.append({
            'title': title,
            'date': date,
            'source': source,
            'url': url
        })
        try:
            news_collection.insert_one({
                'title': title,
                'date': date,
                'source': source,
                'url': url
            })
        except:
            pass

    return news_list


def get_yandex_news():
    url = 'https://yandex.ru/news/'
    response = requests.get(url, headers=headers)

    dom = html.fromstring(response.text)
    items = dom.xpath('//div[@class="mg-card mg-card_flexible-single mg-card_media-fixed-height mg-card_type_image '
                      'mg-grid__item"]')

    news_list = []
    for item in items:
        link = item.xpath('.//h2/a/@href')[0]

        url = get_yandex_url(link)
        title = item.xpath('.//h2/a/text()')[0].replace('\xa0', '')
        source = item.xpath('.//div[contains(@class, "mg-card-footer")]//a/text()')[0]
        date = item.xpath('.//div[contains(@class, "mg-card-footer")]//span[@class="mg-card-source__time"]/text()')[0]
        news_list.append({
            'url': url,
            'title': title,
            'source': source,
            'date': date
        })
        try:
            news_collection.insert_one({
                'title': title,
                'date': date,
                'source': source,
                'url': url
            })
        except:
            pass

    main_news = dom.xpath('//div[@class="mg-card mg-card_type_image mg-card_stretching mg-card_flexible-double '
                          'mg-grid__item"]')[0]
    link = main_news.xpath('.//h2/a/@href')[0]

    url = get_yandex_url(link)
    title = main_news.xpath('.//h2/a/text()')[0].replace('\xa0', '')
    source = main_news.xpath('.//div[contains(@class, "mg-card-footer")]//a/text()')[0]
    date = main_news.xpath('.//div[contains(@class, "mg-card-footer")]//span[@class="mg-card-source__time"]/text()')[0]
    news_list.append({
        'url': url,
        'title': title,
        'source': source,
        'date': date
    })
    try:
        news_collection.insert_one({
            'title': title,
            'date': date,
            'source': source,
            'url': url
        })
    except:
        pass

    return news_list


def get_yandex_url(link):
    response = requests.get(link, headers=headers)
    dom = html.fromstring(response.text)
    url = dom.xpath('//h1/a/@href')[0]
    return url


if __name__ == '__main__':
    get_lenta_news()
    get_mailru_news()
    get_yandex_news()
    for doc in news_collection.find({}):
        pprint(doc)
