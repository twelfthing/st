# -*- coding: utf-8 -*-
import re
import sys
import time
import json
import urlparse
import hashlib
import requests
from lxml import etree
from datetime import datetime
from StringIO import StringIO
from cds.spiders import BaseArticleSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.http.response.text import TextResponse

from twisted.internet import defer,reactor


class NoIdClass(Exception):
    pass

 
        
           
class WeiXinArticle(BaseArticleSpider):
    
    name = "weixin"
    
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0'
    
    cookies = {'SUID':'B96EE7746B20900A0000000055DD1DFF','PHPSESSID':'bjmqfvbvgaa5nm50o320cpbae6','SUIR':'1440554495','SUV':'000675F974E76EB955DD1DFF4D74C784'}

    start_urls = ['http://weixin.sogou.com/gzh?openid=oIWsFt3yiHypGkIxXlQG0b82p8xw','http://weixin.sogou.com/gzh?openid=oIWsFt1j96X46FRTNI4rm4-ZhAT0',\
                      'http://weixin.sogou.com/gzh?openid=oIWsFt4hXrM5dp8RoGjPriYFdU8M','http://weixin.sogou.com/gzh?openid=oIWsFt6KUV9U97HDz5mivHFJ1a6E',\
                      'http://weixin.sogou.com/gzh?openid=oIWsFt5G-Y0nP19GtbRoiaP9wru8','http://weixin.sogou.com/gzh?openid=oIWsFt3KsahZCDRJW8u7vugcMGaQ',\
                      'http://weixin.sogou.com/gzh?openid=oIWsFt-o_Zjia048kQnkJ9mOpWKs','http://weixin.sogou.com/gzh?openid=oIWsFt-Act8nltEKnIMfZ_UOiHtM',\
                      'http://weixin.sogou.com/gzh?openid=oIWsFt7N3poQ0cPpLgZqFVBSpLoc','http://weixin.sogou.com/gzh?openid=oIWsFt8r8wyZjIN3DhX_veXMbr-0']
    
    start_urls = ['http://weixin.sogou.com/gzh?openid=oIWsFt3yiHypGkIxXlQG0b82p8xw']

    download_delay = 1
    
    #max_concurrent_requests = 1
    

    def parse(self, response):
        for i in response.headers.getlist('Set-Cookie'):
            if 'SNUID' in i:
                self.cookies['SNUID'] = i.split('=')[1].split(';')[0]
                break
        x = Selector(response)
        weixin_name = ''.join(x.xpath('//h3[@id="weixinname"]/text()').extract())
        weixin_id = ''.join(x.xpath('//label[@name="em_weixinhao"]/text()').extract())
        
        req = Request('http://weixin.sogou.com/weixin?type=1&query='+weixin_id, callback=self.parse_list)
        req.meta['weixin_name'] = weixin_name
        req.meta['weixin_id'] = weixin_id
        req.meta['url'] = response.url
        
        yield req
        
    def parse_list(self, response):
        weixin_name = response.meta['weixin_name']
        weixin_id = response.meta['weixin_id']
        url = response.meta['url']
        
        x = Selector(response)
        ext = x.xpath('//div[@class="wx-rb bg-blue wx-rb_v1 _item"]/@href').extract()[0].split('?')[1]
        reqs = []
        
            
        page = 1
        total = 1
        while page <= total:
            try:
                print 'current page:%s'%page
                url = 'http://weixin.sogou.com/gzhjs?cb=sogou.weixin.gzhcb&%s&gzhArtKeyWord=&page=%d&t=%f'%(ext,page,time.time())
                r = requests.get(url,cookies=self.cookies, timeout=10)
                articles = json.loads(re.findall(u'\{[\s|\S]*?\}',r.text)[0])
                  
                for xml in articles['items']:
                    href = etree.fromstring(xml.split('?>')[1]).xpath('//url/text()')[0]
                    href = urlparse.urljoin('http://weixin.sogou.com',href)
                    date = etree.fromstring(xml.split('?>')[1]).xpath('//date/text()')[0]
                    date = datetime.strptime(date,'%Y-%m-%d').strftime('%Y-%m-%d')
                    if self.all == '0':
                        #微信中一天可以发布多篇
                        if date == datetime.today().strftime('%Y-%m-%d'):
                            req = Request(url=urlparse.urljoin('http://weixin.sogou.com/',href), callback=self.parse_article, cookies=self.cookies)
                            req.meta['weixin_name'] = weixin_name
                            req.meta['weixin_id'] = weixin_id
                            reqs.append(req)
                        else:
                            return reqs
                    elif self.all == '1':
                        req = Request(url=urlparse.urljoin('http://weixin.sogou.com/',href), callback=self.parse_article, cookies=self.cookies)
                        req.meta['weixin_name'] = weixin_name
                        req.meta['weixin_id'] = weixin_id
                        reqs.append(req)
                page += 1
                total = articles['totalPages']
                break
            except Exception,e:
                page += 1
                total = articles['totalPages']
        print 'total article: %i'%len(reqs)
        return reqs
    

        
    def parse_article(self, response):
        weixin_name, weixin_id = response.meta['weixin_name'],response.meta['weixin_id']
        x = Selector(response)
        title = ''.join(x.select('//h2[@id="activity-name"]/text()').extract()).strip()
        publish_date = ''.join(x.select('//em[@id="post-date"]/text()').extract()).strip()
        briefs = x.select('//div[@id="js_content"]/*').extract()
        

         
         
        print briefs
            
            

        
        
        
        
        
        
   




