# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import logging

import MySQLdb
import MySQLdb.cursors
from pymongo import MongoClient
from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi

from items import JingDong


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    # 调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '123456', 'scrapyspider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, fav_nums, url_object_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql,
                            (item["title"], item["url"], item["create_date"], item["fav_nums"], item["url_object_id"]))
        self.conn.commit()
        return item


class MysqlTwistedPipeline(object):
    # 采用异步的机制写入mysql
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class ArticleImagePipeline(ImagesPipeline):
    # 下载图片的pipeline
    def item_completed(self, results, item, info):
        if 'front_image_url' in item:
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item


class SmartcranehubPipeline(object):
    def open_spider(self, spider):
        self.client = MongoClient('localhost', 27017)
        # 数据库和数据表，如果没有的话会自行创建
        self.db = self.client['SmartSpiderHubTest']
        self.collection = self.db['Lingshi']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):

        if not isinstance(item, JingDong):
            try:
                collection_name = self.getCollection(item['goods_brand'])
                old_item = self.db[collection_name].find_one({'goods_id': item['goods_id']})

                if old_item is None:
                    logging.info('items: ' + item['goods_id'] + ' insert in ' + collection_name + ' db.')
                    self.db[collection_name].insert(dict(item))
                elif self.needToUpdate(old_item, item):
                    self.db[collection_name].remove({'goods_id': item['goods_id']})
                    self.db[collection_name].insert(dict(item))
                    logging.info("items: " + item['goods_id'] + " has UPDATED in " + collection_name + " db.")
                else:
                    logging.info('items: ' + item['goods_id'] + ' has in ' + collection_name + ' db.')

            except Exception as e:
                logging.error("PIPELINE EXCEPTION: " + str(e))

        return item

    '''
     brand_list =
     ['乐事', '三只松鼠', '旺旺', '达利园', '百草味', '良品铺子', '盼盼', '奥利奥', '口水娃', '港荣', 
     '周黑鸭', '徐福记', '稻香村', '雀巢', '好丽友', '盐津铺子', '波力', '科尔沁', '蜀道香', '豪士', 
     '可比克', '来伊份', '劲仔', '嘉士利', '友臣', '葡记', '康师傅', '米多奇', '上好佳', '法丽兹', 
     '太平', '好想你', '好巴食', 'Aji', '咪咪', '源氏', '有友', '趣多多', '蒙都', '格力高']

    '''

    def getCollection(self, brand):
        if brand == '乐事':
            return 'Leshi'
        elif brand == '旺旺':
            return 'Wangwang'
        elif brand == '三只松鼠':
            return 'Sanzhisongshu'
        elif brand == '百草味':
            return 'Weilong'
        elif brand == '口水娃':
            return 'Koushuiwa'
        elif brand == '奥利奥':
            return 'Aoliao'
        elif brand == '良品铺子':
            return 'Liangpinpuzi'
        else:
            return 'Lingshi'

    def needToUpdate(self, old_item, new_item):
        if old_item['goods_price'] != new_item['goods_price']:
            old_time = old_item['goods_time']
            old_price = float(old_item['goods_price'])
            new_price = float(new_item['goods_price'])

            minus_price = round((new_price - old_price), 2)
            logging.info('Need To Update')

            if minus_price >= 0:
                new_item['goods_describe'] = '比 ' + old_time + ' 涨了 ' + str(minus_price) + ' 元。'
            else:
                new_item['goods_describe'] = '比 ' + old_time + ' 降了 ' + str(minus_price) + ' 元。'
            return True
        return False