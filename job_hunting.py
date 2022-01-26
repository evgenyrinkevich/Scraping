import time

import requests
from bs4 import BeautifulSoup
from pprint import pprint
from pymongo import MongoClient
from pymongo import errors

client = MongoClient('127.0.0.1', 27017)
db = client['jobs']
offers = db.offers
# offers.drop()
offers.create_index('link', name='link_index', unique=True)

SEARCH_STRING = 'Python'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}


def wage_parse(vacancy_el, elem_attr_info, replace_symbols):
    wage = {}
    try:
        tag_span_text = vacancy_el.find('span', {elem_attr_info['name']: elem_attr_info['value']}).get_text()
        for symbol in replace_symbols:
            tag_span_text = tag_span_text.replace(symbol, '')
        tag_span_text = tag_span_text.split()
        wage['currency'] = tag_span_text[-1] if tag_span_text[-1].isalpha() else None
        if 'от' in tag_span_text:
            wage['from'] = int(tag_span_text[1])
            wage['to'] = None
        elif 'до' in tag_span_text:
            wage['from'] = None
            wage['to'] = int(tag_span_text[1])
        else:
            wage['from'] = int(tag_span_text[0])
            wage['to'] = int(tag_span_text[2])

    except:
        wage['currency'], wage['from'], wage['to'] = None, None, None

    return wage


def get_hh_jobs(search_string):
    """
    Gets job offers by the search_string from hh.ru
    """

    url = 'https://hh.ru'

    params = {'text': search_string,
              'clusters': 'true',
              'ored_clusters': 'true',
              'enable_snippets': 'true',
              'items_on_page': '20',
              'page': 0}

    while True:

        time.sleep(0.01)  # to avoid requests error
        response = requests.get(url + '/search/vacancy',
                                params=params, headers=HEADERS)

        dom = BeautifulSoup(response.text, 'html.parser')

        vacancies_list = dom.find_all('div', {'class': 'vacancy-serp-item'})

        if not vacancies_list:
            break

        for vacancy_el in vacancies_list:
            tag_a = vacancy_el.find('a', {'class': 'bloko-link'})
            wage = wage_parse(vacancy_el, elem_attr_info={'name': 'data-qa',
                                                          'value': 'vacancy-serp__vacancy-compensation'},
                              replace_symbols=['\u202f', '.'])
            vacancy = {
                'title': tag_a.get_text(),
                'link': tag_a.get('href'),
                'wage': wage,
                'source': url
            }

            try:
                offers.insert_one(vacancy)
            except errors.DuplicateKeyError:
                pass
        params['page'] += 1


def get_higher_wages_offers(collection, wage):
    """
    Gets offers with salary <= wage from collection
    """

    def convert_wage_to_rub(wage, currency):
        try:
            data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute'][currency]
            rate = data['Value'] / data['Nominal']
        except:
            return wage
        return wage / rate

    search_wage = wage

    for currency in ('руб', 'USD', 'EUR', 'KZT'):

        if currency != 'руб':
            search_wage = convert_wage_to_rub(wage, currency)

        for doc in collection.find({'$or':
                                    [
                                        {'wage.from': {'$gt': search_wage}},
                                        {'wage.to': {'$gt': search_wage}}
                                    ], 'wage.currency': currency}):
            pprint(doc)


def main():
    get_hh_jobs(SEARCH_STRING)
    get_higher_wages_offers(offers, 500000)


if __name__ == "__main__":
    main()
