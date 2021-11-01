from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options

# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import WebDriverException, TimeoutException
# from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
# import sys
import random
import time
import sqlite3
import os 
from sqlite3 import  OperationalError
#%%

path_to_driver = '/home/atl/.selenium/geckodriver-v0.30.0-linux64/geckodriver'
driver = webdriver.Firefox(executable_path=path_to_driver )

#%%
rnd = lambda: random.randint(1, 3)
#%%
driver.get('https://otzovik.com/sitemap')
assert "Каталог" in driver.title
#%% Categories: https://otzovik.com/sitemap
n = 2   # !!!!!!!!!!!!!!!!!!!!!!!!!
def parse_cats(link):
    # https://otzovik.com/sitemap
    
    driver.get(link)
    time.sleep(rnd())
    
    n_cats = len(driver.find_elements_by_css_selector('div.sitemap-left h3 a'))
    
    # for icat in range(n):    # !!!!!!!
    for icat in range(1, n_cats):
        
        driver.get(link)
        time.sleep(rnd())
        now = time.time()
        is_catched = True
        
        while True:
            try:
                cat = driver.find_elements_by_css_selector('div.sitemap-left h3 a')[icat]
                link_cat = cat.get_attribute('href')
                break
            
            except NoSuchElementException:
                print('wait until element in DOM')                
                time.sleep(0.05) 
                
                delta = time.time() - now
                if delta > 10:
                    is_catched = False
                    break
        
        if not is_catched:
            continue


        yield link_cat

# start_url = 'https://otzovik.com/sitemap'
# for link_cat in parse_cats(start_url):
#     print(link_cat)  
#%%  parse reviews

def parse_reviews(link):
    # 'https://otzovik.com/auto/autospares/' 

    driver.get(link)
    time.sleep(rnd())
    
    n_revs = len(driver.find_elements_by_css_selector('a.product-name'))

    # for irev in range(n):    #!!!!!!!!
    for irev in range(n_revs):    
        
        driver.get(link)
        time.sleep(rnd())
        now = time.time()
        is_catched = True
        while True:
            try: 
                
                review = driver.find_elements_by_css_selector('a.product-name')[irev]
                link_rev = review.get_attribute('href')
                break
            
            except NoSuchElementException:
                    
                print('wait until element in DOM')                
                time.sleep(0.05)
    
                delta = time.time() - now
                if delta > 10:
                    is_catched = False
                    break
                
        if not is_catched:
            continue
                
        yield link_rev
    
    driver.get(link)
    time.sleep(rnd())
    
    css_next = 'a.pager-item.next.tooltip-top'
    link_next = driver.find_element_by_css_selector(css_next).get_attribute('href')

    if link_next:
        
        for link_rev_next in parse_reviews(link_next):
            yield link_rev_next

# link = 'https://otzovik.com/auto/autospares/'            
# link = 'https://otzovik.com/auto/moto/mopeds/'
# for link_rev in parse_reviews(link):
#     print(link_rev)
#%% parse description https://otzovik.com/reviews/sharovaya_opora_finwhale/

def parse_descr(link):
    # 'https://otzovik.com/reviews/akkumulyator_fb_altica_premium_125d26l/'
    driver.get(link)
    time.sleep(rnd())
    
    css_rt = 'a.review-title'
    ntitles = len(driver.find_elements_by_css_selector(css_rt))
    
    for ititle in range(ntitles):
        
        driver.get(link)
        time.sleep(rnd())
        
        titles = driver.find_elements_by_css_selector(css_rt)
        titles[ititle].click()
        
        # description of review
        css_bd = 'div.review-body.description'
        now = time.time()
        is_catched = True
        
        while True:
        
            try:
                descr = driver.find_element_by_css_selector(css_bd)
                text = descr.text
                stars = driver.find_elements_by_css_selector(
                    'span.product-rating.tooltip-right span.icons.icon-star-1')
                rate = len(stars)
                break
            
            except NoSuchElementException:
            
                print('wait until element in DOM')                
                time.sleep(0.05)
                
                delta = time.time() - now
                if delta > 10:
                    is_catched = False
                    break
                
        if not is_catched:
            continue
            
        yield {
            'link': driver.current_url,
            'stars': rate,
            'text': text
            }
# link_rev = 'https://otzovik.com/reviews/filtr_salonniy_pilenga/'    
# for dct in parse_descr(link_rev):    
#     print(dct)
#%% crawling

# remove db if exists
db_name = 'otzovik.db'
# if os.path.isfile(db_name):
#     os.remove(db_name)

# creating sqllite db
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
# cursor.execute("CREATE TABLE otz (link text , rate int, text text)")

# crawlling 
start_url = ' https://otzovik.com/sitemap'

for link_cat in parse_cats(start_url):
    for link_rev in parse_reviews(link_cat):
        print(link_rev)
        for dct in parse_descr(link_rev):    
            
            # insert ito db
            link, rate, text = dct.values()
            try:
                cursor.execute(f"INSERT INTO otz VALUES('{link}', '{rate}', '{text}')") 
                conn.commit()
            except OperationalError:
                print('error:', link)
            
#%%

#%%
# import pandas as pd


# with open(file_name, 'r') as file:
#     txt = file.read()
    
# pd.read_csv(file_name,) # delimiter=',')
# #%%
# file_name = 'otzovik.csv'
# with open(file_name, 'w') as file: 
#     pass

# for i in range(3):
#     dct =  {
#             'text': 'text',
#             'stars': str(i),
#             'link': 'www.adr.ru'
#         }
#     with open(file_name, 'a') as file: 
#         rec = ';;;'.join(dct.values()) + '\n'
#         file.write(rec)    
# #%%
# import pandas as pd

# df = pd.read_csv(file_name, delimiter=';;;')
# #%%
# import sqlite3


# #%%
# asd = 'ok'
# link, rate, text = dct.values()

# cursor.execute(f"INSERT INTO otz VALUES('{link}', '{rate}', '{text}')") 
# conn.commit()

# #%%
# dct = {'link': 'ya.ru', 'rate': 5, 'text': 'my text'}
# txt = '''{}, {}, {}'''.format(dct['link'], dct['rate'], dct['text'] )
# print(txt)

#%%
# stars = driver.find_elements_by_css_selector(
#         'span.product-rating.tooltip-right span.icons.icon-star-1')
# print(stars)    
# #%%
# css_butt = 'a.review-btn.review-read-link'
# more_butts = driver.find_elements_by_css_selector(css_butt)
# id_butts = len(driver.find_elements_by_css_selector(css_butt))



# for id_butt in range(id_butts):
#     # driver.get(link)
#     try: 
#         driver.find_elements_by_css_selector(css_butt)[id_butt].click()
#         css = 'div.review-body.description'
#         # description of review
#         descr = driver.find_element_by_css_selector(css)
        
#         # rating
#         stars = driver.find_element_by_css_selector('span.product-rating.tooltip-right') #.css('span.icons.icon-star-1')
#         stars = driver.find_elements_by_css_selector('span.product-rating.tooltip-right span.icons.icon-star-1')
#         n_stars = len(stars)
    
#     except NoSuchElementException:
#         css = 'div.review-teaser'
#         descr = driver.find_element_by_css_selector(css)
    
#     # description of review
#     text = descr.text             

#         # yield {'descr': text, 'rate': n_stars}
# #%%
# # driver.get('https://otzovik.com/review_12588549.html')        

# # link_rev = 'https://otzovik.com/reviews/akkumulyator_fb_altica_premium_125d26l/'

# stars = driver.find_element_by_css_selector('span.product-rating.tooltip-right') #.css('span.icons.icon-star-1')
# stars = driver.find_elements_by_css_selector('span.product-rating.tooltip-right span.icons.icon-star-1')
# n_stars = len(stars)
# print(n_stars)
# #%%
# for txt in parse_descr(link_rev):
#     print(txt)





#%%
# from selenium.webdriver.common.by import By
# t = driver.find_elements(By.CSS_SELECTOR, 'div.sitemap-left a')
# print(t)


# # os.environ["PATH"] += os.pathsep + DIR
# MAX_WAIT = 20

# # options = Options()
# # try:
# #   sys.argv[1]
# #   options.options = sys.argv[1]
# # except IndexError:
# #   options.headless = True

# def load_page(dv, link):
#   while True:
#     try:
#       dv.get(link)
#       return dv
    
#     except (TimeoutException, WebDriverException):
#       print(f'exception trying loading {link}')
#       continue

# def get_element_by_xpath(dv, xpath):
#   '''
#   to be sure that catched element has a desired atribute.
#   Function returns list of links.
#   '''
#   start = time.time()
#   while True:
    
#     links = dv.find_elements_by_xpath(xpath)
#     links = [i.get_attribute('href') for i in links]
    
#     if any(i == 'javascript:void(0)' for i in links):
#         time.sleep(0.5)
#         print('sleeeeeeping')

#     elif time.time() - start > MAX_WAIT:
#       print('new driver')
#       url = dv.current_url
#       dv = load_page(dv, url)
#       start = time.time()

#       continue

#     else:
#       print('time required', round(time.time() - start))
#       return links 

# dv = webdriver.Firefox(options=options, executable_path=FILE)
# dv.implicitly_wait(5)

# dv.set_page_load_timeout(30)

# dv = load_page(dv, 'http://mvideo.ru')

# # 1st level
# links = dv.find_elements_by_xpath('//a[@class="header-nav-item-link"]')
# links = [i.get_attribute('href') for i in links]
# links = [i for i in links if not ('appl' in i or 'akci' in i)]

# for link in links:

#   print(link, 1)

#   # 2nd (links, texts) level https://www.mvideo.ru/televizory-i-video
#   dv = load_page(dv, link)

#   links = dv.find_elements_by_css_selector('a.category-grid-item-link')
#   texts = dv.find_elements_by_xpath('//div[@class="category-grid-title"]')

#   for txt, link in list(zip(texts, links)):
  
#     txt = txt.text
#     link = link.get_attribute('href')

#     if 'диагонал' in txt:
#       continue

#     print(txt, link, 2)
  
#     # links of 3d level https://www.mvideo.ru/televizory-i-cifrovoe-tv-1?reff=menu_main
#     dv = load_page(dv, link)
#     links = dv.find_elements_by_xpath('//a[@class="category-grid-item-link"]')
#     texts = dv.find_elements_by_xpath('//div[@class="category-grid-title"]')

#     for txt, link in zip(texts, links):
#       txt = txt.text
#       link = link.get_attribute('href')
#       print(txt, link, 3)

#       #4th level https://www.mvideo.ru/televizory-i-cifrovoe-tv/televizory-65
#       dv = load_page(dv, link)
#       xpath = '//div[@class="product-grid-card__title"]/a'
#       links =  get_element_by_xpath(dv, xpath) 

#       for link in links: # #!!!!!!!!!!!!!!!!!!!!!!!!1
        
#         dv = load_page(dv, link)

#         dv.find_elements_by_xpath('//a[@class="c-tabs__menu-link"]')[2].click()
#         rev = dv.find_elements_by_xpath('//span[@class="text-cutter-wrapper"]')
#         rev = [i.text for i in rev]
#         rev = [i for i in rev if not (i.lower() == 'да' or i.lower() == 'нет')]
        
#       # specific link 3 level to disiareable https://www.mvideo.ru/televizory-i-cifrovoe-tv/televizory-65       
#       if 'все' in txt.lower():
#         break
        
#         break
#       break
#     break
#   break

# dv.close()