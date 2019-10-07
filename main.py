import defines, time, hashlib, json, datetime, glob, subprocess
from selenium import webdriver
from datetime import date
from termcolor import cprint
from colorama import init as init_color


def print_separator(sep='='):
    print(sep*30)


def get_previous_file_name_after_date(extension: str):
    max = defines.min_date
    for file in glob.glob('*' + extension):

        y, m, d = [int(x) for x in file.split('.')[0].split('_')]
        prev = datetime.datetime(day=d, month=m, year=y)

        if prev > max:
            max = prev

    if max != defines.min_date:
        return str(max)[:10].replace('-', '_') + extension
    else:
        return ''


def create_file_name_today_date(extension: str):
    return str(date.today().strftime("%Y/%m/%d")).replace('/', '_') + extension

# returns the filename of the file created
def create_database_updated():
    js = list()
    file_name = ''

    PROXY = "socks5://localhost:9050"
    tor_proc = subprocess.Popen(defines.tor_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument('--proxy-server=%s' % PROXY)
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
                    'name': product_name,
                    'price': product_price,
                    'link': product_link,
                    'hash': product_hash
                }
            )

    try:
        file_name = create_file_name_today_date(extension='.db')
        with open(file_name, 'w+', encoding='utf-8') as f:
            json.dump(js, f, ensure_ascii=False, indent=4)
    except Exception as e:
        cprint(e, 'red')

    tor_proc.kill()
    cprint('DONE - created database for ' + file_name, 'green')

    return file_name


def extract_price(j):
    return float(j['price'])


# returns the filename of the file created
def create_comparison_files(db_updated, db_prev):
    stats = list()
    new = list()
    file_stat_name = ''
    file_new_name = ''

    with open(db_updated, 'r', encoding='utf-8') as f:
        js_new = json.load(f)
    with open(db_prev, 'r', encoding='utf-8') as f:
        js_old = json.load(f)

    for j_new in js_new:
        is_new = True
        for j_old in js_old:
            if j_new['hash'] == j_old['hash']:
                is_new = False
                price_new = float(j_new['price'])
                price_old = float(j_old['price'])
                j_new['price'] = str((price_new-price_old)*100/price_new) + '%'
                stats.append(j_new)
                break
        if is_new:
            new.append(j_new)

    new.sort(key=extract_price, reverse=True)

    try:
        file_stat_name = create_file_name_today_date('.stat')
        with open(file_stat_name, 'w+', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
        file_new_name = create_file_name_today_date('.stat')
        with open(file_new_name, 'w+', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
    except Exception as e:
        cprint(e, 'red')


    cprint('DONE - created stat ' + file_stat_name, 'green')

    return file_stat_name


if __name__ == '__main__':
    init_color()

    db_prev = get_previous_file_name_after_date(extension='.db')
    db_updated = create_database_updated()

    if db_prev == '':
        cprint('FINISHED', 'green')
        cprint('CAN\'T CREATE COMPARISON FILES. DID NOT HAVE TO WHAT TO COMPARE THE CURRENT ONE.', 'red')
        exit(2)

    create_comparison_files(db_updated, db_prev)

    cprint('FINISHED', 'green')



