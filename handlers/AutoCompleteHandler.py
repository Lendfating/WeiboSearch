# -*- coding:utf-8 -*-
'''
Created on 2013-12-7

@author: 振
'''
import tornado.web

class AutoCompleteHandler(tornado.web.RequestHandler):
    @property
    def autoCompleter(self):
        return self.application.autoCompleter
    
    def get(self):
        query = self.get_argument("query");
        if len(query)>0:
            data = self.autoCompleter.search(query)
        else:
            data = []
        self.write({'state':'ok','data':data})
        