# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Match(scrapy.Item):
    date = scrapy.Field()
    t1 = scrapy.Field()
    s1 = scrapy.Field()
    t2 = scrapy.Field()
    s2 = scrapy.Field()
    pass
    # define the fields for your item here like:
    # name = scrapy.Field()