import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import BcsmsmItem
from itemloaders.processors import TakeFirst


class BcsmsmSpider(scrapy.Spider):
	name = 'bcsmsm'
	start_urls = ['https://www.bcsm.sm/site/home/sala-stampa/comunicati-stampa-e-notizie.html']

	def parse(self, response):
		post_links = response.xpath('//h3/a')
		for post in post_links:
			date = post.xpath('./text()').get()
			date = re.findall(r'\d{2}/\d{2}/\d{4}', date)[0]
			url = post.xpath('./@href').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//div[@class="freccia fr"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h2/text()').get()
		description = response.xpath('//div[@class="box-content"]//text()[normalize-space() and not(ancestor::h2)]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BcsmsmItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
