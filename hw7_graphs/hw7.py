from flask import Flask
from flask import url_for, render_template, request, redirect
from flask import send_from_directory
import re
import gensim
import logging
import pandas as pd
import urllib.request
from gensim.models import word2vec
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import style
import networkx as nx
from networkx.algorithms import community
from networkx.algorithms.community import greedy_modularity_communities
import random
from random import sample
from random import randint
import matplotlib.colors as pltc
style.use('ggplot')
all_colors = [k for k, v in pltc.cnames.items()]



app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def index():
    first_word = 0
    g_den = 0
    g_dia = 0
    g_rad = 0
    g_ac = 0
    g_dpcc = 0
    g_dc = 0
    g_bc = 0
    g_cc = 0
    g_ec = 0
    n_o_e = 0
    n_o_n = 0
    c = []
    if request.args:
        text = request.args.get('text', '')
        wordtype = request.args.get('wordtype', '')
        download_r = request.args.get('download_r', '')
        if wordtype == 's':
            wordtype = '_S'
        if wordtype == 'a':
            wordtype = '_A'
        if wordtype == 'v':
            wordtype = '_V'
        # чтобы автоматически не скачивалось, но была такая возможность
        if download_r == 'y':
            urllib.request.urlretrieve("http://rusvectores.org/static/models/"
                                       "rusvectores2/ruscorpora_mystem_cbow_300"
                                       "_2_2015.bin.gz", "ruscorpora_mystem_cbow_300_2_2015.bin.gz")
        # не добавляя вручную часть речи не получается искать
        first_word = text + wordtype
        G = nx.Graph()
        m = 'ruscorpora_mystem_cbow_300_2_2015.bin.gz'
        model = gensim.models.KeyedVectors.load_word2vec_format(m, binary=True)
        # первые узлы - я не знаю как еще автоматизировать для любых слов
        words = []
        G.add_node(first_word)
        if first_word in model:
            print(first_word)
            for i in model.most_similar(positive=[first_word], topn=10):
                if i[0].endswith(wordtype):
                    print(i[0], i[1])
                    words.append(i[0])
                    G.add_node(i[0])
                    G.add_edge(first_word, i[0])
            print('\n')
            # узлы первого порядка
            lastwords = []
            for word in words:
                print(word)
                for i in model.most_similar(positive=[word], topn=10000):
                    if i[1] >= 0.5:
                        if i[0].endswith(wordtype):
                            print(i[0], i[1])
                            G.add_edge(word, i[0])
                            lastwords.append(i[0])
                print('\n')
            # узлы второго порядка
            over = []
            for w in lastwords:
                print(w)
                for i in model.most_similar(positive=[w], topn=10000):
                    if i[1] >= 0.5:
                        if i[0].endswith(wordtype):
                            print(i[0], i[1])
                            G.add_edge(w, i[0])
                            over.append(i[0])
                print('\n')

            # проверяем есть ли связь между узлами второго уровня
            for i in range(len(over)):
                for j in range(i + 1, len(over)):
                    if model.similarity(over[i], over[j]) >= 0.5:
                        G.add_edge(over[i], over[j])
            # вычисляем центральные узлы
            d = nx.degree_centrality(G)
            print(sorted(d.items(), key=lambda x: x[1], reverse=True))
            s = sorted(d.items(), key=lambda x: x[1], reverse=True)
            g_dc = 'Слово: ' + str(s[0][0]) + '; Коэффициент: ' + str(s[0][1])
            d = nx.betweenness_centrality(G)
            print(sorted(d.items(), key=lambda x: x[1], reverse=True))
            s = sorted(d.items(), key=lambda x: x[1], reverse=True)
            g_bc = 'Слово: ' + str(s[0][0]) + '; Коэффициент: ' + str(s[0][1])
            d = nx.closeness_centrality(G)
            print(sorted(d.items(), key=lambda x: x[1], reverse=True))
            s = sorted(d.items(), key=lambda x: x[1], reverse=True)
            g_cc = 'Слово: ' + str(s[0][0]) + '; Коэффициент: ' + str(s[0][1])
            d = nx.eigenvector_centrality(G)
            print(sorted(d.items(), key=lambda x: x[1], reverse=True))
            s = sorted(d.items(), key=lambda x: x[1], reverse=True)
            g_ec = 'Слово: ' + str(s[0][0]) + '; Коэффициент: ' + str(s[0][1])

            node_d = []
            g_den = nx.density(G)
            g_dia = nx.diameter(G)
            g_rad = nx.radius(G)
            g_ac = nx.average_clustering(G)
            g_dpcc = nx.degree_pearson_correlation_coefficient(G)
            n_o_e = G.number_of_edges()
            n_o_n = G.number_of_nodes()

            # цвет - сообщества
            # размер - количество связей
            pos = nx.spring_layout(G)

            # сообщества
            gmc = list(greedy_modularity_communities(G))
            c = []
            count = 0
            for frozenset in gmc:
                count += 1
                f = list(frozenset)
                c.append('Сообщество ' + str(count) + ': ' + str(f))
                colors = sample(all_colors, 100)
                node_d = []
                for i in frozenset:
                    node = i
                    node_d.append(G.degree(node)*20)
                nx.draw_networkx_nodes(G, pos, nodelist=frozenset,
                                       node_color=random.choice(colors),
                                       node_size=node_d)

            # создаем граф
            nx.draw_networkx_edges(G, pos, edge_color='black')
            nx.draw_networkx_labels(G, pos, font_size=8)
            plt.axis('off')
            nx.write_gexf(G, 'graph_file.gexf')
            save_results_to = 'static/'
            plt.savefig(save_results_to + 'image1.png', bbox_inches='tight')

            plt.show()

        else:
            first_word = 'Увы, слова "%s" нет в модели!' % first_word

    return render_template('index.html', first_word=first_word, g_den=g_den,
                           g_dia=g_dia, g_rad=g_rad, g_ac=g_ac, g_dpcc=g_dpcc,
                           g_dc=g_dc, g_bc=g_bc, g_cc=g_cc, g_ec=g_ec,
                           n_o_e=n_o_e, n_o_n=n_o_n, c=c)


if __name__ == '__main__':
    app.run(debug=False)

"""Хотя код написан для любого слова, смотрела я его на слове "фея"
Первое сообщество - профессии
Второе - в основном синонимы слова девушка
третье - волшебные всякие персонажи
4 - национальности
5 - ?????
6 - в основном цвет волос
7 - звания, титулы"""
