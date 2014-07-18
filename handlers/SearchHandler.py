# -*- coding:utf-8 -*-
'''
Created on 2013-12-7

@author: 振
'''
import time
import tornado.web

from core.storage import MongoStorage

def strftime(t):
    return time.strftime('%Y-%m-%d %H:%M',time.localtime(t))


class SearchHandler(tornado.web.RequestHandler):
    @property
    def invertedIndex(self):
        return self.application.invertedIndex
    
    @property
    def ranker(self):
        return self.application.ranker
    
    @property
    def autoCompleter(self):
        return self.application.autoCompleter
    
    @property
    def extendQuery(self):
        return self.application.extendQuery
    
    def get(self):
        query = self.get_argument("query", "");
        rankBy = self.get_argument("rankBy", "relevancy");
        if query == "":
            # 没有搜索关键字，返回主页
            self.render("index.html", title=u"微博搜索");
        else:
            # terms 是切分之后的词项，p是索引
            user,terms,p = self.invertedIndex.search(query)
            if p is None:
                count, docIDs = 0, []
            elif rankBy == 'relevancy':
                count, docIDs = self.ranker.rankByRelevancy(terms,p)
            elif rankBy == 'time':
                count, docIDs = self.ranker.rankByTime(terms,p)
            elif rankBy == 'hot':
                count, docIDs = self.ranker.rankByHot(terms,p)
            
            storage = MongoStorage()
            if user is not None:
                user = storage.getUserInfo(user)
            weibos = storage.getWeibos(docIDs)
            if storage.readHotQuery(query) is None:
                storage.saveHotQuery({'_id':query,'tf':10})
                self.autoCompleter.addNewQuery({'_id':query,'tf':10})
            storage.close()
            # 扩展相关搜索
            relatedQueries = self.extendQuery.search(query)
            self.render("result.html", title=u"微博搜索", query=query, rankBy=rankBy, user=user, count=count, weibos=weibos, relatedQueries=relatedQueries, strftime=strftime);
                
                