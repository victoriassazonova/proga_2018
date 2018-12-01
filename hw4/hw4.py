import matplotlib.pyplot as plt
from matplotlib.patches import Shadow
import csv
import json
from flask import Flask
from flask import url_for, render_template, request, redirect
from flask import send_from_directory

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

filename = 'data.csv'
fieldnames = ("name", "age", "city", "q1", "q2")


@app.route('/')
def index():
    urls = {'главная': url_for('index'),
            'статистика': url_for('stats'),
            'json': url_for('jason'),
            ' поиск': url_for('search')}
    if request.args:
        name = request.args.get('name', '')
        age = request.args.get('age', '')
        city = request.args.get('city', '')
        if city == 'm':
            city = 'Москва'
        if city == 's':
            city = 'Санкт-Петербург'
        if city == 'd':
            city = 'Другое'
        q1 = request.args.get('q1', '')
        if q1 == 'a11':
            q1 = '[ч]'
        if q1 == 'a12':
            q1 = '[ш]'
        q2 = request.args.get('q2', '')
        if q2 == 'a21':
            q2 = '[ч]'
        if q2 == 'a22':
            q2 = '[ш]'
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            if name != '':
                writer.writerow([name, age, city, q1, q2])
                return redirect('/thanks')
    return render_template('index.html', urls=urls)


@app.route('/stats')
def stats():
    urls = {'главная': url_for('index'),
            'статистика': url_for('stats'),
            'json': url_for('jason'),
            ' поиск': url_for('search')}
    counter_1 = 0
    counter_2 = 0
    counter_3 = 0
    counter_4 = 0
    counter_5 = 0
    counter_6 = 0
    with open(filename, encoding='utf-8') as f:
        for line in f:
            a = line.split(',')
            if a[2] == 'Москва':
                if a[3] == '[ч]':
                    counter_1 += 1
                if a[3] == '[ш]':
                    counter_2 += 1
            if a[2] == 'Санкт-Петербург':
                if a[3] == '[ч]':
                    counter_3 += 1
                if a[3] == '[ш]':
                    counter_4 += 1
            if a[2] == 'Другое':
                if a[3] == '[ч]':
                    counter_5 += 1
                if a[3] == '[ш]':
                    counter_6 += 1
    fig1 = plt.figure(1, figsize=(8, 6))
    ax = fig1.add_axes([0.1, 0.1, 0.8, 0.8])
    labels = 'Москва, [ч]', 'Москва, [ш]', 'Санкт-Петербург, [ч]',\
             'Санкт-Петербург, [ш]', 'Другое, [ч]', 'Другое, [ш]'
    fracs = [counter_1, counter_2, counter_3, counter_4, counter_5, counter_6]
    explode = (0, 0.05, 0, 0, 0, 0)
    pies1 = ax.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%',
                   colors=['#c69c04', '#fbeeac', '#eedc5b',
                           '#ffff84', '#fafe4b', '#fffcc4'])
    save_results_to = 'static/'
    plt.savefig(save_results_to + 'image1.png', dpi=300)
    counter_7 = 0
    counter_8 = 0
    counter_9 = 0
    counter_10 = 0
    counter_11 = 0
    counter_12 = 0
    with open(filename, encoding='utf-8') as file:
        for line in file:
            a = line.strip().split(',')
            if a[2] == 'Москва':
                if a[4] == '[ч]':
                    counter_7 += 1
                if a[4] == '[ш]':
                    counter_8 += 1
            if a[2] == 'Санкт-Петербург':
                if a[-1] == '[ч]':
                    counter_9 += 1
                if a[-1] == '[ш]':
                    counter_10 += 1
            if a[2] == 'Другое':
                if a[-1] == '[ч]':
                    counter_11 += 1
                if a[-1] == '[ш]':
                    counter_12 += 1
    fig2 = plt.figure(2, figsize=(8, 6))
    ax = fig2.add_axes([0.1, 0.1, 0.8, 0.8])
    labels = 'Москва, [ч]', 'Москва, [ш]', 'Санкт-Петербург, [ч]',\
             'Санкт-Петербург, [ш]', 'Другое, [ч]', 'Другое, [ш]'
    fracs = [counter_7, counter_8, counter_9, counter_10,
             counter_11, counter_12]
    explode = (0, 0.05, 0, 0, 0, 0)
    pies2 = ax.pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%',
                   colors=['#c69c04', '#fbeeac', '#eedc5b',
                           '#ffff84', '#fafe4b', '#fffcc4'])
    save_results_to = 'static/'
    plt.savefig(save_results_to + 'image2.png', dpi=300)
    with open(filename, encoding='utf-8') as file:
        content = file.read().split('\n')
        return render_template("stats.html", content=content, urls=urls)


template = '{{"1": "{}", "2": "{}", "3": "{}", "4": "{}", "5": "{}"}}'
fieldnames = ("name", "age", "city", "q1", "q2")


@app.route('/jason')
def jason():
    urls = {'главная': url_for('index'),
            'статистика': url_for('stats'),
            'json': url_for('jason'),
            ' поиск': url_for('search')}
    with open("data.csv", "rt", encoding="utf-8") as f, \
            open("data.json", "wt", encoding="utf-8") as t:
        t.write("[\n")
        for row in csv.DictReader(f, fieldnames=fieldnames, delimiter=","):
            t.write(json.dumps(row, ensure_ascii=False, indent=4) + "\n")
        t.write("]")
    with open("data.json", encoding='utf-8') as file:
        content = file.read().split('\n')
        return render_template("json.html", content=content, urls=urls)


@app.route('/search')
def search():
    found = 0
    list = []
    urls = {'главная': url_for('index'),
            'статистика': url_for('stats'),
            'json': url_for('jason'),
            ' поиск': url_for('search')}

    if request.args:
        search = request.args.get('search', '')
        city = request.args.get('city', '')
        if city == 'm':
            city = 'Москва'
        if city == 's':
            city = 'Санкт-Петербург'
        if city == 'd':
            city = 'Другое'

        with open(filename, encoding='utf-8') as file:
            for line in file:
                if search in line:
                    if city in line:
                        found += 1
                        list.append(line)
        return render_template('results.html', found=found, urls=urls, list=list)
    return render_template('search.html', urls=urls)


@app.route('/thanks')
def thanks():
    urls = {'главная': url_for('index'),
            'статистика': url_for('stats'),
            'json': url_for('jason'),
            ' поиск': url_for('search')}
    return render_template('thanks.html', urls=urls)


@app.route('/results')
def results():
    urls = {'главная': url_for('index'),
            'статистика': url_for('stats'),
            'json': url_for('jason'),
            ' поиск': url_for('search')}
    return render_template('results.html', urls=urls)


if __name__ == '__main__':
    app.run(debug=False)
