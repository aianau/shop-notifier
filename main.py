import defines, time, hashlib, json, datetime, glob, subprocess
from selenium import webdriver
from datetime import date
from termcolor import cprint
from colorama import init as init_color


def print_separator(sep='='):
    print(sep*30)


def get_newest_file_name_after_date(extension: str):
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


def dump_json_by_date_filename(js, extension):
    file_name = create_file_name_today_date(extension=extension)
    with open(file_name, 'w+', encoding='utf-8') as f:
        json.dump(js, f, ensure_ascii=False, indent=4)
    cprint('DONE - created database for ' + file_name, 'green')


# returns the filename of the file created
def create_database_updated():
    js = list()
    js_men = list()
    js_nonhuman = list()

    tor_proc = subprocess.Popen(defines.tor_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument('--proxy-server=%s' % defines.proxi)
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

            is_men = False
            for k in defines.keywords_men:
                if k in str(product_name).lower() or k in str(product_link).lower():
                    is_men = True
            if is_men:
                js_men.append(
                    {
                        'name': product_name,
                        'price': product_price,
                        'link': product_link,
                        'hash': product_hash
                    }
                )

            is_nonhuman = True
            for k in defines.keywords_human:
                if k in str(product_name).lower() or k in str(product_link).lower():
                    is_nonhuman = False
            if is_nonhuman:
                js_nonhuman.append(
                    {
                        'name': product_name,
                        'price': product_price,
                        'link': product_link,
                        'hash': product_hash
                    }
                )

    try:
        dump_json_by_date_filename(js=js, extension='.db')
        dump_json_by_date_filename(js=js_men, extension='.men.db')
        dump_json_by_date_filename(js=js_nonhuman, extension='.nonhuman.db')

    except Exception as e:
        cprint(e, 'red')

    tor_proc.kill()


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
                if price_new-price_old != 0:
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

    db_men_prev = get_newest_file_name_after_date(extension='.men.db')
    db_nonhuman_prev = get_newest_file_name_after_date(extension='.nonhuman.db')
    create_database_updated()
    db_men_updated = get_newest_file_name_after_date(extension='.men.db')
    db_nonhuman_updated = get_newest_file_name_after_date(extension='.nonhuman.db')

    if db_men_prev == '':
        cprint('CAN\'T CREATE COMPARISON FILES FOR MEN. DID NOT HAVE TO WHAT TO COMPARE THE CURRENT ONE.', 'red')
    else:
        create_comparison_files(db_men_updated, db_men_prev)

    if db_nonhuman_prev == '':
        cprint('CAN\'T CREATE COMPARISON FILES FOR NONHUMAN. DID NOT HAVE TO WHAT TO COMPARE THE CURRENT ONE.', 'red')
    else:
        create_comparison_files(db_nonhuman_updated, db_nonhuman_prev)

    cprint('FINISHED', 'green')



