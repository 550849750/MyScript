# encoding=utf-8
import re
import random
import nltk
from mysqlapi import MysqlApi
import time

# import sys, importlib
# import configparser
# import pymysql
# from urllib import parse
# # import json
# # import codecs
# # import jieba
# # import jieba.posseg
# # from textrank4zh import TextRank4Keyword, TextRank4Sentence
# # from pprint import pprint
# # import spid
# # from ci import chinese_stopwords
# # jieba.setLogLevel('WARNING')

# 获取db对象
db = MysqlApi()
# 待处理表名
TABLE = db.tables


def char_filter(char):
    """字符数据过滤"""
    char = char.strip()
    char = re.sub('(\.|—|\||_|\-)+[\w\W]*$', '', char)
    char = re.sub('(\[[\w\W]*?\])|(【[\w\W]*?】)|(#[\w\W]*?#)', '', char)
    return char


def char_handle(words):
    """字符处理器"""
    lst = []
    for word in words:
        word = char_filter(word)
        # 按标点符号拆分词组
        res = re.split(',|,|\?|？|！|!|：|:|；|;| ', word)
        lst.extend(res)

    tem = nltk.FreqDist(lst)
    # 按词频排序 [词条,词频值]
    tem = sorted(tem.items(), key=lambda x: x[1], reverse=True)
    title = ''
    # 词频最高的词条
    titles_maxfreq = []
    i = 0
    for row in tem:
        # 舍弃<5字符的内容
        if len(row[0]) < 5:
            continue
        if i == 0:
            # 取第一个满足条件的串为title
            title = row[0]
        elif i <= 3:
            # 词频前三\>=5字符\非title则加入该组
            titles_maxfreq.append(row[0])
        else:
            break
        i += 1

    tem2 = []
    for row in tem:
        # 记录每个词的(词条,词频,字符数)
        tem2.append((row[0], row[1], len(row[0])))
    # 按字符数排序
    tem2 = sorted(tem2, key=lambda x: x[2], reverse=True)

    # 取出最长的6个词条(排除第一条)
    titles_maxlen = []
    i = 0
    for row in tem2:
        if i == 0:
            i += 1
            continue
        titles_maxlen.append(row[0])
        i += 1
        if (i > 6):
            break

    offset2 = 0
    if len(tem2[0]) < (5 + offset2):
        offset2 = random.choice(range(len(tem2)))

    if len(tem2[offset2]) != 0:
        # 为title随机添加一条较长的词条
        title += ' ' + tem2[offset2][0]
    return title, titles_maxfreq, titles_maxlen


# 数据处理函数
def process(row, table):
    update_data = {}
    bd_titles = row['baidutitle'].split("\n")
    # title处理
    title, titles_maxfreq, titles_maxlen = char_handle(bd_titles)
    # 词频词组
    frequency_list = get_word_list(titles_maxfreq, 3, 'cp')
    update_data.update(frequency_list)
    # 长度词组
    length_list = get_word_list(titles_maxlen, 3, 'cd')
    update_data.update(length_list)
    # 相关词处理
    words = row['xgc'].split("\n")
    title, titles_maxfreq, titles_maxlen = char_handle(words)
    if len(titles_maxlen) > 1:
        related_list = get_word_list(titles_maxlen[1:], 3, 'xgc')
        update_data.update(related_list)

    # 添加处理标志
    update_data['is_worked'] = 1
    # 更新数据库
    db.update(table, 'Id={}'.format(row['Id']), update_data)


def get_word_list(words, num=3, prefix=''):
    """按需求数量返回字典值"""
    res = {}
    for i in range(num):
        if i < len(words):
            key = prefix + str(i + 1)
            res[key] = words[i]

    return res


def main():
    table_names = TABLE.split(',')
    for table in table_names:
        # 为表加上`is_worked`字段
        cursor = db.execute(
            "select count(*) as c from information_schema.columns where table_name=%s and column_name='is_worked';",
            (table,)).get_cursor()
        if not cursor:
            continue
        row = cursor.fetchone()
        if row['c'] == 0:
            db.execute(
                "ALTER TABLE " + table + " ADD `is_worked` INT(5) NOT NULL DEFAULT '0' AFTER `PageUrl`, ADD INDEX (`is_worked`);")
        # 取出数据进行处理
        cursor = db.execute(
            "select * from {} where is_worked=0 and baidutitle!='' limit 500;".format(table)).get_cursor()
        if not cursor:
            continue
        rows = cursor.fetchall()
        for row in rows:
            try:
                process(row, table)
            except Exception as e:
                db.execute("UPDATE " + table + " SET is_worked=-1 WHERE Id=%s;", (row['Id'],))
                print(e)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(5)
