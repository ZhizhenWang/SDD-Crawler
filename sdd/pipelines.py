# -*- coding: utf-8 -*-
import pymongo
from sdd.items import SddItem, ReportItem, OrgItem
from scrapy.exceptions import DropItem


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MongoPipeline(object):
    collection_search = 'search_items'
    collection_org = 'org_items'
    collection_rep = 'report_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, SddItem):
            self.db[self.collection_search].insert_one(dict(item))
        elif isinstance(item, OrgItem):
            self.db[self.collection_org].insert_one(dict(item))
        elif isinstance(item, ReportItem):
            self.db[self.collection_rep].insert_one(dict(item))
        return item


class DuplicatesPipeline(object):
    def __init__(self):
        self.org_seen = set()
        self.report_seen = set()

    # duplicates filter
    def process_item(self, item, spider):
        if isinstance(item, OrgItem):
            if item['org_id'] in self.org_seen:
                raise DropItem('Duplicated organization found: {}'.format(item))
            else:
                self.org_seen.add(item['org_id'])
                replace_str(item)
                return item
        elif isinstance(item, ReportItem):
            if item['report_id'] in self.report_seen:
                raise DropItem('Duplicated report found: {}'.format(item))
            else:
                self.report_seen.add(item['report_id'])
                return item
        else:
            return item


def replace_str(item):
    for key, value in item.items():
        if value == 'Not provided':
            item[key] = None
