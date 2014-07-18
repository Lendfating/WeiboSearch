#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2013-12-5

@author: 振
'''
import math

from setting import high_list_max_length

class Term(object):
    '''
    词项类
    '''

    def __init__(self, index=0):
        """ 
            @describe: 词项构造函数，根据给定数据构造词典词项
            @param index: 词典压缩时，该词项对应的在词典中的位置（临时未使用）
        """
        #self.index = index;    # 词项指针，指向该单词在词典中单词串中的位置
        self.df = 0;            # 文档频率（document frequency）
        self.high_posting_list = None;  # 高端倒排记录表，降序存储，最大容量为high_list_max_length（1000）
        self.low_posting_list = None;   # 低端倒排记录表，降序存储
        
    def getWord(self):
        """ 
            @describe: 返回该词项对应的单词 （尚未使用）
        """
        return ""
    
    def addPosting(self, posting):
        """ 
            @describe: 向对应的倒排记录表中添加新倒排记录
            @param posting: 新倒排记录
            @note: 倒排记录表按降序组织，且此函数只在初始化构造倒排记录时才会调用，
                #对应的倒排记录先临时都填入高端链表，之后会用统一的链表整理阶段，再将多余的记录导入低端链表
        """
        if self.high_posting_list is None or posting>self.high_posting_list:
            # 将posting填在链表头
            posting.next = self.high_posting_list;
            self.high_posting_list = posting;
        else:
            # posting在之后的某个位置
            p = self.high_posting_list;
            while p.next is not None and p.next>posting:
                p = p.next;
            posting.next = p.next;
            p.next = posting;
        # 文档频率自动增加
        self.df += 1;
               
    def splitPostingList(self):
        """ 
            @describe: 将posting分割成两部分，高质量段放入高端倒排表，低质量部分放入低端倒排记录表
        """
        if self.df>high_list_max_length:
            i, p = 1, self.high_posting_list;
            while i<high_list_max_length:
                i += 1;
                p = p.next;
            self.low_posting_list = p.next;
            p.next = None;
            
    def generateSkips(self):
        """ 
            @describe: 生成跳表指针
            @note: 初始阶段未考虑文档使用信息，采用sqrt(L)作为间隔
        """
        def __generateSkips(list, gap):
            """ 以gap为间隔，自动为链表list生成跳表指针 """
            if gap < 5: # 间距太小的话就没必要建立跳表指针了
                return;
            current = list
            while True:
                i, p = 0, current;
                while i<gap and p.next is not None:
                    i += 1;
                    p = p.next;
                if i == gap:
                    current.skip = p;   # 跳表指针
                    current = p;
                else:
                    break;
        # 为高端表生成跳表指针，间距为sqrt(L)
        gap = int(math.sqrt(self.df)) if self.df<high_list_max_length else int(math.sqrt(high_list_max_length))
        __generateSkips(self.high_posting_list, gap)
        # 为低端表生成跳表指针，间距为sqrt(L)
        if self.df>high_list_max_length:
            gap = int(math.sqrt(self.df-high_list_max_length))
            __generateSkips(self.low_posting_list, gap)


if __name__ == "__main__":
    import sys
    reload(sys)
    exec("sys.setdefaultencoding('utf-8')");
    assert sys.getdefaultencoding().lower() == "utf-8";
     
    