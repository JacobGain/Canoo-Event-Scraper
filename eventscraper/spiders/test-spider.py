import scrapy
from eventscraper.items import EventItem
from datetime import datetime


class TestSpider(scrapy.Spider):
    name = 'test'
    start_urls = ['https://www.youraga.ca/exhibitions/current-exhibitions']

    def parse(self, response):

        for events in response.css('div.views-row'):

            item = EventItem()

            title = events.css('h4::text').get()

            date = events.css('span.start-date::text').get()
            date2 = events.css('span.end-date::text').get()
            if date2:
                date = date + " - " + date2

            # time = events.css('').get()

            description = ''.join(events.css('div.field.field--name-field-exh-teaser div.field-data *::text').getall()).strip()

            website_url = events.css('a::attr(href)').get()
            #

            image_url = events.css('img::attr(src)').get()
            #

            if title:
                item['title'] = title.strip()
                item['date'] = date
                item['time'] = None
                item['description'] = description.replace('\xa0', ' ')
                item['address'] = '2 Sir Winston Churchill Sq, Edmonton, AB'
                item['venue_name'] = "Art Gallery of Alberta"
                item['website_url'] = 'https://www.youraga.ca' + website_url
                item['image_url'] = 'https://www.youraga.ca' + image_url
                yield item
