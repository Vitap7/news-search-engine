# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo

class ChgovnewsPipeline(object):
    def __init__(self):
        self.mongo_client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.mongo_client['myNewsDB']
        self.collection = self.db['news_coll']
        self.collection.drop()
        self.cnt = 0
    def process_item(self, item, spider):

        d = dict(item)
        self.cnt += 1
        title = d['title']
        time = d['time']
        url = d['url']
        text = d['text']
        comment = d['comment']
        titleNtext = title+' '+text

        #print(title)

        data = {'No':self.cnt,'title':title,'time':time,'url':url,'text':text,'comment':comment,'titleNtext':titleNtext}

        # 数据写入
        self.collection.insert_one(data)

        return item