from scrapy import Spider, Request
from airbnb.items import AirbnbItem
from scrapy_splash import SplashRequest
#from selenium import webdriver
import re 

#################################  IMPORTANT  ################################################
# When running this script, need to run this command in the background on a separate terminal:
# docker run -p 8050:8050 scrapinghub/splash
#################################  IMPORTANT  ################################################

class AirbnbSpider(Spider):

	name = "airbnb_spider"
	allowed_urls = ["https://airbnb.com"]
	start_urls = ["https://airbnb.com"]



	def parse(self, response):
		# CALLS PARSERS ON EVERY PRICE POINT FOR PLACES IN MANHATTAN
		# WE COULD EXPAND THIS TO OTHER BOROS BY APPENDING THEIR NAMES TO NEW LISTS.
		# OR IN OTHER SIMILAR FASHIONS.

		# Construction of URLs
		URL_frag1 = r"https://www.airbnb.com/s/Manhattan--New-York-City--NY--United-States/homes?refinement_paths%5B%5D=%2Fhomes&allow_override%5B%5D=&price_max="
		URL_frag2 = r"&ne_lat=40.819590026706805&ne_lng=-73.91768915134355&sw_lat=40.692268164540494&sw_lng=-74.05330163913652&zoom=12&search_by_map=true&price_min="
		URL_frag3 = r"&s_tag=ikIBNgau"

		lastURL = r"https://www.airbnb.com/s/Manhattan--New-York-City--NY--United-States/homes?refinement_paths%5B%5D=" + r"%2F" + r"homes&allow_override%5B%5D=&ne_lat=40.819590026706805&ne_lng=-73.91768915134355&sw_lat=40.692268164540494&sw_lng=-74.05330163913652&zoom=12&search_by_map=true&price_min=999&s_tag=D2-Gtzq2"

		for price in range(10,991,10):
			url = URL_frag1 + str(price+10) + URL_frag2 + str(price) + URL_frag3
			if price == 990: 
				url = lastURL
			yield SplashRequest(url, callback=self.parse_PriceRange, args = {"wait": 5}, endpoint = "render.html", meta = {"price":price})



	def parse_PriceRange(self, response):
		# GOAL HERE:
		# CALL A PARSER TO GO THROUGH EACH PAGE AT ANY GIVEN PRICE POINT

		price = response.meta['price']
		URL_frag1 = response.url
		urls = [(URL_frag1 + "&section_offset=" + str(i)) for i in range(18)]

		#Checking if we have any urls at this price point
		if response.xpath('//h1[@class="_tpbrp"]/text()').extract_first() != "No results":
			for url in urls:
				yield SplashRequest(url, callback=self.parse_OnePage, args = {"wait": 5}, endpoint = "render.html")



	def parse_OnePage(self, response):
		# GOAL HERE:
		# CALL A PARSER TO GO THROUGH EACH LISTING ON PAGE

		URL_frag1 = 'https://www.airbnb.com/'
		room_url_parts = response.xpath('//div/a[contains(@href,"rooms")]/@href').extract()

		# Getting prices here (at the multiple listings page), because they are difficult to get in the 
		# actual listing.
		prices = (re.findall('"amount_formatted":"\$([0-9]{2,6})",', response.text))
		
		#There is a chance that there will be no listings, so we want to account for this.
		if room_url_parts:
			urls = [(URL_frag1 + room_url_parts[i]) for i in range(len(room_url_parts))]

			# Iterating through all of the listings in the list "urls"
			i = 0
			for url in urls:
				price = prices[i]
				i += 1
				yield SplashRequest(url, callback=self.parse_details, args = {"wait": 2}, endpoint = "render.html", meta = {'price':price})#,'listDataSingle':listDataSingle})



	def parse_details(self, response):
		# GOAL HERE:
		# GET ALL OF THE DETAILS OF THE PAGE HERE
		# WITH SCRAPY SPLASH WE CAN GET THE TEXT BODY OF THE RESPONSE. 
		# WITH THIS, WE CAN REGEX THE ENTIRE BODY TO GET MOST OF THE INFORMATION.

		print("-" * 50)

		item = AirbnbItem()


		#Extracting the roomID from url.
		try:
			roomID = re.search('rooms/([0-9]*)\?location', str(response.url)).group(1)
		except AttributeError:
			roomID = ''

		# Extracting rating and numReviews from below xpath object string.
		string1 = str(response.xpath('//button[@class="_ff6jfq"]/@aria-label').extract_first())

		try:
			rating = re.search('Rated ([0-5](.[0-9])?) out of 5', string1).group(1)
		except AttributeError:
			rating = ''

		try:
			numReviews = re.search('from ([0-9]*) reviews', string1).group(1)
		except AttributeError:
			numReviews = ''

		price = response.meta['price']

		###########################  Overview  #######################
		item['roomID'] = roomID
		item['numReviews'] = numReviews
		item['price'] = price
		item['shortDesc'] = (re.search('"localized_room_type":"(.{1,50})","city',response.text)).group(1)


		#######################  Host   ##############################
		item['numHostReviews'] = response.xpath('//span[@class="_e296pg"]/span[@class="_1uhfauip"]/text()').extract_first()
		item['isSuperhost'] = (re.search('"is_superhost":(.{1,5}),',response.text)).group(1)


		#################  Numbers of rooms/baths/guests  ############
		item['numBaths'] = (re.search('"bathroom_label":"([0-9]\.?[0-9]?).*","bed_label"', response.text)).group(1)
		item['numBeds'] = (re.search('"bed_label":"(.).*","bedroom_label"', response.text)).group(1)

		if re.search('"bedroom_label":"([0-9][0-9]?).*","guest_label"', response.text) != None:
			item['numRooms'] = (re.search('"bedroom_label":"([0-9][0-9]?).*","guest_label"', response.text)).group(1)
		else:
			item['numRooms'] = 0
		if re.search('"guest_label":".{1,8}([0-9][0-9]?).{1,8}",', response.text) != None:
			item['numGuests'] = (re.search('"guest_label":".{1,8}([0-9][0-9]?).{1,8}",', response.text)).group(1)
		else:
			item['numGuests'] = (re.search('"guest_label":"([0-9][0-9]?) guest.*', response.text)).group(1)


		############## Types of rooms/baths/guests  ###################
		item['bathType'] = (re.search('"bathroom_label":"[0-9].?[0-9]? (.*)","bed_label"', response.text)).group(1)
		if re.search('"bedroom_label":"[0-9] (.*)","guest_label"', response.text) != None:
			item['bedroomType'] = (re.search('"bedroom_label":"[0-9] (.*)","guest_label"', response.text)).group(1)
		else:
			item['bedroomType'] = (re.search('"bedroom_label":"(..?.?.?.?.?.?.?.?.?.?.?)","guest_label"', response.text)).group(1)
		item['bedType'] = (re.search('"bed_label":"[0-9] (.*)","bedroom_label"', response.text)).group(1)


		########################  Coordinates  ########################
		coordinates = re.search('"listing_lat":([0-9]{2}.[0-9]*),"listing_lng":(-[0-9]{2}.[0-9]*),', response.text)
		item['latitude'] = coordinates.group(1)
		item['longitude'] = coordinates.group(2)


		##########################  Ratings  ##########################
		# Sometimes the ratings are not available...
		if numReviews:
			item['rating'] = rating
			item['accuracy'] = (re.search('"accuracy_rating":([0-9][0-9]?),"', response.text)).group(1)
			item['communication'] = (re.search('"communication_rating":([0-9][0-9]?),"', response.text)).group(1)
			item['cleanliness'] = (re.search('"cleanliness_rating":([0-9][0-9]?),"', response.text)).group(1)
			item['location'] = (re.search('"location_rating":([0-9][0-9]?),"', response.text)).group(1)
			item['checkin'] = (re.search('"checkin_rating":([0-9][0-9]?),"', response.text)).group(1)
			item['value'] = (re.search('"cleanliness_rating":([0-9][0-9]?),"', response.text)).group(1)
			item['guestSatisfaction'] = (re.search('"guest_satisfaction_overall":([0-9][0-9][0-9]?),"', response.text)).group(1)
		else:
			item['rating'] = ''
			item['accuracy'] = ''
			item['communication'] = ''
			item['cleanliness'] = ''
			item['location'] = ''
			item['checkin'] = ''
			item['value'] = ''
			item['guestSatisfaction'] = ''


		yield item
