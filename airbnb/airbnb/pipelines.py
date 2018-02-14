# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter

# class AirbnbPipeline(object):
#     def process_item(self, item, spider):
#         return item

class ValidateItemPipeline(object):
	def process_item(self, item, spider): 
		return item

class WriteItemPipeline(object): 

	def __init__(self):
		self.filename = 'airbnb_manhattan.csv'

	def open_spider(self, spider):
		self.csvfile = open(self.filename, 'wb') 
		self.exporter = CsvItemExporter(self.csvfile) 
		self.exporter.start_exporting()

	def close_spider(self, spider): 
		self.exporter.finish_exporting() 
		self.csvfile.close()

	def process_item(self, item, spider): 
		self.exporter.export_item(item)
		return item