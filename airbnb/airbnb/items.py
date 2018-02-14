# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AirbnbItem(scrapy.Item):
    # define the fields for your item here like:
	roomID = scrapy.Field()
	rating = scrapy.Field()
	numReviews = scrapy.Field()
	numHostReviews = scrapy.Field()
	price = scrapy.Field()
	numGuests = scrapy.Field()
	roomType = scrapy.Field() #studio, 2 bedroom
	numBeds = scrapy.Field()
	numBaths = scrapy.Field()
	numRooms = scrapy.Field()
	shortDesc = scrapy.Field()
	latitude = scrapy.Field()
	longitude = scrapy.Field()

	accuracy = scrapy.Field() #studio, 2 bedroom
	communication = scrapy.Field()
	cleanliness = scrapy.Field()
	location = scrapy.Field()
	checkin = scrapy.Field()
	value = scrapy.Field()
	guestSatisfaction = scrapy.Field()

	shortDesc = scrapy.Field()
	isSuperhost = scrapy.Field()
	responseTimeShown = scrapy.Field()
	bathType = scrapy.Field()
	bedroomType = scrapy.Field()
	bedType = scrapy.Field()

