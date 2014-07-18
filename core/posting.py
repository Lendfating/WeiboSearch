#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2013-12-5

@author: 振
'''

class Posting(object):
    '''
    倒排记录类
    '''
    def __init__(self, docID, tf, static_grade, time):
        """ 
            @describe: 构造函数，构造新倒排记录
            @param docID: 文档ID编号
            @param tf: 词项频率
            @param static_grade: 静态评分
            @param time: 微博发布时间  
        """
        self.docID = docID;     # 文档ID
        self.tf = tf;           # 词项频率（文档中该词项的频率）
        self.tfs = [tf]         # 以列表形式展示
        self.static_grade = static_grade; # 静态评分
        self.time = time;       # 微博发布时间
        self.next = None;       # next指针
    
    def __eq__(self, posting):
        """ 
            @describe: 重载比较运算符“=”，比较操作是基于“static_grade, docID”进行的
            @param posting: 待比较数据
        """
        return self.docID == posting.docID
    
    def __ne__(self, posting):
        """ 
            @describe: 重载比较运算符“!=”，比较操作是基于“static_grade, docID”进行的
            @param posting: 待比较数据
        """
        return self.docID != posting.docID
    
    def __lt__(self, posting):
        """ 
            @describe: 重载比较运算符“<”，比较操作是基于“static_grade, docID”进行的
            @param posting: 待比较数据
        """
        return (self.static_grade < posting.static_grade) or \
            (self.static_grade == posting.static_grade and self.docID < posting.docID)
            
    def __le__(self, posting):
        """ 
            @describe: 重载比较运算符“<=”，比较操作是基于“static_grade, docID”进行的
            @param posting: 待比较数据
        """
        return (self.static_grade < posting.static_grade) or \
            (self.static_grade == posting.static_grade and self.docID <= posting.docID)
            
    def __gt__(self, posting):
        """ 
            @describe: 重载比较运算符“>”，比较操作是基于“static_grade, docID”进行的
            @param posting: 待比较数据
        """
        return (self.static_grade > posting.static_grade) or \
            (self.static_grade == posting.static_grade and self.docID > posting.docID)
            
    def __ge__(self, posting):
        """ 
            @describe: 重载比较运算符“>=”，比较操作是基于“static_grade, docID”进行的
            @param posting: 待比较数据
        """
        return (self.static_grade > posting.static_grade) or \
            (self.static_grade == posting.static_grade and self.docID >= posting.docID)
    
    def hasSkip(self):
        """ 
            @describe: 根据属性skip是否存在，判断是否存在跳表指针
        """
        return hasattr(self, 'skip')
    
    def merge(self, posting):
        """ 
            @describe: 合并两个倒排记录 ，用于链表归并
        """
        return TempPosting(self.docID, self.tf, posting.tf, self.static_grade, self.time)
        

class TempPosting(Posting):
    '''
    链表合并时中间结果倒排记录类
    '''
    
    def __init__(self, docID, tf1, tf2, static_grade, time):
        """ 
            @describe: 构造函数，构造新倒排记录
            @param docID: 文档ID编号
            @param tf1: 初始词项频率1
            @param tf2: 初始词项频率2
            @param static_grade: 静态评分
            @param time: 微博发布时间  
        """
        Posting.__init__(self, docID, tf1, static_grade, time)
        self.tfs.append(tf2);
        
    def hasSkip(self):
        """ 
            @describe: 根据属性skip是否存在，判断是否存在跳表指针
        """
        return False;
    
    def merge(self, posting):
        """ 
            @describe: 合并两个倒排记录 ，用于链表归并
        """
        self.tfs.append(posting.tf)
        return self;
        
        