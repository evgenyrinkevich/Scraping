import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from pymongo import MongoClient


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36'}
client = MongoClient('127.0.0.1', 27017)
db = client['mail']
email_list = db.trending_products
email_list.drop()


def get_emails(user_email, user_pwd, db_collection):
    """
    Scrapes emails info from mail.ru account into a MongodDB collection
    """

    # open browser
    email_name, domain_name = user_email.split('@')
    service = Service("./chromedriver")
    chrome_options = Options()
    chrome_options.binary_location = "/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("start-maximized")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://mail.ru/")

    # enter user' login and password
    elem = driver.find_element(By.XPATH, "//select[contains(@class, 'domain-select')]")
    select = Select(elem)
    select.select_by_value('@' + domain_name)

    elem = driver.find_element(By.XPATH, "//input[contains(@class, 'email-input')]")
    elem.send_keys(email_name)
    elem.send_keys(Keys.ENTER)

    # get newest email url
    elem = driver.find_element(By.XPATH, "//input[contains(@class, 'password-input')]")
    driver.implicitly_wait(10)
    elem.send_keys(user_pwd)
    elem.send_keys(Keys.ENTER)
    link_1st_email = driver.find_element(By.XPATH, "//div[contains(@class, 'Grid__inner')]/a[1]").get_attribute('href')
    driver.get(link_1st_email)

    while True:
        # scrape info
        time.sleep(1)
        title = driver.find_element(By.XPATH, "//h2[@class='thread-subject']").text
        content = WebDriverWait(driver, 2)\
            .until(ec.element_to_be_clickable((By.XPATH, "//div[contains(@id, 'BODY')]"))).get_attribute('innerHTML')
        date = driver.find_element(By.XPATH, "//div[@class='letter__author']//div[@class='letter__date']").text
        sender = driver.find_element(By.XPATH, "//div[@class='letter__author']/span[@class='letter-contact']") \
            .get_attribute('title')

        try:
            db_collection.insert_one({
                'title': title,
                'content': content,
                'date': date,
                'sender': sender,
                'link': driver.current_url
            })
        except:
            pass

        # click on "next email" element
        elem = driver.find_element(By.XPATH, "//span[contains(@class, 'arrow-down')]")
        if 'button2_disabled' in elem.get_attribute('class'):
            break
        elem.click()
    driver.quit()


if __name__ == '__main__':
    get_emails('study.ai_172@mail.ru', 'NextPassword172#', email_list)
