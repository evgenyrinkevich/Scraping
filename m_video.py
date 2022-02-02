from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from pymongo import MongoClient


client = MongoClient('127.0.0.1', 27017)
db = client['mvideo']
trending_products = db.trending_products
trending_products.drop()


def get_mvideo_trending_products():
    """
    Gets name, url, price and img link for trending products from mvideo.ru
    """
    service = Service("./chromedriver")
    chrome_options = Options()
    chrome_options.binary_location = "/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("start-maximized")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.mvideo.ru/")
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight / 3);")

    wait = WebDriverWait(driver, 10)
    elem = wait.until(ec.presence_of_element_located((By.XPATH, '//span[contains(text(), "В тренде")]/ancestor::button')))
    elem.click()

    data = []
    prices = []
    elem = driver.find_elements(By.XPATH, "//mvid-carousel[contains(@class,'carusel')]")[0]  # контейнер "в тренде"
    elems = elem.find_elements(By.XPATH, ".//span[@class='price__main-value']")
    for el in elems:
        prices.append(''.join(el.text.split()))

    elems = elem.find_elements(By.XPATH, ".//a[contains(@class, 'img-with-badge')]")
    for el in elems:
        url = el.get_attribute('href').replace('/reviews', '')
        img_el = el.find_element(By.TAG_NAME, 'img')
        name = img_el.get_attribute('alt')
        img = img_el.get_attribute('srcset').split('//')[1].split()[0]
        details = {
            'url': url,
            'name': name,
            'img': 'https://' + img
        }
        data.append(details)
    for item in zip(data, prices):
        item[0]['price'] = int(item[1])

    for product in data:
        try:
            trending_products.insert_one(product)
        except Exception as e:
            print(e)
    # for doc in trending_products.find({}):
    #     print(doc)
    driver.quit()


if __name__ == '__main__':
    get_mvideo_trending_products()
