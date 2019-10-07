import datetime

url = 'https://www.decathlon.ro/C-177431-final-de-colectie/N-478360-gen~barbati'
tor_path = r'D:\programs\TOR\Browser\TorBrowser\Tor\tor.exe'
proxi = "socks5://localhost:9050"

keywords_men = [
    'adulţi',
    'adulți',
    'bărbați',
    'bărbaţi',
    'barbati',
    'băieți',
    'baieti'
]

keywords_human = [
    'adulţi',
    'adulți',
    'adulti',
    'copii',
    'damă',
    'dama',
    'fete',
    'bărbaţi',
    'bărbați',
    'barbati',
    'băieţi',
    'băieți',
    'baieti'
]

number_pages = 50
min_date = datetime.datetime(2000, 1, 1)