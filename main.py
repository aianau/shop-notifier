import defines, time, hashlib, json
from selenium import webdriver
from datetime import date
from termcolor import cprint
from colorama import init as init_color


def print_separator(sep='='):
    print(sep*30)


def create_database():
    js = list()

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(r'.\chromedriver.exe', options=options)
    driver.get(url=defines.url)

    for i in range(0, defines.number_pages):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.2)

    lis = driver.find_elements_by_tag_name('li')
    for li in lis:
        if str(li.get_attribute('class')).startswith('new-product-thumbnail'):
            product_name = li.get_attribute('data-product-name')
            product_price = li.get_attribute('data-product-price')
            product_link = li.find_element_by_tag_name('a').get_attribute('href')

            hash = hashlib.md5()
            hash.update(str(product_name).encode(encoding='utf-8'))
            hash.update(str(product_price).encode(encoding='utf-8'))
            hash.update(str(product_link).encode(encoding='utf-8'))
            product_hash = hash.hexdigest()

            js.append(
                {
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_link': product_link,
                    'product_hash': product_hash
                }
            )

    try:
        with open('db_' + date.today().strftime("%d/%m/%Y").replace('/', '_'), 'w+', encoding='utf-8') as f:
            json.dump(js, f, ensure_ascii=False, indent=4)
    except Exception as e:
        cprint(e, 'red')

    cprint('DONE - created database for ' + date.today().strftime("%d/%m/%Y").replace('/', '_'), 'green')


if __name__ == '__main__':
    init_color()
    create_database()



