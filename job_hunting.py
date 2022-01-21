import requests
from bs4 import BeautifulSoup
from pprint import pprint

SEARCH_STRING = 'Python'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}


def wage_parse(vacancy_el, elem_attr_info, replace_symbols):
    wage = {}
    try:
        tag_span_text = vacancy_el.find('span', {elem_attr_info['name']: elem_attr_info['value']}).get_text()
        for symbol in replace_symbols:
            tag_span_text = tag_span_text.replace(symbol, '')

        wage['currency'] = 'usd' if 'usd' in tag_span_text.lower() else 'руб'

        if 'от' in tag_span_text:
            wage['from'] = int(''.join(filter(str.isdigit, tag_span_text)))
            wage['to'] = None
        elif 'до' in tag_span_text:
            wage['from'] = None
            wage['to'] = int(''.join(filter(str.isdigit, tag_span_text)))
        else:
            wage['from'] = int(tag_span_text.split('–')[0])
            wage['to'] = int(''.join(filter(str.isdigit, tag_span_text.split('–')[1])))

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
              'page': 0}

    jobs_json = []
    while True:

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
                              replace_symbols=['\u202f', ' ', '.'])
            vacancy = {
                'title': tag_a.get_text(),
                'link': tag_a.get('href'),
                'wage': wage,
                'source': url
            }
            jobs_json.append(vacancy)
            params['page'] += 1

    return jobs_json


def get_superjob_jobs(search_str):
    """
        Gets job offers by the search_string from superjob.ru
        """

    url = 'https://www.superjob.ru/'

    params = {'keywords': search_str,
              'noGeo': '1',
              'page': 1}

    jobs_json = []
    while True:

        response = requests.get(url + '/vacancy/search',
                                params=params, headers=HEADERS)

        dom = BeautifulSoup(response.text, 'html.parser')

        vacancies_list = dom.find_all('div', {'class': '_2ft-o iJCa5 f-test-vacancy-item _1fma_ _2nteL'})

        if not vacancies_list:
            break

        for vacancy_el in vacancies_list:
            tag_a = vacancy_el.find('span', {'class': '_3a-0Y _3DjcL _3sM6i'}).findChild()
            wage = wage_parse(vacancy_el, elem_attr_info={'name': 'class',
                                                          'value': '_2Wp8I _3a-0Y _3DjcL _1tCB5 _3fXVo'},
                              replace_symbols=['\xa0', ' ', '.'])
            vacancy = {
                'title': tag_a.get_text(),
                'link': url + tag_a.get('href'),
                'wage': wage,
                'source': url
            }
            jobs_json.append(vacancy)
            params['page'] += 1

    return jobs_json


def main():
    pprint(get_hh_jobs(SEARCH_STRING))
    pprint(get_superjob_jobs(SEARCH_STRING))


if __name__ == "__main__":
    main()

# Результат выполнения скрипта:
# [{'link': 'https://hhcdn.ru/click?b=273804&place=35&hhtmFrom=vacancy_search_list',
#   'source': 'https://hh.ru',
#   'title': 'Python Developer',
#   'wage': {'currency': None, 'from': None, 'to': None}},
#  {'link': 'https://hh.ru/vacancy/51448522?from=vacancy_search_list&query=Python&hhtmFrom=vacancy_search_list',
#   'source': 'https://hh.ru',
#   'title': 'Founding Data scientist / Machine Learning Engineer',
#   'wage': {'currency': 'руб', 'from': 500000, 'to': None}},
#  {'link': 'https://hh.ru/vacancy/51262245?from=vacancy_search_list&query=Python&hhtmFrom=vacancy_search_list',
#   'source': 'https://hh.ru',
