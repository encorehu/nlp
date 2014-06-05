# -*- coding: utf-8 -*-

import re

from base import BaseExtractor, BaseRegexExtractor

class LinkExtractor(BaseRegexExtractor):
    regex = '<\s*[Aa]{1}\s+[^>]*?[Hh][Rr][Ee][Ff]\s*=\s*[\"\']?([/:_;=\w\&\?\%\+\-\.\(\)]+)[\"\']?\s*.*?>(.*?)</[Aa]{1}>'

    def extract(self, html):
        r=super(LinkExtractor, self).extract(html)
        return r

class MarkdownExtractor(BaseExtractor):
    errors=[]

    def extract(self, html, baseurl=None):

        def cut_tail_whitespaces(txt):
            line_list=txt.split('\n')
            result=[]
            for x in line_list:
                result.append(x.rstrip())
            return '\n'.join(result)

        if len(html)==0:
            return ''
        l1=len(html)
        data=[]
        piece='' # <> 之间的片段
        href_patten='href\s?=\s?[\'\"]?([#\w\-\:_/\.\&]+)[\'\"]?\s?'
        hp=re.compile(href_patten)
        url_href=''
        url_title=''
        url_text=''
        url_flag=False


        # 对x当前所处的位置的全局判断
        get_into_script_tag = False #是不是在script标记内
        get_into_style_tag  = False #是不是在style标记内

        text_flag  = True   # 数据标记

        start_tag  = False   # <
        end_tag    = False   # >


        script_start = False
        script_end   = False

        style_start  = False
        style_end    = False

        pre_flag = False


        # 一个一个字符开始探测, 可以称之为流式探测, string flow
        i=0
        for x in html:
            i=i+1
            #self.errors.append(x)

            if x == '<':

                start_tag = True   # 开始进入标签
                end_tag   = False  # 不是结束标签

                text_flag  = False  # 下一个x不是数据

                piece=''  # piece 不记录<>这两个符号,因为遇到<, 表示开始了一个新的piece, 这个时候piece重新开始记录<...>之间的符号
                #self.errors.append("标记开始了----".decode('cp936'))
                #print x,text_flag,repr(x)
                continue # (1)进入了标记, 开始下一个字符
            elif x == '>':
                text_flag  = True   # 下一个x可能是数据
                #print piece
                try:
                    piece=piece.split()[0] # pre class="prettyprint lang-py"  这种提取出pre
                except:
                    # piece = '' # 即, <> 内无字符的情况, 不进行后续的标记判断
                    self.errors.append(''.join([ x,i,'piece',repr(piece)]))
                    continue
                # 遇到> 表示piece 完全的结束了, 这个时候才是比较piece的最佳位置而不是在后面
                if piece.lower().startswith('script'):
                    get_into_script_tag   = True   # 已经找到一个script标记

                    script_start = True   # 脚本可以算作是开始了
                    script_end   = False  # 脚本还没有结束,因为没有发现</script>

                    text_flag     = False  # 脚本标记内的都不能算作数据

                    #print '进入Script区域'
                elif piece.lower()  =='/script':
                    get_into_script_tag   = False  # 即将要离开了script标记了, 所以为假

                    script_start = False  # 理由同上
                    script_end   = True   # 同上

                    text_flag     = True   # 可能要进入数据区
                    #print '离开script区域'
                elif piece.lower().startswith('style'):
                    get_into_style_tag   = True

                    style_start = True
                    style_end   = False

                    text_flag    = False

                    #print '进入style区域'

                elif piece.lower()  =='/style':
                    get_into_style_tag   = False

                    style_start = False
                    style_end   = True

                    text_flag     = True
                    #print '离开style区域'
                elif piece.lower() =='br /' or piece.lower() =='br ' or piece.lower() =='br' or piece.lower() == 'p' or piece.lower() == '/p':
                    #print piece*5
                    if pre_flag:
                        data.append('\n    ')
                    else:
                        data.append('\n')

                elif piece.lower().startswith('pre'):
                    #print piece*5
                    data.append('\n    ')
                    pre_flag = True

                elif piece.lower() == '/pre':
                    #print piece*5
                    data.append('\n    ')
                    pre_flag = False

                elif piece.lower()== 'a':
                    hrefs = hp.findall(piece)
                    if len(hrefs)==1:
                        if baseurl!=None:
                            if baseurl.startswith('http'):
                                url_href=buildnewurl(baseurl,hrefs[0])
                            else:
                                url_href= hrefs[0]
                        else:
                            url_href= hrefs[0]
                    #print piece*5
                    url_flag = True
                    data.append('[')


                elif piece.lower() == '/a':
                    #print piece*5
                    if url_href:
                        data.append('](%s)' % url_href)
                    else:
                        data.append(']')
                    url_flag = False
                    url_text = ''
                    url_href = ''



                elif piece.lower() == 'li':
                    #print piece*5
                    if pre_flag:
                        pass
                    else:
                        data.append(' - ')
                elif piece.lower() == '/li':
                    #print piece*5
                    if pre_flag:
                        data.append('\n    ')

                elif piece.lower() == 'em':
                    data.append('*')
                elif piece.lower() == '/em':
                    data.append('*')
                elif piece.lower() == 'strong':
                    data.append('**')
                elif piece.lower() == '/strong':
                    data.append('**')
                elif piece.lower() == 'h1':
                    data.append('\n# ')
                elif piece.lower() == '/h1':
                    data.append(' #\n')
                elif piece.lower() == 'h2':
                    data.append('\n## ')
                elif piece.lower() == '/h2':
                    data.append(' ##\n')
                elif piece.lower() == 'h3':
                    data.append('\n### ')
                elif piece.lower() == '/h3':
                    data.append(' ###\n')
                elif piece.lower() == 'h4':
                    data.append('\n#### ')
                elif piece.lower() == '/h4':
                    data.append(' ####\n')

                if get_into_script_tag:  # 如果x的上一个位置是脚本标签内, 那么
                    text_flag = False  # 脚本标记中的内容不是数据

                if get_into_style_tag:
                    text_flag = False

                start_tag = False  # 结束标记
                end_tag   = True


                #print 'piece:','-'*10,piece
                #self.errors.append("----标记结束了\n".decode('cp936'))
                #print x,text_flag,repr(x)
                continue
            else:  #(2)进入了标记内部 或者数据内部
                #piece+=x
                #print 'piece:',piece
                # 开始判断piece, 从而判断text_flag
                #print "可能是数据,也可能不是"


                # piece=其他的字符串的情况, 主要是 scr sc h ta table之类不完整的片段

                get_into_script_tag   = False
                get_into_style_tag    = False
                #text_flag             = False
                if start_tag: # 前面出现了< , 后面的x就是<之后, >之前的, 也就是<...>之间的数据, 因此, 不需要记录
                    #print 'text flag',text_flag
                    piece+=x

                if end_tag: # 前面结束标记 > 出现了,进入数据区了
                    # 这个时候, piece不用记录<...>之间的片段了
                    if script_start: # 找到了script 并且  那么就会进入script内部, 这些不是数据, 直接下一个字符
                        text_flag = False

                    if  style_start:# 找到了style 并且  那么就会进入script内部, 这些不是数据, 直接下一个字符
                        text_flag = False




                if text_flag:# >为真, < 为假, >...< 之间的才是数据
                    if pre_flag==True and x == '\n':
                        data.append('%s    ' % x)
                    else:
                        data.append(x)



        aaa=''.join(data).strip() \
              .replace('&nbsp;',' ') \
              .replace('&lt;','<')\
              .replace('&gt;','>')\
              .replace('&quot;','"') \
              .replace('&amp;','&') \
              .replace('&lsquo;',u'‘') \
              .replace('&rsquo;',u'’') \
              .replace('&ldquo;',u'“') \
              .replace('&rdquo;',u'”') \
              .replace('&hellip;',u'…') \
              .replace('&mdash;',u'—') \
              .replace('\r','\n') \
              .replace('\n\n\n','\n\n') \
              .replace('\n\n\n','\n\n')

        l2=len(aaa)
        #print repr(aaa)
        #print aaa
        return cut_tail_whitespaces(aaa)
