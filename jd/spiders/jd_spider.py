# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import CrawlSpider
import re
from scrapy.http import Request
import json
import pprint

class JdSpiderSpider(CrawlSpider):
    name = 'jd_spider'
    allowed_domains = ['m.jd.com','p.3.cn']
    start_urls = ['https://item.jd.com/3378484.html']

    rules = (
            Rule(LinkExtractor(allow=(r'(https|http)://item.jd.com/\d+.html')),
                callback='parse_item',
                follow=True
                ),
            )

    def parse_item(self, response):
        ware_id_list = list()
        url_group_shop = LinkExtractor(allow=(r'(https|http)://item.jd.com/\d+.html')).extract_links(response)

        re_get_id = re.compile(r'(https|http)://item.jd.com/(\d+).html')  #返回一个re.pattern对象

        for url in url_group_shop:
            ware_id = re_get_id.search(url.url).group(2)
            ware_id_list.append(ware_id)

        for ware_id in ware_id_list:
           yield Request('https://item.m.jd.com/ware/detail.json?wareId={}'.format(ware_id),
                          callback = self.detail_pag,
                          meta = {'ware_id':ware_id},
                          priority = 5,
                        )

    def detail_pag(self,response):
        _ = self
        data = json.loads(response.text)
        yield Request('https://p.3.cn/prices/mgets?type=1&skuIds=J_{}'.format(response.meta['ware_id']),
                       callback = self.get_price,
                       meta = {'ware_id':response.meta['ware_id'],
                               'data':data},
                       priority = 10,
                     )

    def get_price(self,response):
        _ = self
        data = json.loads(response.text)
        detail_data = response.meta['data']
        ware_id = response.meta['ware_id']
        item = {
                'detail':detail_data,
                'price':data,
                'ware_id':ware_id
               }

        pprint.pprint(item)
        yield item
