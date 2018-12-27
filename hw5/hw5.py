from flask import Flask
from flask import url_for, render_template, request, redirect
from flask import send_from_directory
import sqlite3
import os
import re
from pymystem3 import Mystem
app = Flask(__name__)


def dbcreation():
    conn = sqlite3.connect('mydata.db')
    c = conn.cursor()
    # создаем базу данных
    c.execute('CREATE TABLE IF NOT EXISTS paper(plain TEXT, \
    lemmas TEXT, link TEXT, title TEXT)')
    conn.commit()
    # добавляем в нее все тексты
    directory = os.walk('paper/plain')
    for root, dirs, files in directory:
        for file in files:
            if file.endswith('.txt'):
                path = os.path.join(root, file)
                r = re.search('paper/plain/(.*?)/(.*?)/', path)
                if r:
                    year = r.group(1)
                    month = r.group(2)
                ms = os.path.join("paper/lemmas/" + year + "/" +
                                  month + "/" + file)
                with open(path, 'r') as t:
                    x = t.read().strip()
                    f = open(ms, 'r')
                    y = f.read().strip()
                    r = re.search("@url (.*?)\n", x)
                    if r:
                        li = r.group(1)
                    r = re.search("@ti (.*?)\n", x)
                    if r:
                        ti = r.group(1)
                    c = conn.cursor()
                    c.execute('INSERT INTO paper VALUES (?, ?, ?, ?)',
                              (x, y, li, ti))
                    conn.commit()


# закоменнтировано, чтобы он не вносил всё каждый раз в БД заново
# наверное можно было бы делать проверку как то но..
'''dbcreation()'''


@app.route('/')
def index():
    list = []
    # лемматизируем запрос пользователя
    if request.args:
        text = request.args.get('text', '')
        m = Mystem()
        lemmas = m.lemmatize(text)
        str1 = (''.join(lemmas)).strip()
        conn = sqlite3.connect("mydata.db")
        c = conn.cursor()
        search = '%' + str1 + '%'
        # ищем его в леммах
        c.execute("SELECT * FROM paper WHERE lemmas LIKE ?", [search])
        for row in iter(c.fetchone, None):
            check = 0
            lt = row[1]
            lt_list = lt.split()
            first = lemmas[0]
            for i in lt_list:
                if i == first:
                    check = lt_list.index(i)
                    pl = row[0]
                    pl_list = pl.split()
                    for m in pl_list:
                        if m.startswith("https:"):
                            del pl_list[:pl_list.index(m) + 1]
                    # хочу вывод соседних, проверяю, есть ли столько в статье
                    if len(pl_list) >= check + 30 and check >= 30:
                        str2 = (' '.join(pl_list[check - 30:check + 30]))
                    if len(pl_list) < check + 30 and check < 30:
                        str2 = (' '.join(pl_list[0:len(pl_list)]))
                    if len(pl_list) >= check + 30 and check < 30:
                        str2 = (' '.join(pl_list[0:check + 30]))
                    if len(pl_list) < check + 30 and check >= 30:
                        str2 = (' '.join(pl_list[check - 30:len(pl_list)]))
                    """из-за того, что index возвращает первое вхождение,
                    он находит лемм. фразу, но с выводом проблемы, тк
                    выводится фрагмент по 1 вхождению 1 слова, а не всей фразы
                    как и только 1 вхождение одного слова следовательно тоже,
                    поэтому для поиска фразы я буду выводить весь текст,
                    тк либо так, либо не тот фрагмент"""
                    if len(lemmas) > 2:
                        str2 = (' '.join(pl_list[0:len(pl_list)]))
                    list.append(row[3])
                    list.append(row[2])
                    list.append(str2)
                    list.append("\n")

    return render_template('index.html', list=list)


if __name__ == '__main__':
    app.run(debug=False)
