# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

from scrapy.spider import BaseSpider

class BaseArticleSpider(BaseSpider):
    
    def __init__(self, *args, **kwargs):
        self.all = kwargs.get('all','1')