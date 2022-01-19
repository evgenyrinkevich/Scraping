import requests


def get_temperature_by_ip():
    try:
        ip = requests.get('https://api.ipify.org').content.decode('utf-8')
        url = f'http://ip-api.com/json/{ip}'
        response = requests.get(url)
        json_current_ip = response.json()

        url = 'https://api.openweathermap.org/data/2.5/weather'
        city = json_current_ip.get('city')
        appid = 'a96a09800bb68d786215631deb3af8f8'

        params = {'q': city,
                  'appid': appid}

        response = requests.get(url, params=params)
        j_data = response.json()
        print(f"Current temperature in {j_data.get('name')} is {j_data.get('main').get('temp') - 273.15:.2f} Celcius.")
    except AttributeError:
        print('Invalid API key')


get_temperature_by_ip()

# Результат выполнения скритпа:
# Current temperature in Moscow is -10.59 Celcius.
