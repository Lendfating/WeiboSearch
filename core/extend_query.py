#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2013-12-20

@author: 振
'''
import jieba
from storage import MongoStorage
from abstract_inverted_index import Posting, AbstractInvertedIndex

class ExtendQuery(AbstractInvertedIndex):
    def __init__(self):
        AbstractInvertedIndex.__init__(self)
        
    def initExtendQuery(self):
        def handler(item):
            synonyms = item['synonyms'];
            for synonym in synonyms:
                self.addPosting(item['_id'], Posting(synonym['word'], synonym['tf']))
                
        storage = MongoStorage()
        storage.handleSynonyms(handler)
        storage.close()
        
    
    def search(self, query):
        keys = jieba.cut_for_search(query)
        p = self._search(keys)
        result = []
        while p is not None:
            result.append(p.word)
            p = p.next
        return result;
    
if __name__ == "__main__":
    import sys
    reload(sys)
    exec("sys.setdefaultencoding('utf-8')");
    assert sys.getdefaultencoding().lower() == "utf-8";

    words = [{'word':'a','tf':12},{'word':'b','tf':1},{'word':'c','tf':234}]
    for term in words:
        for synonym in words:
            if term != synonym:
                print term['word'],
                print synonym['word'],
                print synonym['tf']
    
    
    
        