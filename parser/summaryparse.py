# -*- encoding:utf-8 -*-
from textrank4zh import TextRank4Sentence
import jieba
import random

jieba.setLogLevel('ERROR')


class ParseSummary():

    def __init__(self):
        """
        返回一个摘要提取器
        """
        self.tr4s = TextRank4Sentence()

    def parse(self, text, random_num=20, loop_num=2, period_length=4):
        """
        解析文章,提取摘要信息

        :param text: 文章内容

        :param random_num: 句子数量

        :param loop_num: 递归处理次数

        :param period_length: 断句时的最大句子数
        :return:
        """
        sentence = self.__new_sentence(text, random_num=random_num, loop_num=loop_num)
        summary = self.__result_sentence(sentence, period_length)
        return summary

    def __new_sentence(self, text, random_num=20, loop_num=2):
        """
        根据段落内容提炼摘要信息

        :param text: 文本内容

        :param random_num: 句子数随机值

        :param loop_num: 递归次数
        :return:
        """
        self.tr4s.analyze(text=text, source='all_filters')
        # random间距为5
        rand_start = int(random_num) - 5
        # 句子条数
        hit = random.randint(rand_start, random_num)
        sentences = self.tr4s.get_key_sentences(num=hit)
        sentences.sort(key=lambda x: x['weight'], reverse=True)
        phrases = []
        # 拆分成短语
        for sentence in sentences:
            res = str(sentence['sentence']).split('，')
            res = filter(lambda x: len(x) > 5, res)
            phrases.extend(res)

        new_phrases = list(set(phrases))
        new_phrases.sort(key=phrases.index)
        new_sentence = '。'.join(new_phrases)
        # 递归处理
        loop_num -= 1
        if loop_num > 0:
            next_random_num = len(phrases)
            new_sentence = self.__new_sentence(new_sentence, next_random_num, loop_num)

        return new_sentence

    def __result_sentence(self, text, period_length=4):
        """
        随机断句处理

        :param text:文本

        :param period_length: 最大句子数
        :return:
        """
        phrases = str(text).split('。')
        # 打乱句子顺序
        # random.shuffle(phrases)
        sentence = ''
        #
        period_start = int(period_length) - 1
        period_end = period_start + 2
        # 断句撞击值
        init = 1
        hit = random.randint(period_start, period_end)
        for i in range(len(phrases)):
            if init % hit == 0:
                hit = random.randint(period_start, period_end)
                init = 1
                sentence = '。'.join((sentence, phrases[i]))
            else:
                init += 1
                if sentence:
                    sentence = '，'.join((sentence, phrases[i]))
                else:
                    sentence = phrases[i]

        return sentence + '。'
