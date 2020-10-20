# encoding:utf-8
from summaryparse import ParseSummary
import math


class Summary():

    def __init__(self):
        """获得一个摘要提取器"""
        self.parser = ParseSummary()

    def summary(self, text, phrases_num=2, sentence_num=15, **kwargs):
        """
        根据文章获取文本摘要并分段

        :param text:    文章内容

        :param phrases_num: 要拆分的段落数

        :param sentence_num: 每个段落需要取出的句子基数

        :param kwargs: 任意关键字参数
        :return:
        """
        if not kwargs:
            kwargs = {}
        # 定制参数
        kwargs['random_num'] = sentence_num * int(phrases_num)
        # 提取摘要
        sentence = self.parser.parse(text, **kwargs)
        sentences = str(sentence).split('。')
        sentences = list(map(lambda x: x + '。', sentences))
        # 向上取整
        split_idx = math.floor(len(sentences) / phrases_num)
        sections = []
        i = 0
        while True:
            if i < phrases_num:
                i += 1
                start = (i - 1) * split_idx
                end = i * split_idx
                section = ''.join(sentences[start:end]) if i < phrases_num else ''.join(sentences[start:])
                sections.append('<p>' + section + '</p>')
            else:
                break
        # 多段内容
        return "\n".join(sections)

# if __name__ == '__main__':
#     text = """
#     深圳资讯网消息 有一种安全感，叫做“我是中国人”。众所周知，安全感，成了中国的一张新名片。在中国，无论多晚都好，独自出门也不必担心人身安全，可以尽兴撸串，可以放心闲逛。就连外国朋友都表示在中国感到心安。今日，公安部新闻发言人李国忠表示，中国是公认的最有安全感国家之一，治安案件发现受理数同比下降12.4%。而这一句话引发网友热议，纷纷表示厉害了我的国!
#
#
#
# 　　9月23日，公安部举行新闻发布会，介绍开展打击文物犯罪和电信网络诈骗犯罪情况。公安部新闻发言人李国忠表示，今年前8个月，全国公安机关立刑事案件数同比下降6.2%，治安案件发现受理数同比下降12.4%。
#
# 　　“我国社会大局持续保持安全稳定，是世界上公认的最有安全感的国家之一。”李国忠表示，当前，针对人民群众反映强烈的文物犯罪、电信网络诈骗犯罪等突出问题，公安机关坚持重拳出击、露头就打，有的放矢地开展专项打击、集中整治，坚决把犯罪分子的嚣张气焰打下去，把人民群众的合法权益维护好。
#
# 　　他还表示，在全国机动车保有量达3.6亿辆，驾驶人近4.5亿的情况下，全国道路交通事故起数、死亡人数同比分别下降21.6%、34.6%。
#
# 　　李国忠介绍，今年8月31日，公安部再次会同国家文物局，部署开展为期一年的打击文物犯罪专项行动。9月4日，公安部对10名涉嫌重大文物犯罪在逃人员发布A级通缉令。各地公安机关闻令而动，一人一专班、一人一方案，通过分析研判、布控查缉、亲情劝投等措施，全力开展追捕工作。
#
# 　　在广大群众和新闻媒体的大力支持下，9月21日最后一名在逃犯罪嫌疑人向警方投案自首，至此10名A级通缉在逃人员全部到案，追缴了一大批国家文物，有些属于西周、东周、春秋时期，具有很高的历史、科学、艺术价值，实现了初战告捷。
#
# 　　李国忠表示，下一步，公安部要求各级公安机关进一步提升政治站位，进一步加大攻坚力度，充分运用大数据、人工智能等新技术、新手段，对文物犯罪组织者、出资者、实施者等人员，对盗窃、倒卖、走私等行为，依法实行全员、全链条严厉打击，坚决保护文物安全。
#
# 　　中国是公认的最有安全感国家之一，这也离不开国家高效有力的治理，带给人民群众强烈的安全感，而由此激发的社会共治积极性，又成为平安中国的坚强基石。在国家筑起的铜墙铁壁的护佑下，生活在这片土地的人们尽可安心、放心。
#
#     """
#     obj = Summary()
#     print(obj.summary(text))
