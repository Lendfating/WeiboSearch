# -*- coding:utf-8 -*-
'''
Created on 2013-7-15

@author: 振
'''
import os.path
import tornado.web
import tornado.ioloop

from handlers.SearchHandler import SearchHandler
from handlers.AutoCompleteHandler import AutoCompleteHandler
from handlers.GetUserHandler import GetUserHandler
from core.inverted_index import InvertedIndex
from core.Ranker import Ranker
from core.auto_complete import AutoComplate
from core.extend_query import ExtendQuery

class Application(tornado.web.Application):   
    def __init__(self, invertedIndex, ranker, autoCompleter, extendQuery):
        # 定义路由解析规则
        handlers = [
            (r"/aj/user", GetUserHandler),
            (r"/aj/autoComlpete", AutoCompleteHandler),
            (r".*", SearchHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "views/templates"),
            static_path=os.path.join(os.path.dirname(__file__), "views/static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
        self.invertedIndex = invertedIndex
        self.ranker = ranker
        self.autoCompleter = autoCompleter
        self.extendQuery = extendQuery
        
if __name__ == "__main__":
    import sys
    reload(sys)
    exec("sys.setdefaultencoding('utf-8')");
    assert sys.getdefaultencoding().lower() == "utf-8";
    import sys 
    sys.path.append("../") 
    import jieba 
    jieba.load_userdict("data/nickname.txt") 
    
    # 初始化倒排记录表和排名器
    invertedIndex = InvertedIndex()
    invertedIndex.initInvertedIndex()
    ranker = Ranker()
    autoCompleter = AutoComplate()
    autoCompleter.initAutoComplate()
    extendQuery = ExtendQuery()
    extendQuery.initExtendQuery()
    application = Application(invertedIndex, ranker, autoCompleter, extendQuery)
    application.listen(8888)
    print "start listening..."
    tornado.ioloop.IOLoop.instance().start()
    