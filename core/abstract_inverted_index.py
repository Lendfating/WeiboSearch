#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2013-12-21

@author: 振
'''

class Term(object):
    def __init__(self):
        self.df = 0;
        self.posting_link = None;
    
    def addPosting(self, posting):
        """ 
            @describe: 向对应的倒排记录表中添加新倒排记录
            @param posting: 新倒排记录
            @note: 倒排记录表按tf降序组织，且此函数只在初始化构造倒排记录时才会调用
        """
        if self.posting_link is None or posting.tf>self.posting_link.tf:
            # 将posting填在链表头
            posting.next = self.posting_link;
            self.posting_link = posting;
        else:
            # posting在之后的某个位置
            p = self.posting_link;
            while p.next is not None and p.next.tf>posting.tf:
                p = p.next;
            posting.next = p.next;
            p.next = posting;
        # 文档频率自动增加
        self.df += 1;
        
class Posting(object):
    def __init__(self, word, tf):
        self.word = word
        self.tf = tf
        self.next = None
    
    def copy(self):
        """ 
            @describe: 获取副本
        """
        return Posting(self.word, self.tf)
    
    def __eq__(self, posting):
        """ 
            @describe: 重载比较运算符“=”
            @param posting: 待比较数据
        """
        return self.word == posting.word
    
    def __lt__(self, posting):
        """ 
            @describe: 重载比较运算符“<”
            @param posting: 待比较数据
        """
        return self.tf < posting.tf
            
    def __gt__(self, posting):
        """ 
            @describe: 重载比较运算符“>”
            @param posting: 待比较数据
        """
        return self.tf > posting.tf
        
class AbstractInvertedIndex(object):
    '''
    抽象倒排索引表，用于自动补全和查询扩展的实现
    不同于基本倒排索引表，该索引表是一种很基本的索引表，没有采用高低端表、跳表指针等方法
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.hash_vocabulary = {}       # hash词典表
        
    def addPosting(self, term, posting):
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
        
        
    def __union(self, p1, p2, max_length=10):
        """
            @describe: 倒排记录表合并操作(并集)
            @param p1: 倒排记录链表1的指针
            @param p2: 倒排记录链表2的指针
            @param max_length: 结果集的最大长度
        """
        
        class Link(object):
            ''' 包装链表操作 '''
            def __init__(self):
                self.head = None
                self.trail = None
                self.size = 0
                
            def addPosting(self, posting):
                assert self.size <= max_length , "result is full!"
                copy = posting.copy()
                if self.head is None:
                    self.head = self.trail = copy
                else:
                    self.trail.next = copy
                    self.trail = self.trail.next
                self.size += 1
                    
        answer = Link();
        try:
            while p1 is not None and p2 is not None:
                if p1 == p2:
                    answer.addPosting(p1)
                    p1 = p1.next
                    p2 = p2.next
                elif p1 > p2:
                    answer.addPosting(p1)
                    p1 = p1.next
                else:
                    answer.addPosting(p2)
                    p2 = p2.next
            while p1 is not None:
                answer.addPosting(p1)
                p1 = p1.next
            while p2 is not None:
                answer.addPosting(p2)
                p2 = p2.next
        except AssertionError:  
            pass
        
        return answer.head
    
    def _search(self, keys, max_length=10):
        """
            @describe: 根据查询，合并倒排索引表进行超找工作
            @param query: 查询短语
        """
        p = None
        for key in keys:
            if self.hash_vocabulary.has_key(key):
                p = self.__union(p, self.hash_vocabulary[key].posting_link, max_length)
        return p

