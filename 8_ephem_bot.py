"""
Домашнее задание №2 доп
4. не сделал
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
"""
    Задание 1
    Использование библиотек: ephem
    Реализуйте в боте команду /wordcount которая считает слова в присланной фразе.
    Например на запрос /wordcount Привет как дела бот должен ответить: 3 слова. Не забудьте:
    Добавить проверки на пустую строку
    Как можно обмануть бота, какие еще проверки нужны?
"""
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
"""
    Задание 2
    Реализуйте в боте команду, которая отвечает на вопрос
    “Когда ближайшее полнолуние?” Например /next_full_moon 2019-01-01. Чтобы узнать,
    когда ближайшее полнолуние, используйте ephem.next_full_moon(ДАТА)
"""
def next_full_moon(update, context):
    user_text = update.message.text
    now_data = dt.date.today()
    next_full_moon = ephem.next_full_moon(now_data).datetime().strftime('%d-%m-%Y в %H:%M')
    update.message.reply_text(f'Ближайшее полнолуние {next_full_moon}')


"""
Задание 3
Научите бота играть в города. Правила такие - внутри бота есть список городов, пользователь пишет /cities Москва и если
в списке такой город есть, бот отвечает городом на букву "а" - "Альметьевск, ваш ход".
Оба города должны удаляться из списка.
Помните, с ботом могут играть несколько пользователей одновременно
"""
def game_cities(update, context):
    cities_list =['Москва', 'Абакан', 'Новый волочек']
    if (context.user_data == {}) | (not context.user_data.get(update.message.chat.id)):
        context.user_data[update.message.chat.id] = {'bot_cities': cities_list,
                                                     'former_bot_cities': [],
                                                     'former_user_cities': []}
    # Проверка. Юзер ничего не ввел
    if context.args == []:
        update.message.reply_text(f'Ничего не введено!')  # ответ бота
        return
    # Проверка. Список бота пуст
    if context.user_data[update.message.chat.id]['bot_cities'] == []:
        update.message.reply_text(f'Я сдаюсь! Конец игры! \nНо могу начать заново')  # ответ бота
        context.user_data[update.message.chat.id]['bot_cities'] = cities_list
        return

    user_city = " ".join(context.args).lower().strip(" ").capitalize()
    former_user_cities = context.user_data[update.message.chat.id]['former_user_cities']
    bot_cities = context.user_data[update.message.chat.id]['bot_cities']
    former_bot_cities = context.user_data[update.message.chat.id]['former_bot_cities']

    # Проверка. Город юзера уже был задействован в игре
    if (user_city in former_user_cities) | (user_city in former_bot_cities):
        update.message.reply_text(f'Такой город уже был')  # ответ бота
        return
    # Проверка. Введенный город юзером отсутствует в списке бота
    if user_city not in bot_cities:
        update.message.reply_text(f'Такого города я не знаю, введи другой!')  # ответ бота
        return

    # Проверка. Город с неправильной первой буквой
    if former_bot_cities !=[]:
        if user_city[0].lower() != former_bot_cities[-1][-1]:
            update.message.reply_text(f'Караул!!! Первая буква должна быть {former_bot_cities[-1][-1]}')  # ответ бота
            return

    # Если город юзера в списке, то начинаем выбирать подходищий город из списка Бота.
    if user_city in bot_cities:
        end_letter_user_cities = user_city[-1]
        for bot_city in bot_cities:
            bot_city = bot_city.lower()
            # На случай если последний город из списка бота ввел пользователь. Здаемся, городов больше нет
            if (len(bot_cities) == 1) & (bot_cities[0].lower() == user_city.lower()):
                update.message.reply_text(f'Я сдаюсь! Конец игры! \nНо могу начать заново')  # ответ бота
                context.user_data.clear()
                return
            # Основной If. Печатаем ответ если первая буква города Бота совпадает с первой буквой города юзера
            if bot_city[0] == end_letter_user_cities:
                if user_city.lower() == bot_city:
                    continue
                update.message.reply_text(f'{bot_city.capitalize()}, ваш ход!')  # ответ бота
                former_bot_cities.append(bot_cities.pop(bot_cities.index(bot_city.capitalize())))
                former_user_cities.append(bot_cities.pop(bot_cities.index(user_city)))
                return
            # На случай если очередной город из списка не подошел по первой букве
            elif bot_city[0] != end_letter_user_cities:
                continue
            # На случай непредвиданного условия
            else:
                update.message.reply_text(f'Я сдаюсь! Конец игры! \nНо могу начать заново')  # ответ бота
                context.user_data.clear()
                return
    else:
        update.message.reply_text(f'Назовите еще город!')  # ответ бота
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
