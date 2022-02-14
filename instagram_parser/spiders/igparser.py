import json
import re
from copy import deepcopy
from urllib.parse import urlencode
import scrapy
from scrapy.http import HtmlResponse
import os
from dotenv import load_dotenv
from instagram_parser.items import InstagramParserItem

load_dotenv()


class IgparserSpider(scrapy.Spider):
    name = 'igparser'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://instagram.com/accounts/login/ajax/'
    inst_login = os.getenv('USERNAME')
    inst_password = os.getenv('PASSWORD')
    # users_to_parse = ['django.python', 'pythontraininginpune']
    api_url = 'https://i.instagram.com/api/v1/friendships/'

    def parse(self, response: HtmlResponse, **kwargs):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_password},
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users_to_parse:
                yield response.follow(url=f'/{user}/',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'username': user})

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables_followers = {'search_surface': 'follow_list_page',
                               'count': 12}
        variables_following = {'count': 12}
        url_followers = f'{self.api_url}{user_id}/followers/?{urlencode(variables_followers)}'
        url_following = f'{self.api_url}{user_id}/following/?{urlencode(variables_following)}'

        yield response.follow(url_followers,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              callback=self.user_followers,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables_followers': deepcopy(variables_followers)
                                         }
                              )
        yield response.follow(url_following,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              callback=self.user_following,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables_following': deepcopy(variables_following)
                                         }
                              )

    def user_followers(self, response: HtmlResponse, username, user_id, variables_followers):
        j_data = response.json()
        if j_data.get('big_list'):
            variables_followers['max_id'] = j_data.get('next_max_id')
            url_followers = f'{self.api_url}{user_id}/followers/?{urlencode(variables_followers)}'
            yield response.follow(url_followers,
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                                  callback=self.user_followers,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables_followers': deepcopy(variables_followers)
                                             }
                                  )
        for user in j_data.get('users'):
            item = InstagramParserItem(
                profile_username=username,
                status='follower',
                user_id=user.get('pk'),
                username=user.get('username'),
                pic=user.get('profile_pic_url'),
                data=user
            )
            yield item

    def user_following(self, response: HtmlResponse, username, user_id, variables_following):
        j_data = response.json()
        if j_data.get('big_list'):
            variables_following['max_id'] = j_data.get('next_max_id')
            url_following = f'{self.api_url}{user_id}/following/?{urlencode(variables_following)}'
            yield response.follow(url_following,
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                                  callback=self.user_following,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables_following': deepcopy(variables_following)
                                             }
                                  )
        for user in j_data.get('users'):
            item = InstagramParserItem(
                profile_username=username,
                status='followee',
                user_id=user.get('pk'),
                username=user.get('username'),
                pic=user.get('profile_pic_url'),
                data=user)

            yield item

    @staticmethod
    def fetch_csrf_token(text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    @staticmethod
    def fetch_user_id(text, username):
        try:
            matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('{\"id\":\"\\d+\"', text)[-1].split('"')[-2]
