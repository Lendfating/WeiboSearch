# -*- coding:utf-8 -*-
'''
Created on 2013-12-7

@author: 振
'''
import tornado.web
from core.storage import MongoStorage

class GetUserHandler(tornado.web.RequestHandler):
    def get(self):
        nickname = self.get_argument("nickname");
        storage = MongoStorage()
        user = storage.getUserInfo(nickname)
        storage.close()
        if user is not None:
            self.write({'state':'ok','data':user}) 
        else:
            self.write({'state':'error'})