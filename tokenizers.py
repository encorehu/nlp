#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Encore Hu, <huyoo353@126.com>'

import sys
import os
import time
start = time.time()

def _tokenize(textline):
    #print 'you call me'
    for x in textline:
        yield x

tokenize = _tokenize

class BaseChineseWordTokenizer(object):
    '''针对一行短语进行处理, 比如一行文本, 或者几个字组合成的短句子. '''
    def __init__(self, textline='', *args, **kwargs):
        self.textline = textline

    def __iter__(self):
        # 之类需要实现如何从行文本中提取token, 使用list, 或者 generator
        raise NotImplementedError

    def __call__(self):
        print 'you call me'

    def process_tokens(self, text, tokens):
        #for i,token in enumerate(tokens):
        #    print i,token
        # 如果传入了tokens, 即传入了有其他分词器处理后返回的tokens,
        # 那么对每一个token进行处理
        if tokens:
            ###print len(tokens)
            t=[]
            for token in tokens:
                if len(token)>1:# 不处理空的token和仅有一个字符的token
                    self.textline = token
                    for x in self: # 这里转到实例的迭代函数 tokenizer.__iter__()
                        t.append(x) #(list(self))
                else:
                    t.append(token)
            return t
        else:
            # 如果其他分词器未返回tokens, 则可能本分词器是第一个分词器,
            #则对传入的原始text数据进行分词.
            ###if not self.textline: # 即不为'', 或者none
            ###    self.textline = text
            self.textline = text
            return list(self) # list 操作调用本class的__iter__方法

class ChineseWordTokenizer(BaseChineseWordTokenizer):
    def __iter__(self):
        for x in self.textline:
            yield x



class ChineseWordWhitespaceTokenizer(BaseChineseWordTokenizer):
    '''空格分割器'''
    def __iter__(self):
        # split by whitespace
        for x in self.textline.split():
            yield x

class ChineseWordDotTokenizer(BaseChineseWordTokenizer):
    '''小数点分割, 不要用这个, 还没写好

    pass:
            1.2 2.3234
    split:
    2.
    a2.v
    '''
    #choices = '.'.decode('utf-8')
    #choices = list(choices)
    choices = ['.']


    def __iter__(self):
        # split by dot
        nflag=0 # 点后面的一个字符是不是数字
        tmp=[]
        length = len(self.textline)

        for i,x in self.textline:
            if x in self.choices:
                # 忽略标点符号, 并断开
                if i == 0:
                    continue # 点在最前面不管, 直接处理第二个字符
                else:
                    if i+1 < length:
                        pass # 明天再弄!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                yield ''.join(tmp) # 分开处, yield抛出分的部分结果
                tmp=[]
            else:
                tmp.append(x)
        if tmp:
            yield ''.join(tmp)

class ChineseWordPunctionTokenizer(BaseChineseWordTokenizer):
    # 去掉了小数点, 因为可能是小数中的点, 比如2.3, 因此小数点应该在数字处理完毕之后再去除
    # 目前准备放到小数之中处理
    # 去掉连字符 - 和 _
    Punction = ' ,/;\'[]\<>?:"{}|~!@#$%^&*()+=，。、；‘【】、《》？：“｛｝§·～！@#￥%……&*（）'.decode('utf-8')

    def __iter__(self):
        tmp=[]
        for x in self.textline:
            if x in self.Punction:
                # 忽略标点符号, 并断开
                yield ''.join(tmp) # 分开处, yield抛出分的部分结果
                tmp=[]
            else:
                tmp.append(x)
        if tmp:
            yield ''.join(tmp)

class ChineseWordBeforeTokenizer(BaseChineseWordTokenizer):
    '''在字符之前截断
    比如这里有2个人, 就从2个的2前面截断, 成为[这里有, 2个人]
    '''
    choices = '不把我和比或与非就'.decode('utf-8')

    def __iter__(self):
        nflag=0
        tmp=[]
        for x in self.textline:
            if x in self.choices: #当前字符是候选字符

                if nflag == 1: #前一个字符是候选字符, 则继续添加该字符
                    tmp.append(x)
                else: # 前一个字符不是数值, 那么就把这个东西从前一个字符的后面截断, 把前面的部分抛出
                    # 不过这个会将 统一, 同一 给分开.
                    yield ''.join(tmp) # 分开处, yield抛出分的部分结果
                    tmp=[]
                    tmp.append(x)
                nflag = 1
            else:#当前字符不是数值
                nflag = 0
                tmp.append(x)
        if tmp:
            yield ''.join(tmp)

class ChineseWordNumericTokenizer(BaseChineseWordTokenizer):
    '''字符前截断----数字之前断开, 数字之后还有数字, 从最开始的数字之前断开
    比如这里有2个人, 就从2个的2前面截断, 成为[这里有, 2个人]
    '''
    # 第经常和数字联系在一起, 比如第一, 第二第3名
    ###numbers = '.0123456789第〇一二三四五六七八九零壹贰叁肆伍陆柒捌玖十百千万亿拾佰仟两元钱块斤辆斗选'.decode('utf-8')
    numbers = '.0123456789第〇一二三四五六七八九零壹贰叁肆伍陆柒捌玖十块元角分厘'.decode('utf-8')

    def __iter__(self):
        nflag=0
        tmp=[]

        for i,x in enumerate(self.textline):
            if x =='.' and i == 0:
                continue # . 在第一个位置, 直接处理第二个

            if x in self.numbers:#当前字符是数值

                if nflag == 1:
                    #前一个字符是候选的数值, 则继续添加数值,
                    #比如不把九十八这种分开, 继续添加可选字符, 因为它们是同类或者它们经常联系在一起的
                    # 即:前后字符都是候选字符的处理
                    tmp.append(x)
                else: # 前一个字符不是数值, 那么就把这个东西从前一个字符的后面截断, 把前面的部分抛出
                    # 不过这个会将 统一, 同一 给分开.
                    yield ''.join(tmp) # 分开处, yield抛出分的部分结果
                    tmp=[]
                    tmp.append(x)
                nflag = 1
            else:#当前字符不是数值
                nflag = 0
                tmp.append(x)
        if tmp:
            yield ''.join(tmp)

class ChineseWordAfterTokenizer(BaseChineseWordTokenizer):
    '''在字符之后截断

    以的字为例子, 比如这里有个开心的人, 就从开心的后面截断, 成为[这里有个开心的, 人]

    不过, 这个会将 的确 的的确确 给错误分开.
    '''
    choices = list('于是的都有个性化了'.decode('utf-8'))

    def __iter__(self):
        nflag=0
        tmp=[]
        for x in self.textline:
            if x in self.choices:#当前字符是的

                if nflag == 1: #前一个字符是的
                    yield ''.join(tmp) # 分开处, yield抛出分的部分结果
                    tmp=[]
                    tmp.append(x)
                else: # 前一个字符不是的
                    tmp.append(x)
                    yield ''.join(tmp) # 分开处, yield抛出分的部分结果
                    tmp=[]
                nflag = 1
            else:#当前字符不是的
                nflag = 0
                tmp.append(x)
        if tmp:
            yield ''.join(tmp)

class ChineseWordDeTokenizer(BaseChineseWordTokenizer):
    '''在字符后截断

    以的字为例子, 比如这里有个开心的人, 就从开心的后面截断, 成为[这里有个开心的, 人]

    不过, 这个会将 的确 的的确确 给错误分开.
    '''
    choices = list('于是的都有个性化了吧'.decode('utf-8'))

    def __iter__(self):
        nflag=0
        tmp=[]
        for x in self.textline:
            if x in self.choices:#当前字符是的

                if nflag == 1: #前一个字符是的
                    yield ''.join(tmp) # 分开处, yield抛出分的部分结果
                    tmp=[]
                    tmp.append(x)
                else: # 前一个字符不是的
                    tmp.append(x)
                    yield ''.join(tmp) # 分开处, yield抛出分的部分结果
                    tmp=[]
                nflag = 1
            else:#当前字符不是的
                nflag = 0
                tmp.append(x)
        if tmp:
            yield ''.join(tmp)

class ChineseWordFamilyNameTokenizer(BaseChineseWordTokenizer):
    '''字符前截断
    比如这里有2个人, 就从2个的2前面截断, 成为[这里有, 2个人]
    '''
    choices = '王陈李张刘'.decode('utf-8')

    def __iter__(self):
        nflag=0
        tmp=[]
        for x in self.textline:
            if x in self.choices:#当前字符是数值

                if nflag == 1: #前一个字符是数值
                    tmp.append(x)
                else: # 前一个字符不是数值, 那么就把这个东西从前一个字符的后面截断, 把前面的部分抛出
                    # 不过这个会将 统一, 同一 给分开.
                    yield ''.join(tmp) # 分开处, yield抛出分的部分结果
                    tmp=[]
                    tmp.append(x)
                nflag = 1
            else:#当前字符不是数值
                nflag = 0
                tmp.append(x)
        if tmp:
            yield ''.join(tmp)



# 这里设置好需要使用的分词器, 将会按照顺序对待处理文本进行分词
# 长的先分成短的, 短的继续分到分词器无能为力为止.
TOKENIZER_CLASSES=[
    ChineseWordWhitespaceTokenizer, # 先根据空格(空格,制表符,换行回车符)进行分词
    ###ChineseWordNumericTokenizer,    # 然后把数值从数值的前面分开, 这个主要是想
    ChineseWordPunctionTokenizer,   # 然后根据标点符号分词
    ChineseWordNumericTokenizer,    # 然后把数值从数值的前面分开
    ChineseWordDeTokenizer,         # 然后把'的'从的后面分开
    #ChineseWordBeforeTokenizer,     # 然后在一些字符之前截断, 比如 与或非, 我你他

    #ChineseWordFamilyNameTokenizer, # 然后按照在姓氏前分开
]

class BaseHandler(object):
    def __init__(self):
        self._tokenizers = None
        self._load_tokenizer()

    def _load_tokenizer(self, tobeloadedclasses = TOKENIZER_CLASSES):
        tokenizers = []

        for tn_class in tobeloadedclasses:
            try:
                tn_instance = tn_class() # 实例化tokenizer
            except: # exceptions.MiddlewareNotUsed:
                print '%s init error' % tn_class.__name__
                continue

            if hasattr(tn_instance, 'process_tokens'):
                tokenizers.append(tn_instance.process_tokens)

        self._tokenizers = tokenizers

    def get_tokens(self, text):
        ###print len(self._tokenizers)
        tokens = []
        for tokenizer_method in self._tokenizers:
            #print tokenizer_method
            #print '-'*80
            tokens = tokenizer_method(text, tokens)
        #print ('/ '.join(tokens))

        ###for token in tokens:
        ###    if token:
        ###        yield token

        return tokens

if __name__ == '__main__':
    text ='''《疯狂的小鸟》是由来自越南的独立游戏开发者Dong Nguyen所开发的作品，游戏中玩家必须控制一只小鸟，跨越由各种不同长度水管所组成的障碍，而这只鸟其实是根本不会飞的……所以玩家每点击一下小鸟就会飞高一点，不点击就会下降，玩家必须控制节奏，拿捏点击屏幕的时间点，让小鸟能在落下的瞬间跳起来，恰好能够通过狭窄的水管缝隙，只要稍一分神，马上就会失败阵亡'''
    text = text.decode('utf-8')

    bh=BaseHandler()
    tokenize = bh.get_tokens
    r={}
    words_list = tokenize(text)
    print text
    print '-'*80
    print '/ '.join( words_list)


    for word in words_list:
        r[word]=r.get(word,0)+1


    length =len(r)
    print u'词语总数:',len(r)