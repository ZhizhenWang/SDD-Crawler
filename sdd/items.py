# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SddItem(scrapy.Item):
    org_name = scrapy.Field()
    org_id = scrapy.Field()
    size = scrapy.Field()
    sector = scrapy.Field()
    country = scrapy.Field()
    region = scrapy.Field()
    reports = scrapy.Field()


class OrgItem(scrapy.Item):
    org_id = scrapy.Field()
    org_name = scrapy.Field()
    size = scrapy.Field()
    type = scrapy.Field()
    listed = scrapy.Field()
    sector = scrapy.Field()
    country = scrapy.Field()
    country_status = scrapy.Field()
    employees = scrapy.Field()
    revenue = scrapy.Field()
    community = scrapy.Field()
    stock = scrapy.Field()


class ReportItem(scrapy.Item):
    report_id = scrapy.Field()
    report_name = scrapy.Field()
    pub_year = scrapy.Field()
    report_type = scrapy.Field()
    adherence = scrapy.Field()
