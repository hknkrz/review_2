from bs4 import BeautifulSoup
import collections
import requests

FIRST_40_WORDS = 40
SHORT_WORD = 3
KEY_WORD_QUANTITY = 5


def word_counter(link):
    """Принимает ссылку на статью, проводит частотный анализ текста"""
    tag_str = ''
    response = requests.get(link)

    soup = BeautifulSoup(response.content.decode('windows-1251', 'ignore'), 'lxml')
    text = soup.find('article', itemprop='articleBody')
    header = soup.find('h1', itemprop='headline').get_text()
    tag_bar = soup.find('div', class_='textMTags')
    for tag in tag_bar.find_all('a'):
        tag_str += tag.get_text() + '\n'

    all_text = ''
    for element in text.find_all('p'):
        all_text += ' ' + element.get_text()
    word_dict = collections.Counter(all_text.split())
    len_dict = len_counter(word_dict)
    words = popular_words(word_dict)
    return word_dict, len_dict, tag_str, header, words


def len_counter(word_dict):
    """Принимает словарь с частотами слов, строит частотный словарь слов по их длнам"""
    len_dict = {len(x): sum([word_dict[y] if len(y) == len(x) else 0 for y in word_dict.keys()]) for x in
                word_dict.keys()}
    return len_dict


def popular_words(word_dict):
    """Принимает словарь с частотами слов, ищет вероятные ключевые слова"""
    words = []
    for key in word_dict.most_common(FIRST_40_WORDS):
        if len(words) > SHORT_WORD:
            break
        if len(key[0]) > KEY_WORD_QUANTITY:
            words.append(key[0])
    return '\n'.join(words)
