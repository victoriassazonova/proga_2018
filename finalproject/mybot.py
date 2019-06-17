import telebot
import flask
import os
import random
import shelve
from telebot import types
import re
import gensim
import logging
import urllib.request
from gensim.models import word2vec
import random
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

app = flask.Flask(__name__)

TOKEN = os.environ["TOKEN"]
bot = telebot.TeleBot(TOKEN, threaded=False)

bot.remove_webhook()
bot.set_webhook(url="https://stormy-bastion-94812.herokuapp.com/bot")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Вот список комманд: \n"
                     + "/about — что я такое?,\n"
                     + "/commands — список команд,\n"
                     + "/lets_play - ИГРАТЬ,\n"
                     + "/death - Нажмите это, когда надоест,\n"
                     + "чтобы увидеть статистику")


@bot.message_handler(commands=['about'])
def tell_about_yourself(message):
    bot.send_message(message.chat.id, "Я бот, генерирующий предложения! \n"
                     + "@tudum_tss - написать моей создательнице")


@bot.message_handler(commands=['death'])
def tell_about_help(message):
    with open('winn.txt', 'r', encoding='utf-8') as winn:
        now = winn.read()
    with open('total.txt', 'r', encoding='utf-8') as total:
        then = total.read()
    thestring = []
    thestring = now + '/' + then
    bot.send_message(message.chat.id, "Отличная игра!\n"
                     + " Вы дали {} правильных ответов".format(thestring))


@bot.message_handler(commands=['commands'])
def tell_commands(message):
    bot.send_message(message.chat.id, "Вот список комманд: \n"
                     + "/about — что я такое?,\n"
                     + "/commands — список команд,\n"
                     + "/lets_play - ИГРАТЬ,\n"
                     + "/death - Нажмите это, когда надоест,\n"
                     + "чтобы увидеть статистику")


@bot.message_handler(commands=['lets_play'])
def tell_about_game(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Стругацкие')
    btn2 = types.KeyboardButton('бот')
    keyboard.add(btn1, btn2)
    rrrr, tttt = game()
    with open('side.txt', 'w', encoding='utf-8') as results:
        results.write(str(tttt))
    with open('total.txt', 'w', encoding='utf-8') as total:
        total.write(str(0))
    with open('winn.txt', 'w', encoding='utf-8') as winn:
        winn.write(str(0))
    bot.send_message(message.chat.id, rrrr, reply_markup=keyboard)


@bot.message_handler(func=lambda m: True)
def get_answer(message):
    with open('total.txt', 'r', encoding='utf-8') as total:
        now = int(total.read())
        now += 1
    with open('total.txt', 'w', encoding='utf-8') as total:
        total.write(str(now))
    if message.text == 'Стругацкие':
        jjjj = 0
    if message.text == 'бот':
        jjjj = 1
    with open('side.txt', 'r', encoding='utf-8') as res:
        tttt = int(res.read())
    if tttt == jjjj:
        with open('winn.txt', 'r', encoding='utf-8') as winn:
            now = int(winn.read())
            now += 1
        with open('winn.txt', 'w', encoding='utf-8') as winn:
            winn.write(str(now))
        bot.send_message(message.chat.id, "Угадали! \n"
                         + " Нажмите /death если надоело")
    if tttt != jjjj:
        bot.send_message(message.chat.id, "Не угадали! \n"
                         + " Нажмите /death если надоело")
    rrrr, tttt = game()
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Стругацкие')
    btn2 = types.KeyboardButton('бот')
    keyboard.add(btn1, btn2)
    with open('side.txt', 'w', encoding='utf-8') as results:
        results.write(str(tttt))
    bot.send_message(message.chat.id, rrrr, reply_markup=keyboard)


def game():
    decision = random.randint(0, 1)
    if decision == 0:
        with open("text_lined.txt", 'r', encoding='utf-8') as t:
            content = t.readlines()
            r_r = random.randint(0, 137804)
            exx = content[r_r]
            return exx, decision
    if decision == 1:
        with open("gen_text.txt", 'r', encoding='utf-8') as g:
            content = g.readlines()
            r_r = random.randint(0, 13484)
            exx = content[r_r]
            return exx, decision
            exx = content[r_r]
            return exx, decision


@app.route("/", methods=['GET', 'HEAD'])
def index():
    return 'ok'

# страница для нашего бота
@app.route("/bot", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


if __name__ == '__main__':
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
