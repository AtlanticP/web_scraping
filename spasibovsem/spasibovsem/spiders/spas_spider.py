import scrapy
from ..items import SpasibovsemItem
import time

aa = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

class SpasibovsemSpider(scrapy.Spider):

    name = 'spas'

    start_urls = [
        'https://spasibovsem.ru/tehnika-otzyvy/'
        # 'http://127.0.0.1:5000/level1'
    ]

    def parse(self, response):

        if response.status == 502:
            print("I'm sleeping out")
            time.sleep(60)
            yield scrapy.Request(response.ulr, self.response)

        item = SpasibovsemItem()

        rev = response.xpath(
            '//div[@class="text response-text description"]/p/text()'
            ).get()
        
        if rev:
            
            time.sleep(1)
            rev = response.xpath(
                '//div[@class="text response-text description"]/p/text()'
                ).extract()

            rev = [i.rstrip('\r') for i in rev]
            rev = ' '.join(rev)
            item['text'] = rev
            
            mark = response.xpath(
                '//div[@class="val"]/div[@class="stars big"]'
                ).css('::attr("data-fill")').extract()[0]
            item['mark'] = mark

            sent = response.xpath('//div[@class="val"]/text()').extract()
            sent = [i for i in sent if i == 'Да' or i == 'Нет'][0]
            item['sent'] = sent
            print(aa)
            print(item)
            print(aa)
            yield item

        # reviews of 2nd level to proceed further redirect
        link = response.xpath(
            '//div[@class="full-item goto"]/a'
            ).css('::attr("href")').get()

        if link:
            time.sleep(1)
            link = response.urljoin(link)
            
            yield scrapy.Request(link, self.parse)

        # reviews of 1st level
        reviews = response.css('div.name a::attr("href")').extract()

        time.sleep(1)
        for link in reviews:
            review = response.urljoin(link)

            yield response.follow(review, callback=self.parse)
        
        # 1 level, following the next page 
        time.sleep(1)
        next_page = response.xpath(
            '//div[@class="arrow right"]/a'
            ).css('::attr("href")').get()
        next_page = response.urljoin(next_page)       
        
        yield scrapy.Request(next_page, callback=self.parse)








