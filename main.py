from Parser import parse_stories
from SendMessage import new_docs, new_topics, topic, describe_doc, words, get_tags
import telebot
from telebot.util import async_dec
import time

DB_UPDATE_TIME = 160.0

bot = telebot.TeleBot('<YourToken>')

command_dict = {'/new_docs': new_docs, '/new_topics': new_topics, '/topic': topic, '/describe_doc': describe_doc,
                '/get_tags': get_tags, '/words': words}


@async_dec()
def re_parse():
    """Функция, регулярно парсящая новостной сайт"""
    starttime = time.time()
    while True:
        parse_stories()
        time.sleep(DB_UPDATE_TIME - ((time.time() - starttime) % DB_UPDATE_TIME))


@bot.message_handler(content_types=['text'],
                     commands=['/new_docs', '/new_topics', '/topic', '/describe_doc', '/get_tags', '/words'])
def get_text_messages(message):
    command = message.text.split(1)
    if command[0] == '/help':
        bot.send_message(message.from_user.id,
                         '/new_docs <N> - показать N самых свежих новостей\n/new_topics <N> - показать N самых свежих '
                         'тем\n/topic <topic_name> - показать описание темы и заголовки 5 самых свежих новостей в'
                         ' этой теме\n/describe_doc <link> - показать частоту слов и распределение слов по длинам\n'
                         '/get_tags <link> - показать теги статьи\n/words <link> - показать ключевые слова к статье'
                         )

    elif command[0] in command_dict.keys():
        if len(command) != 2:
            bot.send_message(message.from_user.id,
                             'Invalid arguments\n write /help to get a information about arguments for function' +
                             command[0])
            raise Exception('Excepted 1 argument')
        else:

            args = command[1:]
            result = command_dict[command[0]](*args)
            message_to_usr = ''
            for element in result.keys():
                '\n'.join(f"{message_to_usr}{str(element)}{str(result[element])}")
            bot.send_message(message.from_user.id, message_to_usr)
    else:
        bot.send_message(message.from_user.id, 'Invalid function\n write /help to get a list of possible functions')
        raise Exception('Invalid function')


re_parse()
bot.polling(none_stop=True, interval=0)
