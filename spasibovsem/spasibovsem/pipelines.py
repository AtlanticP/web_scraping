# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

aa = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
import sqlite3

class SpasibovsemPipeline(object):
    
    def __init__(self):

        self.create_connection()
        self.create_table()

    def create_connection(self):

        self.conn = sqlite3.connect('spasibo.db')
        self.curr = self.conn.cursor()

    def create_table(self):

        self.curr.execute('''DROP TABLE IF EXISTS spasibo_tb''')
        self.curr.execute("""CREATE TABLE spasibo_tb(
                             text text,
                             sent text,
                             mark text
                          )""")

    def process_item(self, item, spider): 
        # import pdb; pdb.set_trace()
        self.store_db(item)

        return item

    def store_db(self, item):

        self.curr.execute('''INSERT INTO spasibo_tb values (?,?,?)''',(
                item['text'],
                item['sent'],
                item['mark']
            ))

        self.conn.commit()
