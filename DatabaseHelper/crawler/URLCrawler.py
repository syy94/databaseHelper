'''
Created on May 14, 2017

@author: Choony
'''
import scrapy
from scrapy.crawler import CrawlerProcess

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://www.tp.edu.sg/schools/hss/gerontological-management-studies'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        

process = CrawlerProcess()
process.crawl(QuotesSpider)
process.start() # the script will block here until the crawling is finished