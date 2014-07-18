#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 2012-10-23

@author: 振
'''
import os.path
from pymongo import MongoClient

# Mongo relative
mongo_host = None
mongo_port = None

class MongoStorage(object):
    def __init__(self):
        try:
            if mongo_host is not None or mongo_port is not None:
                self.client = MongoClient(mongo_host, int(mongo_port))
            else:
                self.client = MongoClient()
        except:
            print 'exception when connect to mongodb'
            raise
        
        self.db = self.client.weibo;
        
        self.users = self.db.users;
        self.weibos = self.db.weibos;
        self.postings = self.db.postings;
        self.nickNamePostings = self.db.nickNamePostings;
        self.querys = self.db.querys
        self.synonyms = self.db.synonyms
    
    def saveWeibo(self, weibo):
        self.weibos.save(weibo);
        
    def saveWeibos(self, weibos):
        self.weibos.insert(weibos);
        
    def getWeibo(self, id):
        weibo = self.weibos.find_one({"_id": id});
        return weibo;
    
    def getWeibos(self, ids):
        weibos = []
        for id in ids:
            weibos.append(self.weibos.find_one({"_id": id}))
        return weibos
        
    def handleWeibos(self, handler):
        """ 
            @describe: 处理所有微博。依次读取所有不重复的微博，并利用给定的处理句柄进行处理
            @param handler: 处理句柄
        """
        for weibo in self.weibos.find({"repeat": { "$exists": False }}, None, timeout=False):
            handler(weibo)
    
    def handleForwardWeibos(self, handler):
        """ 
            @describe: 转发微博处理。依次读取所有未重复的转发微博，并对其执行handler操作
            @param handler: 处理句柄
        """
        # 获得所有转发微博
        for weibo in self.weibos.find({"ri": None, "repeat": { "$exists": False }}, {"_id": True, "ri": True}, timeout=False):
            handler(weibo)
    
    def checkIsRepeat(self, id):
        """ 
            @describe: 检查某转发微博是否重复
            @param id: 待检查转发微博的原微博的mid
        """
        # 存在对应的原发微博或仍有其他未检查的来源相同的转发微博, 则有重复
        return self.weibos.find({"id": id}) is not None \
                or self.weibos.find({"ri":id, "repeat": { "$exists": False }}).count()>2
        
    def setRepeatWeibo(self, id):
        """ 
            @describe: 设置该微博重复
            @param id: 该转发微博自己的id
        """
        self.weibos.update({'_id':id},{ '$set': { 'repeat': True } });
        
    def savePostingList(self, postingList):
        """ 
            @describe: 将某个倒排记录表保存到磁盘
            @param postingList: 待保存的倒排记录表
        """
        self.postings.save(postingList);
        
    def saveNickNamePostingList(self, postingList):
        """ 
            @describe: 将某个nickname倒排记录表保存到磁盘
            @param postingList: 待保存的倒排记录表
        """
        self.nickNamePostings.save(postingList);
        
    def handlePostingLists(self, handler):
        """ 
            @describe: 处理所有倒排记录信息。依次读取所有倒排记录，并利用给定的处理句柄进行处理
            @param handler: 处理句柄
        """
        for postingList in self.postings.find({}, {"_id": False}, timeout=False):
            handler(postingList)
    
    def handleNickNamePostingLists(self, handler):
        """ 
            @describe: 处理所有nickname倒排记录信息。依次读取所有nickname倒排记录，并利用给定的处理句柄进行处理
            @param handler: 处理句柄
        """
        for nickNamePostingList in self.nickNamePostings.find({}, {"_id": False}, timeout=False):
            handler(nickNamePostingList)
        
    def loadFromDisk(self):
        """
            @describe: 根据磁盘是否有之前的信息记录，来确定是否从磁盘加载
        """
        return self.postings.find({}).count()>0
    
    def readHotQuery(self, query):
        """ 
            @describe: 更新热点查询信息（添加新查询记录）
            @param query: 待存储查询记录
        """
        return self.querys.find_one({"_id": query})
        
    def updateHotQuery(self, query):
        """ 
            @describe: 更新热点查询信息（添加新查询记录）
            @param query: 待存储查询记录
        """
        self.querys.update(query)
        
    def saveHotQuery(self, query):
        """ 
            @describe: 存储热点查询信息
            @param query: 待存储查询记录
        """
        self.querys.save(query)
            
    def handleHotQuerys(self, handler):
        """ 
            @describe: 热点查询处理。依次读取所有热点查询记录，并对其执行handler操作
            @param handler: 处理句柄
        """
        # 获得所有转发微博
        for query in self.querys.find({}, {"_id": True, "tf": True}, timeout=False):
            handler(query)
    
    def saveSynonyms(self, synonyms):
        """ 
            @describe: 存储近义词信息
            @param synonyms: 待存储近义词信息
        """
        self.synonyms.save(synonyms)
        
    def handleSynonyms(self, handler):
        """ 
            @describe: 同义词处理。依次读取所有同义词信息，并对其执行handler操作
            @param handler: 处理句柄
        """
        for item in self.synonyms.find({}, {"_id": True, "synonyms": True}, timeout=False):
            handler(item)
            
    def getUserInfo(self, nickname):
        """ 
            @describe: 尽力获取用户的基本信息，没有的话返回None
            @param nickname: 用户显示名
        """
        return self.users.find_one({'_id':nickname})
        
    def close(self):
        self.client.close()

class MongoManager(object):
    def __init__(self):
        self._id = 0;   # 用于缩短微博的本地id
    
    def _importData(self, dir):
        """ 
            @describe: 将制定目录下的微博数据导入mongo数据库
            @param dir: 原微博数据目录
        """
        import re
        pattern = re.compile(r'\w{6,10}')# 将正则表达式编译成Pattern对象
        p_nickname = re.compile(ur'@([\-_a-zA-Z0-9\u4e00-\u9fa5]+)')# 将正则表达式编译成Pattern对象
        for parent, dirnames, filenames in os.walk(dir):
            for filename in filenames:
                print "导入文件 %s" % filename;
                try:
                    f = open(os.path.join(parent, filename), 'r')
                    f.readline();   # 舍弃第一行的表头信息
                    lines = f.readlines();
                    print "文件 %s 供 %d 行信息" % (filename, len(lines))
                    for line in lines:
                        infos = line.split(',');
                        i = 0;
                        try:
                            # 本地话自维护的微博短ID
                            self._id += 1;
                            # 消息ID,<3480502457598982>
                            id = None if infos[i]=='' else int(infos[i]); i+=1;
                            # 用户ID,<2840053912>
                            ui = int(infos[i]); i+=1;
                            # 用户名,<2840053912>或<gemfansclub>
                            un = infos[i]; i+=1;
                            # 屏幕名,<给你一杯xX>
                            sn = infos[i]; i+=1;
                            # 用户头像,<http://tp1.sinaimg.cn/2840053912/50/40000340595/1>
                            while True:
                                iu = infos[i]; i+=1;
                                if iu.startswith('http'):
                                    break;
                                sn += ',%s' % iu;   # 分错了，将前一部分的还给前一部分
                            # 转发消息ID,<3479439268659225> 可能为''
                            ri = None if infos[i]=='' else int(infos[i]); i+=1;
                            # 消息内容,<天然水晶批发网 东海水晶批发 东海水晶批发网 东海水晶www.jingzhidu.com>
                            mt = infos[i]; i+=1;
                            # 消息URL,<yxMeFvSQe>
                            while True:
                                mu = infos[i]; i+=1;
                                if pattern.match(mu):   # 8-10个字母或数字组成的串（不一定对）
                                    break;
                                mt += ',%s' % mu;   # 分错了，将前一部分的还给前一部分
                            # 来源,<新浪微博>
                            srn = infos[i]; i+=1;
                            # 图片URL,<http://ww1.sinaimg.cn/bmiddle/8c617b99jw1dvzxr4oti5j.jpg>
                            while True:
                                pu = infos[i]; i+=1;
                                if pu=="" or pu.startswith('http'):
                                    break;
                                mt += ',%s' % mu;   # 分错了，将前一部分的还给前一部分
                                mu += ',%s' % srn;   # 分错了，将前一部分的还给前一部分
                                srn += ',%s' % pu;   # 分错了，将前一部分的还给前一部分
                            # 音频URL,<>
                            au = infos[i]; i+=1;
                            # 视频URL,<>
                            vu = infos[i]; i+=1;
                            # 转发数,<0>
                            rc = int(infos[i]); i+=1;
                            # 评论数,<0>
                            cc = int(infos[i]); i+=1;
                            # 发布时间,<1345299900>
                            ct = int(infos[i]); i+=1;
                            # @用户 <"@阿宝家的小猪,@枫留散,@陈祉璇s,@中华恐龙园,@">
                            nc, str = [], '';
                            while i<len(infos):
                                str += infos[i];
                                i += 1;
                            nc = [x.encode('utf-8') for x in p_nickname.findall(str.decode('utf-8'))]
                            if len(nc)>0:
                                pass
                            # 存储数据
                            self.storage.saveWeibo({'_id':self._id, 'id':id, 'ui':ui, 'un':un, 'sn':sn, 'iu':iu, 'ri':ri, 'mt':mt, 'mu':mu, 'srn':srn, 'pu':pu, 'au':au, 'vu':vu, 'rc':rc, 'cc':cc, 'ct':ct, 'nc':nc});
                        except Exception,e:
                            if len(infos)<6 or not infos[6].startswith("抱歉，此微博"):
                                print e
                                print "!!! ERROR : %s" % line
                finally:
                    f.close()

                
    def _checkRepeatData(self):
        """ 
            @describe: 检查所有重复出现的微博（原发和转发都存在、转发自同一个微博），并标记为“重复”
        """
        def handler(weibo):
            ''' 定义重复微博的检查处理规则 '''
            if self.storage.checkIsRepeat(weibo['ri']):
                # 重复微博进行标注处理
                self.storage.setRepeatWeibo(weibo['_id'])
                
        # 根据既定规则处理所有转发微博
        self.storage.handleForwardWeibos(handler)
        
    def importData(self):
        self.storage = MongoStorage()
        try:
            print "starting import data......"
            self._importData("D:\\raw_data")
            print 'succeed import all data ....' 
            
            print "starting check repeat data in the datebase......"
            self._checkRepeatData()
            print 'succeed handing all repeat data ....'
        finally:
            self.storage.close()
        
        
        
if __name__ == "__main__":
    import sys
    reload(sys)
    exec("sys.setdefaultencoding('utf-8')");
    assert sys.getdefaultencoding().lower() == "utf-8";
    
    command = input("输入命令：")
    if command == 1:    # 导入原始微博数据
        manager = MongoManager()
        manager.importData()
    elif command == 2:  # 生成nickname词典
        f = open("../data/nickname.txt", "w+")
        def handler(nickNamePostingList):
            f.write(nickNamePostingList['term']+' '+str(nickNamePostingList['df'])+"\r\n")
        storage = MongoStorage()
        storage.handleNickNamePostingLists(handler)
        storage.close()
        f.close()
    elif command == 3:  # 录入查询记录，用于查询自动补全
        f = open("../data/query.txt", "r")
        storage = MongoStorage()
        while 1:
            line = f.readline()
            if len(line) == 0:
                break
            items = line.split('\n')[0].split('\t')
            storage.saveHotQuery({'_id':items[0], 'tf':int(items[1])})
        storage.close()
        f.close()
    elif command == 4:  # 录入近义词信息，用于相关词扩展
        f = open("../data/synonyms.txt", "r")
        storage = MongoStorage()
        while 1:
            line = f.readline()
            if len(line) == 0:
                break
            items = line.split('\n')[0].split('\t')
            synonyms,i = [],0
            while 2*i+2<len(items):
                synonyms.append({'word': items[2*i+1], 'tf': float(items[2*i+2])})
                i += 1
            storage.saveSynonyms({'_id':items[0], 'synonyms':synonyms})
        storage.close()
        f.close()
    elif command == 5:  # 存储词项信息到txt
        f = open("../data/terms.txt", "w+")
        storage = MongoStorage()
        def handler(data):
            s = str(data['term'])
            high_list = data['highPostingList']
            low_list = data['lowPostingList']
            for item in high_list:
                s += '\t'+str(item['docID'])
            for item in low_list:
                s += '\t'+str(item['docID'])
            s += '\n'
            f.write(s)
        storage.handlePostingLists(handler)
        storage.close()
        f.close()
        
   
    