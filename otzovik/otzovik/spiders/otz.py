import scrapy
import time
import random

n = 1
rnd = lambda : random.randint(5, 10)

class OtzSpider(scrapy.Spider):
    name = 'otz'
    # allowed_domains = ['https://otzovik.com/']
    # start_urls = ['https://otzovik.com/sitemap']
    
    def start_requests(self):
        
        url = 'https://otzovik.com/sitemap'

        time.sleep(1)
        request = scrapy.Request(url=url, callback=self.parse)
        
        yield request 
        

    def parse(self, response):
        
        categories = response.css('div.sitemap-left h3 a::attr(href)').getall()
        
        for cat in categories[:n]:  #!!!!!!!!!!!!!!

            time.sleep(rnd())
            link = response.urljoin(cat)
            
            yield scrapy.Request(link, callback=self.parse_cat)
            
    def parse_cat(self, response):
        # https://otzovik.com/auto/autospares/
        
        products = response.css('a.product-name::attr(href)').getall()
        
        # if response.meta.get('cnt') > 1:   #!!!!!!{'next':'page}
            
        #     print(response.meta.get('next_page'))
        #     print(response.meta.get('cnt'))
        #     import pdb; pdb.set_trace()
            
        for prod in products[:n]:
            
            # import pdb; pdb.set_trace()
            time.sleep(rnd())
            link = response.urljoin(prod)
            
            yield scrapy.Request(link, callback=self.parse_prods)
            
        next_page = response.css('a.pager-item.next.tooltip-top::attr(href)').get()
  
        if next_page:
            
            # import pdb; pdb.set_trace()
            link = response.urljoin(next_page)
            yield scrapy.Request(link, self.parse_cat, meta={'next_page': link})            

    def parse_prods(self, response):
        # https://otzovik.com/reviews/schetka_stekloochistitelya_beskarkasnaya_just_drive/
        
        reviews = response.css('a.review-title::attr(href)').getall()        
        
        for review in reviews[:1]:
            
            time.sleep(rnd())
            link = response.urljoin(review)

            yield scrapy.Request(link, self.parse_review, meta={'link': link})

    def parse_review(self, response):
        # https://otzovik.com/review_12583355.html

        time.sleep(rnd())
        review = response.css('div.review-body.description::text').getall()
        review = '.'.join(review)
        
        stars = response.css('span.product-rating.tooltip-right').css('span.icons.icon-star-1')
        est = len(stars)
        
        yield {
            'review': review,
            'estimation': est,
            'link': response.meta['link']
            }