# encoding=utf-8
import re
import random
import nltk


class Title():
    """
    title处理
    """

    def process(self, row):
        """
        数据处理方法,返回内容更新字典

        :param row: 数据行

        :return:
        """
        data = {}
        bd_titles = row['baidutitle'].split("\n")
        # title处理
        title, titles_maxfreq, titles_maxlen = self.__char_handle(bd_titles)
        # 词频词组
        frequency_list = self.__get_word_list(titles_maxfreq, 3, 'cp')
        data.update(frequency_list)
        # 长度词组
        length_list = self.__get_word_list(titles_maxlen, 3, 'cd')
        data.update(length_list)
        # 相关词处理
        words = row['xgc'].split("\n")
        title, titles_maxfreq, titles_maxlen = self.__char_handle(words)
        if len(titles_maxlen) > 1:
            related_list = self.__get_word_list(titles_maxlen[1:], 3, 'xgc')
            data.update(related_list)
        return data

    def __char_filter(self, char):
        """字符数据过滤"""
        char = char.strip()
        char = re.sub('(\.|—|\||_|\-)+[\w\W]*$', '', char)
        char = re.sub('(\[[\w\W]*?\])|(【[\w\W]*?】)|(#[\w\W]*?#)', '', char)
        return char

    def __char_handle(self, words):
        """字符处理器"""
        lst = []
        for word in words:
            word = self.__char_filter(word)
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

    def __get_word_list(self, words, num=3, prefix=''):
        """按需求数量返回字典值"""
        res = {}
        for i in range(num):
            if i < len(words):
                key = prefix + str(i + 1)
                res[key] = words[i]

        return res
