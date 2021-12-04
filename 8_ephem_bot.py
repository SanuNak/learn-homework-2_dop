"""
Домашнее задание №1

Использование библиотек: ephem
1.
Реализуйте в боте команду /wordcount которая считает слова в присланной фразе.
Например на запрос /wordcount Привет как дела бот должен ответить: 3 слова. Не забудьте:
Добавить проверки на пустую строку
Как можно обмануть бота, какие еще проверки нужны?
------------
2.
Реализуйте в боте команду, которая отвечает на вопрос
“Когда ближайшее полнолуние?” Например /next_full_moon 2019-01-01. Чтобы узнать,
когда ближайшее полнолуние, используйте ephem.next_full_moon(ДАТА)
-----------
3.
Научите бота играть в города. Правила такие - внутри бота есть список городов, пользователь пишет /cities Москва и если
в списке такой город есть, бот отвечает городом на букву "а" - "Альметьевск, ваш ход".
Оба города должны удаляться из списка.
Помните, с ботом могут играть несколько пользователей одновременно
------------
4.
Научите бота выполнять основные арифметические действия с двумя числами:
сложение, вычитание, умножение и деление. Если боту дать команду /calc 2-3, он должен ответить “-1”.
Не забудьте обработать возможные ошибки во вводе: пробелы, отсутствие чисел, деление на ноль
Подумайте, как можно сделать поддержку действий с тремя и более числами

"""
import logging
import ephem
import datetime as dt

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import re
import setting

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

PROXY = {
    'proxy_url': setting.PROXY_URL,
    'urllib3_proxy_kwargs': {
        'username': setting.PROXY_USERNAME,
        'password': setting.PROXY_PASSWORD
    }
}

# Задание 1
def word_count(update, context):
    user_text = update.message.text
    if user_text.strip() != "/wordcount":
        user_text = re.sub(r'[^\w\s]', '', user_text) # убираем лишние символы
        split_word = user_text.strip(" ").split(" ") # разбиваем строку на слова
        split_word.remove("wordcount") # удаляем техническое слово
        cnt_word = len(split_word)
        # делаем красиво фразу
        if cnt_word < 5:
            update.message.reply_text(f'{cnt_word} слова')  # ответ бота
        else:
            update.message.reply_text(f'{cnt_word} слов')  # ответ бота
    else:
        update.message.reply_text(f'Ничего не введено')  # ответ бота

# Задание 2
def next_full_moon(update, context):
    user_text = update.message.text
    now_data = dt.date.today()
    next_full_moon = ephem.next_full_moon(now_data).datetime().strftime('%d-%m-%Y в %H:%M')
    update.message.reply_text(f'Ближайшее полнолуние {next_full_moon}')


# Задание 3
def game_cities(update, context):
    cities_list =['Москва', 'Кировск', 'Анапа', 'Новый волочек']
    if (context.user_data == {}) | (not context.user_data.get(update.message.chat.id)):
        context.user_data[update.message.chat.id] = {'bot_cities': cities_list,
                                                     'cities_user': context.args}
    else:
        context.user_data[update.message.chat.id]['cities_user'].append(
            " ".join(context.args).lower().strip(" ").capitalize()
                                                                        )
    if context.args == []:
        update.message.reply_text(f'Ничего не введено!')  # ответ бота
        return

    if context.user_data[update.message.chat.id]['bot_cities'] == []:
        update.message.reply_text(f'Я здаюсь! Конец игры! \n Но могу начать заново')  # ответ бота
        context.user_data[update.message.chat.id]['bot_cities'] = cities_list
        context.user_data[update.message.chat.id]['cities_user'] = []
        return

    user_city = context.user_data[update.message.chat.id]['cities_user'][-1]
    user_cities = context.user_data[update.message.chat.id]['cities_user']
    bot_cities = context.user_data[update.message.chat.id]['bot_cities']

    if user_city in bot_cities:
        end_letter_user_cities = user_city[-1]
        bot_cities.remove(user_city)
        if bot_cities == []:
            update.message.reply_text(f'Я здаюсь! Конец игры! \n Но могу начать заново')  # ответ бота
            context.user_data[update.message.chat.id]['bot_cities'] = cities_list
            context.user_data[update.message.chat.id]['cities_user'] = []
            return
        for bot_city in bot_cities:
            bot_city = bot_city.lower()
            if bot_city[0] == end_letter_user_cities:
                update.message.reply_text(f'{bot_city.capitalize()}, ваш ход!')  # ответ бота
                bot_cities.remove(bot_city.capitalize())
                return
            elif bot_city[0] != end_letter_user_cities:
                continue
            elif bot_cities[0].lower() == bot_city:
                update.message.reply_text(f'Я здаюсь! Конец игры! \n Но могу начать заново')  # ответ бота
                context.user_data[update.message.chat.id]['bot_cities'] = cities_list
                context.user_data[update.message.chat.id]['cities_user'] = []
                return
            else:
                update.message.reply_text(f'Я здаюсь! Конец игры!')  # ответ бота
                context.user_data[update.message.chat.id]['bot_cities'] = cities_list
                context.user_data[update.message.chat.id]['cities_user'] = []
    elif user_city in user_cities:
        update.message.reply_text(f'Такой город уже был')  # ответ бота
        return
    else:
        update.message.reply_text(f'Такого города не знаю, введите другой')  # ответ бота
        return

def greet_user(update, context):
    text = 'Вызван /start'
    update.message.reply_text(text)  # ответ бота


def talk_to_me(update, context):
    user_text = update.message.text
    update.message.reply_text(user_text)  # ответ бота


def ephem_answer(update, context):
    user_text = update.message.text
    update.message.reply_text("Определяем расположение планеты")

    if len(user_text.split(" ")) == 1:
        update.message.reply_text("Ничего не введено, введите имя планеты")

    elif len(update.message.text.split(" ")) > 1:
        user_planet = user_text.split()[1].lower().strip(" ").capitalize()
        ephem_answer = getattr(ephem, user_planet, "Эту планету еще не придумали")
        if isinstance(ephem_answer, type):
            ephem_answer = ephem_answer('2021/10/1')
            constellation = ephem.constellation(ephem_answer)
            update.message.reply_text(constellation)  # ответ бота
        else:
            update.message.reply_text(ephem_answer)


def main():
    # коммуникация с сервером Telegram
    mybot = Updater(setting.API_KEY, request_kwargs=PROXY, use_context=True)

    dp = mybot.dispatcher  # запускаем диспитчер, он определяет тип сообщения

    # если такая комманда есть, то обработч выполнит нашу функцию
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", ephem_answer))
    dp.add_handler(CommandHandler("wordcount", word_count))
    dp.add_handler(CommandHandler("next_full_moon", next_full_moon))
    dp.add_handler(CommandHandler("cities", game_cities))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    # Командуем боту начать ходить в Telegram за сообщениями
    mybot.start_polling()
    # Запускаем бота, он будет работать, пока мы его не остановим принудительно
    mybot.idle()


if __name__ == "__main__":
    main()
