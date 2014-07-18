#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2013-12-5

@author: 振
'''
import math
import jieba
import operator 
from storage import MongoStorage

from term import Term
from posting import Posting

from setting import temp_list_min_length

class Link(object):
    ''' 包装链表操作 '''
    def __init__(self):
        self.head = None
        self.trail = None
        self.count = 0
        
    def append(self, node):
        if self.head is None:
            self.head = self.trail = node
        else:
            self.trail.next = node
            self.trail = self.trail.next
        self.count += 1

class InvertedIndex(object):
    '''
    词项词典类，简称词典
    '''

    def __init__(self):
        """ 
            @describe: 构造函数，初始化倒排记录表的每一部分
        """
        self.compress_vocabulary = "";  # 词汇表,所有单词都存储在里面，采用压缩词汇处理方式（临时未使用）
        self.terms = [];                # 词项列表，数组，对其构建索引（临时未使用）
        self.hash_vocabulary = {}       # 临时存放词项的哈希表。
        self.hash_nickname = {}         # 对用户名、@到的用户名建立倒排索引
        
        
    def __addPosting(self, term, posting):
        """ 
            @describe: 将新词项记录添加到临时倒排索引表中
            @param term: 词项，如：u"中国"
            @param posting: 此项记录
        """
        if not self.hash_vocabulary.has_key(term):
            # 对于新词，在词典中创建该词
            self.hash_vocabulary[term] = Term();
        # 将该倒排记录添加到对应的词项的链表中
        self.hash_vocabulary[term].addPosting(posting);
        
    def __addNickNamePosting(self, nickname, posting):
        """ 
            @describe: 将新nickname词项记录添加到nickname倒排索引表中
            @param nickname: nickname词项，如：u"李振"
            @param posting: 此项记录
        """
        if not self.hash_nickname.has_key(nickname):
            # 对于nickname，在词典中创建该词
            self.hash_nickname[nickname] = Term();
        # 将该倒排记录添加到对应的nickname链表中
        self.hash_nickname[nickname].addPosting(posting);
    
    def __normalization(self, docID, tokens, static_grade, time):
        """ 
            @describe: 对词条进行语言预处理，归一化，之后自动将归一化之后的词项添加到倒排索引中
            @param docID: 文档ID
            @param tokens: 文档中的所有词项
            @param static_grade: 文档的静态评分
            @param time: 微博发布时间
        """
        terms = {}  # 临时词典，用以存储该文档中的所有词及对应的tf
        for token in tokens:
            if token not in '‘~!@#$%^&*()_+{}|:"<>?`-=[]\;\',./ ！￥……（）——：“”《》？·【】、；‘’，。丶～→......的了是转发回复赞谢谢thttpV': 
                # 过滤掉特殊字符
                if not terms.has_key(token):    # 该文档中第一次出现的词
                    terms[token] = 1;
                else:
                    terms[token] += 1;
        # 将归一化之后的词项添加到倒排记录表
        for term in terms:
            self.__addPosting(term, Posting(docID, terms[term], static_grade, time))  # terms[term]中存储的是词项频率
            
    def __tokenization(self):
        """
            @describe: 词条化，对每篇文档词条化之后，自动对词条进行归一化、构建倒排处理
        """
        storage = MongoStorage()
        def handler(weibo):
            """ 处理微博 """
            tokens = jieba.cut_for_search(weibo['mt'])
            # 微博静态评分计算：a*log(转发数)+b*log(评论数)
            static_grade = math.log(weibo['rc']+1)+math.log(weibo['cc']+1)
            # 对生成的词条进行归一化处理
            self.__normalization(weibo['_id'], tokens, static_grade, weibo['ct'])
            # 添加nickname到nickname倒排链表
            nicknames = weibo['nc']
            nicknames.append(weibo['sn'])
            for nickname in nicknames:
                self.__addNickNamePosting(nickname, Posting(weibo['_id'], 1, static_grade, weibo['ct']))
            
        storage.handleWeibos(handler)
        storage.close()
        
    def __arrangePostingList(self, hash):
        """
            @describe: 整理倒排链表，包括高低端倒排表分配、跳表生成
        """
        for term in hash:
            # 根据文档静态评分将倒排记录表进行切分，并放入高低端倒排记录表
            hash[term].splitPostingList()
            # 生成跳表指针
            hash[term].generateSkips()
    
    def reGenerateInvertedIndex(self):
        """
            @describe: 根据原始文档上数据重新生成倒排记录表
        """
        # 1、对原始文档词条话处理，以生成初始倒排记录表
        self.__tokenization()
        # 2、对得到的初始倒排记录表进行整理
        self.__arrangePostingList(self.hash_vocabulary)
        self.__arrangePostingList(self.hash_nickname)
        # 3、对词典排序  hash好像不能排序
        # self.hash_vocabulary = sorted(self.hash_vocabulary.iteritems(), key=itemgetter(1), reverse=True)
        # self.hash_nickname = sorted(self.hash_nickname.iteritems(), key=itemgetter(1), reverse=True)
        
    def __saveInvertedIndex(self, hash, saveHandler):
        """
            @describe: 将倒排记录表保存在磁盘上
            @param hash: hash倒排记录表
            @param saveHandler: 磁盘保存操作句柄
        """
        for term in hash:
            # 0、初始化一个新postingList数据，每个postingList包括词项、文档频率、高端倒排记录表、低端倒排记录表
            postingList = {'term':term, 'df':hash[term].df, 'highPostingList':[], 'lowPostingList':[]}
            # 1、将高端倒排记录表保存到postingList
            p = hash[term].high_posting_list
            while p is not None:
                postingList['highPostingList'].append({'docID':p.docID, 'tf':p.tf, 'static_grade':p.static_grade, 'time':p.time})
                p = p.next
            # 2、将低端倒排记录表保存到postingList
            p = hash[term].low_posting_list
            while p is not None:
                postingList['lowPostingList'].append({'docID':p.docID, 'tf':p.tf, 'static_grade':p.static_grade, 'time':p.time})
                p = p.next
            # 3、保存postingList到磁盘    
            saveHandler(postingList)
        
        
    def saveInvertedIndex(self):
        """
            @describe: 依次将普通倒排记录表和nickname倒排记录表保存在磁盘上
        """
        storage = MongoStorage()
        self.__saveInvertedIndex(self.hash_vocabulary, storage.savePostingList)
        self.__saveInvertedIndex(self.hash_nickname, storage.saveNickNamePostingList)
        storage.close()
    
    def __loadInvertedIndex(self, hash, readHandler):
        """
            @describe: 从磁盘记录上加载之前保存的倒排记录表
            @param hash: hash倒排记录表
            @param readHandler: 磁盘读取操作句柄
        """
        def handler(postingList):
            """
                @describe: 将磁盘上的倒排记录表加载到内存
                @param postingList: 一项倒排记录表磁盘存储项，包括词项、文档频率、高低端倒排记录表
            """
            # 初始化
            term = postingList['term']
            df = postingList['df']
            highPostingList = postingList['highPostingList']
            lowPostingList = postingList['lowPostingList']
            # 定义倒排词项
            hash[term] = Term()
            hash[term].df = df
            # 高端倒排记录表整理
            if len(highPostingList)>0:
                link = Link()
                for posting in highPostingList:
                    link.append(Posting(posting['docID'], posting['tf'], posting['static_grade'], posting['time']))
                hash[term].high_posting_list = link.head
            # 低端倒排记录表整理
            if len(lowPostingList)>0:
                link = Link()
                for posting in lowPostingList:
                    link.append(Posting(posting['docID'], posting['tf'], posting['static_grade'], posting['time']))
                hash[term].low_posting_list = link.head
        # 1、从磁盘加载倒排索引信息到内存  
        readHandler(handler)
        # 2、为高低端表添加跳表指针
        for term in hash:
            hash[term].generateSkips()

        
    def loadInvertedIndex(self):
        """
            @describe: 从磁盘记录上依次加载普通排记录表和nickname倒排记录表
        """
        storage = MongoStorage()
        self.__loadInvertedIndex(self.hash_vocabulary, storage.handlePostingLists)
        self.__loadInvertedIndex(self.hash_nickname, storage.handleNickNamePostingLists)
        storage.close()
    
    def initInvertedIndex(self):
        """
            @describe: 初始化准备倒排记录表，根据需要选择是重新生成还是从磁盘中加载之前的
        """
        storage = MongoStorage()
        if storage.loadFromDisk():
            self.loadInvertedIndex()
        else:
            self.reGenerateInvertedIndex()
            self.saveInvertedIndex()
        storage.close()
    
    def __intersect(self, p1, p2, p2_low):
        """
            @describe: 倒排记录表合并操作
            @param p1: 倒排记录链表1的指针
            @param p2: 倒排记录链表2的高端表指针
            @param p2_low: 倒排记录链表2的低端表指针
        """
        if p1 is None:  # 初始情况
            return p2;
        
        answer, usingHigh = Link(), True;
        while p1 is not None and p2 is not None:
            if p1 == p2:
                answer.append(p1.merge(p2))
                p1 = p1.next
                # p2指针的移动需要考虑是否需要使用低端倒排链表
                if p2.next is None and usingHigh and answer.count<temp_list_min_length:
                    p2 = p2_low
                    usingHigh = False
                else:
                    p2 = p2.next
            elif p1 > p2:
                if p1.hasSkip() and p1.skip >= p2:
                    while p1.hasSkip() and p1.skip >= p2:
                        p1 = p1.skip;
                else:
                    p1 = p1.next
            else:
                if p2.hasSkip() and p2.skip >= p1:
                    while p2.hasSkip() and p2.skip >= p1:
                        p2 = p2.skip;
                else:
                    # p2指针的移动需要考虑是否需要使用低端倒排链表
                    if p2.next is None and usingHigh and answer.count<temp_list_min_length:
                        p2 = p2_low
                        usingHigh = False
                    else:
                        p2 = p2.next
        return answer.head
    
    def search(self, query):
        """
            @describe: 根据查询，合并倒排索引表进行超找工作
            @param query: 查询短语
        """
        keys = jieba.cut_for_search(query)
        user, terms = None, []
        for key in keys:
            if self.hash_nickname.has_key(key):
                user = key
                terms.append(self.hash_nickname[key])
            elif self.hash_vocabulary.has_key(key):
                terms.append(self.hash_vocabulary[key])
        # 按df先对answer排序，从而优化下面的归并操作
        terms.sort(key=operator.attrgetter('df'))
        p = None
        for term in terms:
            p = self.__intersect(p, term.high_posting_list, term.low_posting_list)
            if p is None:
                break
        return user,terms,p
    
    
if __name__ == "__main__":
    import sys
    reload(sys)
    exec("sys.setdefaultencoding('utf-8')");
    assert sys.getdefaultencoding().lower() == "utf-8";

    inveredIndex = InvertedIndex()
    inveredIndex.initInvertedIndex()
    users,terms,p = inveredIndex.search("给力朋友")
    users,terms,p = inveredIndex.search("放弃质量")
    print "finish all work..."
    
    
    
    

            
            
            
            
            
            
            
        