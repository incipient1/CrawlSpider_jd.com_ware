# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo.errors import DuplicateKeyError
from traceback import format_exc
from pymongo import MongoClient
from scrapy.conf import settings

class JdPipeline(object):
    def __init__(self,mongo_uri,mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
                    mongo_uri = crawler.settings.get('MongoDB_uri'),
                    mongo_db = crawler.settings.get('MongoDB_database','items')
                  )

    def open_spider(self,spider):
        _ = spider
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db['jd_info'].ensure_index('ware_id',unique = True)

    def process_item(self, item, spider):
        try:
            self.db.jd_info.update({'ware_id':item['ware_id']},
                    {'$set':item},upsert = True)

        except Exception as e:
            _ = e
            spider.logger.error(format_exc())
        except DuplicateKeyError:
            spider.logger.debug('duplicate key error collection')

        return item

    def close_spider(self,spider):
        _ = spider
        self.client.close()
        print('数据库关闭啦！')

