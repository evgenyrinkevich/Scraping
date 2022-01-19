# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.
import requests
import json


def get_users_repos(username):
    """
    Prints out list of github user's repos and creates a json file
    with all repos info from github API
    """
    try:
        url = f'https://api.github.com/users/{username}/repos'

        response = requests.get(url)
        j_data = response.json()
        print(f'Repos of {username}:')
        for repo in j_data:
            print(repo.get('name'))

        with open(f'{username}_repos.json', 'w') as f:
            json.dump(j_data, f)
    except AttributeError as e:
        print(f'Oops, looks like there\'no such user!')


user_name = input('Enter github username: ')
get_users_repos(user_name)

# Результат выполнения скритпа:
# Repos of evgenyrinkevich:
# Algorithms-And-Data-Structurees-In-Python
# Basic-JS
# django2
# django_gb
# evgenyrinkevich.github.io
# Image_Processing
# MySQL
# password_checker
# pdf_utility
# portfolio
# python
# Scraping
