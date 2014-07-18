#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2013-12-18

@author: 振
'''
import math
from setting import sources_doc_number, top_K_number

class Ranker(object):
    '''
    排序函数，你实现下面的三种排序即可
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.docNumber = sources_doc_number;
        self.topK = top_K_number;
        
    def rankByRelevancy(self, row_terms, posting):
        """ 
            @describe: 根据相关度进行综合排序
            @param row_terms: 相关词项列表, 每一项是一个Term对象，Term的数据结构为：Term{dic,df}
            @param posting: 倒排词项链, 每一项为一个Posting对象，Posting的数据结构如下：
                                Posting{
                                    docID,        # 文档ID编号
                                    tfs[],        # 词项频率
                                    static_grade, # 静态得分
                                    time,         # 发布时间，时间戳格式
                                    next          # 下一项指针
                                }
                    note：terms数组和tfs数组顺序一致
            @return: 结果数量，排序后的docID列表
        """
        terms = []
        for i in xrange(0,len(row_terms)):
            terms.append(math.log10(self.docNumber/row_terms[i].df))  
        #tf--logtf
        
        post = posting
        count=0
        while post is not None:
            self.normalization(post.tfs)
            count=count+post.static_grade
            post = post.next
        # normalize the tfs of a doc; 
        items = []  #store the Item(docID,grade) List, used to sort
        docIDs= []  #store the Top k docID;
        count = math.sqrt(count) if count>0 else 1
        post  = posting
        
        while post is not None:
            similarity = 0
            for i in xrange(0,len(terms)):
                similarity = similarity + terms[i]*post.tfs[i]
            grade = post.static_grade/count + similarity
            items.append((post.docID,grade))
            post = post.next
        # normalize the static grade and then store <docID,endScore> in the items list 
        
        def f(data):
            return data[1]
        
        items.sort(cmp=None, key=f, reverse=True)
        length = len(items)
        for i in xrange(0,min(length,self.topK+1)):
            docIDs.append(items[i][0])
            
        return length, docIDs
    
    def rankByTime(self, terms, posting):
        """ 
            @describe: 根据微博发布时间进行排序
            @param terms: 相关词项列表, 每一项是一个Term对象，Term的数据结构为：Term{dic,df}
            @param posting: 倒排词项链, 每一项为一个Posting对象，Posting的数据结构如下：
                                Posting{
                                    docID,        # 文档ID编号
                                    tfs[],        # 词项频率
                                    static_grade, # 静态得分
                                    time,         # 发布时间，时间戳格式
                                    next          # 下一项指针
                                }
                    note：terms数组和tfs数组顺序一致
            @return: 结果数量，排序后的docID列表
        """
        items = []
        docIDs= []
        while posting is not None:
            items.append((posting.docID,posting.time))
            posting = posting.next
        
        def f(data):
            return data[1]
        items.sort(cmp=None, key=f, reverse=True)
        length = len(items)
        for i in xrange(0,min(self.topK+1,length)):
            docIDs.append(items[i][0])
        return length, docIDs
    
    def rankByHot(self, terms, posting):
        """ 
            @describe: 根据热点进行排序
            @param terms: 相关词项列表, 每一项是一个Term对象，Term的数据结构为：Term{dic,df}
            @param posting: 倒排词项链, 每一项为一个Posting对象，Posting的数据结构如下：
                                Posting{
                                    docID,        # 文档ID编号
                                    tfs[],        # 词项频率
                                    static_grade, # 静态得分
                                    time,         # 发布时间，时间戳格式
                                    next          # 下一项指针
                                }
                    note：terms数组和tfs数组顺序一致
            @return: 结果数量，排序后的docID列表
        """
        docIDs=[]
        i=0
        while posting is not None:
            if  i < self.topK:
                docIDs.append(posting.docID)
            i=i+1
            posting = posting.next
        return i, docIDs
    
    def normalization(self,tfsList):  # log and normalization
        length=0 
        for i in xrange(0,len(tfsList)):
            length = length + (1+math.log10(tfsList[i]))*(1+math.log10(tfsList[i]))
        length=math.sqrt(length)
        for i in xrange(0,len(tfsList)):
            tfsList[i]=(1+math.log10(tfsList[i]))/length
        
        
        
if __name__ == "__main__":
    from term import Term
    from posting import Posting
    terms=[Term(100),Term(10),Term(1)]
    posting4 = Posting('doc4',[1,1,2],100,0.001,None)
    posting3 = Posting('doc3',[2,1,2],200,0.003,posting4)
    posting2 = Posting('doc2',[2,2,2],110,0.004,posting3)
    posting  = Posting('doc1',[3,3,3],900,0.005,posting2)
    temp = Ranker()
    docid = temp.rankByRelevancy(terms, posting)
    for doc in docid:
        print doc
    #just for test
    