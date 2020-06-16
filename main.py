# -*- coding: utf-8 -*-

import itertools
import pyrogram
from pyrogram import *
from requests import get

import re

ip = get('https://api.ipify.org').text
proxy = None
if ip != '91.215.155.217':
    proxy = dict(
        hostname="orbtl.s5.opennetwork.cc",
        port=999,
        username="506702351",
        password="WQBnC2D7"
    )

bot = Client(
    api_id=142098,
    api_hash="6e1c38db937fc8cd0cf10517135f74cf",
    bot_token="1172197402:AAGG51CXUbfwlvzO5rpfrTcE6ffu37jW7UQ",
    session_name="ronmount",
    proxy=proxy,
)

bot.set_parse_mode('html')

a = []
_a = []
rules_list = []
searching_now = False
combinations_list = ''

fruits = {
    1: '🍋',
    2: '🍇',
    3: '🍏',
    4: '🥕',
    5: '🍅',
}


async def clear(m):
    global a
    global _a
    global rules_list
    global searching_now

    a.clear()
    _a.clear()
    rules_list = []
    searching_now = False

    text = '<b>Все списки очищенны.</b>\n\n👉/start Начало поиска'

    await bot.send_message(m.chat.id, text, reply_to_message_id=m.message_id)


async def start(m):
    global searching_now
    if not searching_now:
        searching_now = True
        for i in itertools.product('12345', repeat=5):
            a.append(i[0] + i[1] + i[2] + i[3] + i[4])
        await bot.send_message(m.chat.id, '👌Начинаем поиск. Жду сообщения в формате:\n1) <b>"12345 2"</b>\n'
                                          '2) <b>"🍋🍇🍏🥕🍅<ПРОБЕЛ>2"</b>',
                               reply_to_message_id=m.message_id)
    else:
        await bot.send_message(m.chat.id, '❌Поиск смузи <b>уже стартовал</b>.\nОчистка - /clear',
                               reply_to_message_id=m.message_id)


async def searching(m, fruit_message):
    global a
    global _a
    global rules_list
    global combinations_list
    if searching_now:
        combinations_list = ''
        x_pt1 = fruit_message[0:5]
        try:
            x_pt2 = int(fruit_message[6])
            count = 0
            rules_list.append(fruit_message)
            for j in a:
                for i in range(0, 5):
                    if int(x_pt1[i]) == int(j[i]):
                        count += 1
                if x_pt2 == count - ((count - 1) - abs(count - 1)) // 2:
                    _a.append(j)
                    for k in j:
                        combinations_list += fruits[int(k)]
                    combinations_list += '\n'
                count = 0
            a = _a.copy()
            _a.clear()
        except Exception as err:
            print(err)
        if len(a) <= 20:
            if len(a) == 0:
                await bot.send_message(m.chat.id, '🧐Возможно, ты где-то ошибся и '
                                                  'все возможные решения свелись к нулю.\n'
                                                  'Попробуй бахнуть /clear и /start', reply_to_message_id=m.message_id)
            elif len(a) == 1:
                await bot.send_message(m.chat.id, '🎉 <b>Рецепт смузи найден!</b>\n\n      ' + combinations_list[0:5] + '\n\n'
                                                  '👉Сбросить результаты поиска: /clear')
            else:
                await bot.send_message(m.chat.id, '<b>Мы уже близко!\n</b>' +
                                       combinations_list + '\n' + str(len(a)) + ' возможных решений на данный момент',
                                       reply_to_message_id=m.message_id)
        else:
            await bot.send_message(m.chat.id, '🍹Вариантов сейчас: <b>' + str(len(a)) + '</b>\n\n'
                                              '👉Просмотр: /combinations', reply_to_message_id=m.message_id)
    else:
        await bot.send_message(m.chat.id, '‼️Поиск рецепта еще <b>не стартовал</b>.\n\n👉/start для начала',
                               reply_to_message_id=m.message_id)


async def rules(m):
    string = '<b>Список правил: </b>\n\n'
    for rule in rules_list:
        string += rule + '\n'
    await bot.send_message(m.chat.id, string, reply_to_message_id=m.message_id)


async def help(m):
    string = '<b>Список команд:</b>\n\n' \
             '👉/help - Этот список\n' \
             '👉/start Начало поиска\n' \
             '👉/rules - Список обработанных комбинаций\n' \
             '👉/combinations - Список возможных рецептов\n' \
             '👉/clear - Очистка списка решений\n\n' \
             'Для поиска смузи нужно нажать /start ' \
             'и отправлять сообщения в форматах:\n1) <b>"12345 N"</b>     или \n' \
             '2) <b>"🍋🍇🍏🥕🍅<ПРОБЕЛ>N"</b>, \nгде ' \
             '<b>12345</b> - порядковый номер фруктов при варке смузи, ' \
             'N - цифра от одного до пяти, ' \
             'количество совпадений при приготовлении смузи.\n\n' \
             'Фрукты: 🍋-1, 🍇-2, 🍏-3, 🥕-4, 🍅-5\n' \
             'N: Не очень - 1, неплохой - 2, хороший - 3, отличный - 4, шикарный - 5'
    await bot.send_message(m.chat.id, string, reply_to_message_id=m.message_id)


async def combinations(m):
    if combinations_list != '':
        try:
            await bot.send_message(m.chat.id, combinations_list + '\n' + str(len(a)) + ' возможных решений на данный момент',
                                   reply_to_message_id=m.message_id)
        except Exception:
            await bot.send_message(m.chat.id, 'Комбинаций очень много. Давай не будем захламлять чат? :)',
                                   reply_to_message_id=m.message_id)
    else:
        await bot.send_message(m.chat.id, 'Комбинаций еще нет.\n'
                                          'Для поиска смузи нужно нажать /start '
                                          'и отправлять сообщения в форматах:\n1) <b>"12345 N"</b>     или \n'
                                          '2) <b>"🍋🍇🍏🥕🍅<ПРОБЕЛ>N"</b>, \nгде '
                                          '<b>12345</b> - порядковый номер фруктов при варке смузи, '
                                          'N - цифра от одного до пяти, '
                                          'количество совпадений при приготовлении смузи.\n\n'
                                          'Фрукты: 🍋-1, 🍇-2, 🍏-3, 🥕-4, 🍅-5\n'
                                          'N: Не очень - 1, неплохой - 2, хороший - 3, отличный - 4, шикарный - 5',
                               reply_to_message_id=m.message_id)


@bot.on_message()
async def main(_, m):
    # print(m.text)
    if m.chat.id == -1001479156990 or m.chat.id == 506702351:
        if "/clear" in m.text:
            await clear(m)
        elif "/start" in m.text:
            await start(m)
        elif "/rules" in m.text:
            await rules(m)
        elif "/help" in m.text:
            await help(m)
        elif "/combinations" in m.text:
            await combinations(m)
        elif re.match(r'[1-5]{5} [1-5]', m.text):
            print('numbers!')
            await searching(m, m.text)
        elif re.match('[🍋🍇🍏🥕🍅]{5} [1-5]', m.text):
            fruit_message = re.match('[🍋🍇🍏🥕🍅]{5} [1-5]', m.text)
            print('fruits!')
            text = ''
            for i in fruit_message.group(0)[0:5]:
                if i == '🍋':
                    text += '1'
                elif i == '🍇':
                    text += '2'
                elif i == '🍏':
                    text += '3'
                elif i == '🥕':
                    text += '4'
                else:
                    text += '5'
            try:
                await searching(m, text + ' ' + fruit_message.group(0)[6])
                print(text + fruit_message.group(0)[6])
            except Exception:
                await bot.send_message(m.chat.id, '😡<b>Проверь синтаксис<b>.\n5 фруктов, пробел, цифра.')

            #for i in fruit_message.group(0)
        else:
            pass


bot.run()
