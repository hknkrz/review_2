from bs4 import BeautifulSoup
import requests
import sqlite3

URL = 'https://interfax.ru'
OPTIMAL_PAGE_QUANTITY = 10
LINK_PREFIX_SIZE = 12


def parse_stories():
    """Сбор информации о статьях на 1 десяти страницах новостного сайта
    https://interfax.ru. При первом запуске формируется база данных,
    при последующих она обновляется"""
    upd_time_dict = create_upd_dict()
    response = requests.get(URL + '/story/')
    soup = BeautifulSoup(response.text, 'lxml')

    page_board = soup.find('div', class_='allPNav')
    pages = page_board.find_all('a')
    last_page = pages[len(pages) - 1]['href'][LINK_PREFIX_SIZE:]
    for page in range(1, int(last_page) + 1):
        # Парсинг 10 первых страниц
        if page == OPTIMAL_PAGE_QUANTITY:
            break
        cur_url = URL + '/story/page_' + str(page)
        response = requests.get(cur_url)
        soup = BeautifulSoup(response.content.decode('windows-1251', 'ignore'), 'lxml')
        items = soup.find_all('div', class_='allStory')
        for item in items:
            topics = item.find_all('div', recursive=False)
            for topic in topics:
                link = topic.find('a')['href']
                if link[:6] != '/story':
                    continue
                time = topic.find('time')['datetime']
                name = topic.find('a')['title']

                if name in upd_time_dict.keys():
                    if upd_time_dict[name][0] != str(time):
                        upd_time_dict[name][0] = str(time)
                        upd_time_dict[name][1] = False
                        upd_time_dict[name][2] = parse_topics(link, time)

                    upd_time_dict[name] = [str(time), None, parse_topics(link, None), link]

    update_db(upd_time_dict)
    return


def update_db(update_dict):
    """Функция отвечат за обновление базы данных, принимает словарь с необходимыми обновлениями"""
    with sqlite3.connect('User.db') as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS topics(topic_name PRIMARY KEY,upd_time TEXT,stories TEXT,link TEXT )""")
        for key in update_dict.keys():
            # Если добавлен новый раздел
            if update_dict[key][1] is None:
                cur.execute("INSERT INTO topics VALUES (?,?,?,?)",
                            (key, update_dict[key][0], update_dict[key][2], update_dict[key][3]))

            # Если данные в базе не устарели - переход на следующую итерацию
            elif update_dict[key][1]:
                continue
            # Если в присутствующий в базе раздел новостей добавлены новые статьи
            else:
                for story in cur.execute(f"SELECT stories FROM topics WHERE topic_name = '{key}'"):
                    substr = story[0]
                cur.execute(
                    f"UPDATE topics SET stories = {substr + update_dict[key][2]}")
                cur.execute(
                    f"UPDATE topics SET upd_time = {substr + update_dict[key][0]}")

        conn.commit()


def parse_topics(link, time):
    """Парсинг новостного раздела, принимает ссылку на раздел и время последнего обновления в базе данных
    собирает информацию до тех пор, пока не дойдет до статьи с временем публикации, совпадающем со временем
    обновления базы данных"""
    result = []
    response = requests.get(URL + link)
    soup = BeautifulSoup(response.text, 'lxml')
    page_board = soup.find('div', class_='allPNav')
    if not page_board:
        last_page = 1
    else:
        pages = page_board.find_all('a')
        last_page = pages[len(pages) - 1]['href'].split('_')[1]
    for page in range(1, int(last_page) + 1):
        stories = parse_page(link, '/page_' + str(page))
        for story in stories:
            if story.find('a'):
                if time and str(story.find('time')['datetime']) == time:
                    return result

                result.append(URL + story.find('a')['href'])
    return '\n'.join(list(reversed(result)))


def parse_page(link, page):
    """Парсит информацию с конкретной статьи"""
    cur_url = URL + link + str(page)
    response = requests.get(cur_url)
    soup = BeautifulSoup(response.text, 'lxml')
    story_list = soup.find('div', class_='storyList')
    return story_list.find_all('div', recursive=False)


def create_upd_dict():
    """Генерирует словарь с изменениями базы данных"""
    update_time = dict()
    with sqlite3.connect('User.db') as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS topics(topic_name PRIMARY KEY,upd_time TEXT,stories TEXT,link TEXT )""")

        conn.commit()

        for topic in cur.execute("SELECT topic_name,upd_time FROM topics"):
            update_time[topic[0]] = [topic[1], True, '', '']
        return update_time
