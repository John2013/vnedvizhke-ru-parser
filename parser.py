import math
from os.path import realpath
from queue import Queue

import grequests
import requests
from bs4 import BeautifulSoup
from threading import Thread


def get_soup(url: str='https://vnedvigke.ru/'):
    try:
        request = requests.get(url)
    except requests.exceptions.TooManyRedirects:
        # print('!!!!!!!TooManyRedirects', url)
        return None
    if not request.ok:
        print(request.status_code)
    soup = BeautifulSoup(request.text, 'html.parser')
    return soup


def get_soups_async(urls: list):
    rs = (grequests.get(url) for url in urls)
    responses = grequests.map(rs)
    for res in responses:
        if res is not None:
            yield BeautifulSoup(res.text, 'html.parser')


def get_pages_count_by_items_count(items_count: int, page_size: int=15):
    """
    Получить количество страниц по количеству элементов и размеру страницы

    :param int items_count:
    :param int page_size:
    :return int:
    """
    return int(math.floor(items_count / page_size))


def parse(hostname: str='https://vnedvigke.ru'):
    """
    Получить список ссылок со сописками предложениями

    :param str hostname:
    :return List[str]: Список адресов страниц с предложениями
    """
    soup = get_soup(hostname + '/')

    buy_section_selector = '.main-page-list-buy > li'
    rent_section_selector = 'main-page-list-rent > li'

    sections_tags = \
        soup.select(buy_section_selector) + soup.select(rent_section_selector)

    # noinspection PyShadowingNames
    items_lists_urls: list = []

    items_lists_threads = []

    qe = Queue()

    for section_tag in sections_tags:
        section_a_tag = section_tag.select_one('a')
        section_count_tag = section_tag.select_one('span.small.text-muted')

        if section_count_tag is None:
            continue

        pages_count = get_pages_count_by_items_count(
            int(section_count_tag.text)
        )

        for page in range(pages_count):
            items_lists_urls.append('{}{}?page={}'.format(
                hostname,
                section_a_tag['href'].strip(),
                page + 1
            ))
            # print(items_lists_urls[-1])
            # todo переделать на grequests
            items_lists_threads.append(
                Thread(
                    target=get_items_urls,
                    args=(items_lists_urls[-1], hostname, qe),
                    daemon=True
                )
            )
            items_lists_threads[-1].start()

    map(lambda thread: thread.join(), items_lists_threads)

    contacts_urls = []
    while not qe.empty():
        contacts_urls.append(qe.get())

    # print("count", str(len(contacts_urls)))

    contacts = []
    for contact_soup in get_soups_async(contacts_urls):
        contacts.append(get_contact_list(contact_soup))

    # удалим копии
    contacts = [list(x) for x in set(tuple(x) for x in contacts)]
    # print('count', len(contacts))
    # from pprint import pprint
    # pprint(contacts)

    return contacts


def get_items_urls(url: str, hostname: str, qe):
    soup = get_soup(url)
    if soup is None:
        return None
    a_tags = soup.select('a.ads-list-address')

    # noinspection PyShadowingNames
    items_urls = []

    for a_tag in a_tags:
        items_urls.append(
            '{}{}'.format(hostname, a_tag['href'])
        )
        qe.put(items_urls[-1])

    return items_urls


def get_tags_content(soup, selector):
    """
    Получить текст тега или Кортеж с ссылкой и текстом тега

    :param BeautifulSoup soup:
    :param str selector:
    :return Union[None, Tuple[str], str]:
    """
    tag = soup.select_one(selector)
    if tag is None:
        return None
    if tag.name == 'a':
        return tag['href']
    return tag.text


def get_contact_list(soup):
    name_selector = '.container > .row > .col-md-9 .panel-body .col-md-3 ' \
                    'strong:nth-of-type(1)'

    phone_selector = '.container > .row > .col-md-9 .panel-body .col-md-3 ' \
                     'strong:nth-of-type(2)'

    firm_selector = '.container > .row > .col-md-9 .panel-body .col-md-3 ' \
                    'small'

    vk_selector = '.container > .row > .col-md-9 .panel-body .col-md-3 ' \
                  'i.icon-vkontakte + a'

    return [
        get_tags_content(soup, name_selector),
        get_tags_content(soup, phone_selector),
        get_tags_content(soup, firm_selector),
        get_tags_content(soup, vk_selector)
    ]


if __name__ == '__main__':
    # main_page_soup = get_soup()

    contacts = parse()

    print('count:', len(contacts))

    import csv

    # Write CSV file
    with open('contacts.csv', 'w', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerows(contacts)

    print('Готово, результат в файле', realpath('contacts.csv'))

    input()
