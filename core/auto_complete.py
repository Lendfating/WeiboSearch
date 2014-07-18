#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2013-12-20

@author: 振
'''

from storage import MongoStorage
from abstract_inverted_index import *

class AutoComplate(AbstractInvertedIndex):
    def __init__(self):
        AbstractInvertedIndex.__init__(self)
        
    def addNewQuery(self, query):
        word, tf = query['_id'], query['tf']
        keys = [word[:x] for x in xrange(1,len(word))]
        for key in keys:
            self.addPosting(key, Posting(word, tf))
        
    def initAutoComplate(self):                
        storage = MongoStorage()
        storage.handleHotQuerys(self.addNewQuery)
        storage.close()
        
    def search(self, query):
        p = self._search([query], 5)
        result = []
        while p is not None:
            result.append(p.word)
            p = p.next
        return result
    
        