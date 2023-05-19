import logging
import sys
import os

import requests
# from dotenv import dotenv_values
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from exceptions import NoTokensError

# config = dotenv_values('.env')

# TOKEN = config.get('TOKEN')
TOKEN = os.getenv('TOKEN')

URL = 'https://yesno.wtf/api'

logging.basicConfig(
    handlers=[
        logging.FileHandler('main.log', 'w'),
        logging.StreamHandler(sys.stdout)
    ],
    format='%(asctime)s, %(levelname)s, %(message)s')


def check_tokens():
    """Проверка доступности переменной окружения."""
    return TOKEN


def get_answer():
    """Получения рандомной гифки-ответа."""
    try:
        response = requests.get(URL).json()
        random_answer = response.get('image')
    except requests.exceptions.RequestException as error:
        raise Exception(f'Ошибка запроса к эндпоинту API-сервиса: {error}')
    return random_answer


def new_answer(update, context):
    """Отправка ответа пользователю."""
    chat = update.effective_chat
    try:
        if not update.message.text:
            context.bot.send_message(
                chat.id,
                text='Что-то не то!..'
            )
        elif (update.message.text.endswith('?')
                and len(update.message.text) > 2):
            context.bot.send_video(chat.id, get_answer())
        elif not update.message.text.endswith('?'):
            context.bot.send_message(
                chat.id,
                text='А где знак ?'
            )
        elif len(update.message.text) <= 2:
            context.bot.send_message(
                chat.id,
                text='Слишком короткий запрос, непонятно!'
            )
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения из бота: {error}')


def wake_up(update, context):
    """Команда пробуждения бота."""
    chat = update.effective_chat
    text = 'Какие вопросы?!'
    context.bot.send_message(chat_id=chat.id, text=text)


def main():
    """Основная логика работы бота."""
    try:
        if not check_tokens():
            raise NoTokensError
    except NoTokensError as error:
        message = f'Отсутствует переменная окружения: {error}'
        logging.critical(message)
        sys.exit('Отсутствует переменная окружения')

    try:
        updater = Updater(token=TOKEN)

        updater.dispatcher.add_handler(CommandHandler('start', wake_up))
        updater.dispatcher.add_handler(MessageHandler(Filters.all, new_answer))

        updater.start_polling()
        updater.idle()
    except Exception as error:
        message = f'Сбой в работе программы: {error}'
        logging.error(message)


if __name__ == '__main__':
    main()
