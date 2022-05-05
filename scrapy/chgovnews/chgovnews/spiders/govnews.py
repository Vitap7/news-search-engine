# author : Lsn
# date : 2020-12-10
# scrapy 爬取中国政府新闻网滚动新闻
#
from __future__ import absolute_import
import scrapy
from ..items import ChgovnewsItem
import re

# scrapy crawl govnews

class GovnewsSpider(scrapy.Spider):
    name = 'govnews'
    allowed_domains = ['gov.cn']

    def start_requests(self):
        url = 'http://sousuo.gov.cn/column/30611/'
        # 每页20条新闻
        for x in range(0,500,1):
            yield scrapy.Request(url= url + str(x) +'.htm', callback=self.parse)

    def parse(self, response):

        # 测试输出
        #print(response.body)

        hrefs = response.xpath('//div[@class="list list_1 list_2"]//a/@href').extract()

        for href in hrefs:
            yield scrapy.Request(href,meta={'href':href},callback=self.parse1)

    def parse1(self, response):

        item = ChgovnewsItem()

        # 网页源码中，标题存放在列表第一项，过滤空格
        if response.xpath('//div[@class="content"]//h1/text()').extract():
            item['title'] = response.xpath('//div[@class="content"]//h1/text()').extract()[0].strip()
        else:
            return

        # 默认评论数为0
        item['comment'] = '0'

        # 每条新闻的url
        item['url'] = response.meta['href']

        item['time'] = ''
        timeinfos = response.xpath('//div[@class="pages-date"]').extract()
        # 防止爬取的时间含有无用字样，进行文本清洗
        for timeinfo in timeinfos:
            pat = re.findall(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})",timeinfo)
            item['time'] = ''.join(pat)

        # 文章内容也有无用信息和多余符号，利用正则表达式进行文本清洗
        item['text'] = ''
        textinfos = response.xpath('//div[@class="pages_content"]/p[contains(@style,"text-indent")]/text()').extract()
        pat = re.compile('<[^>]+>',re.S)
        for textinfo in textinfos:
            item['text'] = item['text'].replace('   ','') + pat.sub('',textinfo)

        # 输出测试
        #print(item['title']+'   '+item['url']+'    '+item['time'] + item['text'])
        #print(item['time'])
        #print(item['comment'])
        print(item['title'])
        #print(item['text'])
        yield item

        pass