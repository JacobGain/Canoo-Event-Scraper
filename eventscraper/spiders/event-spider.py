import scrapy
from eventscraper.items import EventItem

# from scrapy_splash import SplashRequest


"""
This is a scrapy spider developed by Jacob Gain for the ICC to scrape information from partnered websites to be put
on the Canoo Events application. The logic for each website is all individually created using css selectors, meaning
it should still work when the websites update their events. If a website were to completely revamp the structure of
their website, in theory the spider will break when attempting to scrape it. To operate the spider, make sure that 
the domains.txt file is populated line by line with the domains to be scraped, and that the domain matches the 
condition in the if/elif statements. Run the run_spiders.py file to run the spider through each domain in domains.txt, 
ensuring that the output is properly structured as jsonl or csv, and is directed to the appropriate folder.
* see run_spiders.py
"""


class EventSpider(scrapy.Spider):
    name = 'old'

    def __init__(self, url=None, *args, **kwargs):
        super(EventSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    def parse(self, response):

        # ----- Toronto Zoo logic ----- 1
        if 'www.torontozoo.com' in response.url:
            for events in response.css('div.c1080'):

                item = EventItem()

                title = events.css('div[style*="font-size:1.4em"]::text').get()

                website_url = events.css('a.event::attr(href)').get()
                # /events/indigenousheritagemonth#evt
                # https://www.torontozoo.com/events/indigenousheritagemonth#evt

                temp_image_url = events.css('div.inner-circle::attr(style)').get()
                # background-image:url(/!/img/event/24/turtleworld.png);
                # https://www.torontozoo.com/!/img/event/24/turtleworld.jpg

                if title:
                    item['title'] = title
                    item['date'] = None
                    item['time'] = None
                    item['description'] = None
                    item['address'] = '2000 Meadowvale Rd, Toronto, ON'
                    item['venue_name'] = 'Toronto Zoo'
                    image_url = temp_image_url.replace('background-image:url(', '').replace(');', '')
                    item['image_url'] = 'https://www.torontozoo.com' + image_url
                    item['website_url'] = 'https://www.torontozoo.com' + website_url
                    yield item

        # ----- Ontario Science Centre Logic ----- 2
        elif 'www.ontariosciencecentre.ca' in response.url:
            for events in response.css('div.osc-callout-items'):

                item = EventItem()

                title = events.css('span.title::text').get()

                date = events.css('span.event.date::text').get()

                time = events.css('span.date1::text').get()

                description = events.css('p::text').get()

                website_url = events.css('a.osc-callout::attr(href)').get()
                # /what-s-on/demos-programs-plus-special-events/all-about-honeybees/
                # https://www.ontariosciencecentre.ca/what-s-on/demos-programs-plus-special-events/a-hair-raising-experience

                if title:
                    item['title'] = title
                    item['date'] = date
                    item['time'] = time
                    item['description'] = description
                    item['address'] = '770 Don Mills Rd, North York, ON'
                    item['venue_name'] = 'Ontario Science Centre'
                    item['image_url'] = None
                    item['website_url'] = 'https://www.ontariosciencecentre.ca' + website_url
                    yield item

        # ----- TELUS Spark Science Centre Logic ----- 3
        elif 'www.sparkscience.ca' in response.url:
            for events in response.css('div.col-12'):

                item = EventItem()

                title = events.css('h4.h4::text').get()

                date = events.css('strong.label.primary-label::text').get().strip()

                description = events.css('p::text').get()

                website_url = events.css('a.learn-more::attr(href)').get()
                # /infinity-dome-theatre/jane-goodall
                # https://www.sparkscience.ca/infinity-dome-theatre/jane-goodall

                temp_image_url = events.css('div.image-holder.bg-stretch::attr(style)').get()
                # "background-image: url('https://images.prismic.io/telusspark/1a588a47-a9cd-4ded-bea2-
                # 06310e879e73_jane-goodall-banner-1536x1520.jpg?auto=compress,format&rect=0,315,1536,890&w=1320&h=765');"

                if title:
                    item['title'] = title
                    item['date'] = date
                    item['time'] = None
                    item['description'] = description
                    item['address'] = "220 Saint George's Drive Northeast, Calgary, AB"
                    item['venue_name'] = 'TELUS Spark Science Centre'
                    image_url = temp_image_url.replace("background-image: url('", '').replace("');", '')
                    item['image_url'] = image_url
                    item['website_url'] = 'https://www.sparkscience.ca' + website_url
                    yield item

        # ----- Art Gallery of Ontario Logic ----- 4
        elif 'ago.ca' in response.url:
            for events in response.css('div.ago-card'):

                item = EventItem()

                title = events.css('a[ hreflang="en"]::text').get()

                date = events.css('div.date-time-info::text').get()

                website_url = events.css('a::attr(href)').get()
                # /events/drawing.-drinks.-social.
                # https://ago.ca/events/drawing.-drinks.-social.

                image_url = events.css('img::attr(src)').get()
                # /sites/default/files/styles/ago_card/public/2024-01/358915-Web%20and%20Standard%20PowerPoint.jpg?itok=UFg0wqEX
                # /sites/default/files/styles/ago_card_325/public/2024-01/358915-Web%20and%20Standard%20PowerPoint.jpg?itok=lPGd3JxL

                if title:
                    item['title'] = title
                    item['date'] = date
                    item['time'] = None
                    item['description'] = None
                    item['address'] = "317 Dundas St W, Toronto, ON"
                    item['venue_name'] = 'Art Gallery of Ontario'
                    item['image_url'] = 'https://ago.ca' + image_url
                    item['website_url'] = 'https://ago.ca' + website_url
                    yield item

        # ----- Canadian Museum of Nature Logic ----- 5
        elif 'nature.ca/en/visit-us/whats-on' in response.url:
            # outer = response.css('div.grid-x')
            for events in response.css('div.grid-x article.cell.large-3.medium-5.loop-card'):

                item = EventItem()

                title = events.css('h3::text').get()

                temp_date = events.css('span.date-year::text').get()
                date = None
                if temp_date:
                    date = temp_date.replace('\xa0', ' ')

                description = events.css('p::text').get()

                website_url = events.css('a.loop::attr(href)').get()
                # https://nature.ca/en/visit-us/whats-on/listing/our-land-our-art/

                image_url = events.css('img.attachment-post-thumbnail::attr(src)').get()
                # https://nature.ca/wp-content/uploads/2022/11/cale-img_1505-1200x800.jpg

                if title and date:
                    item['title'] = title
                    item['date'] = date
                    item['time'] = None
                    item['description'] = description
                    item['address'] = "240 McLeod St, Ottawa, ON"
                    item['venue_name'] = 'Canadian Museum of Nature'
                    item['image_url'] = image_url
                    item['website_url'] = website_url
                    yield item

        # ----- Heritage Park Historical Village Logic ----- 6
        elif 'heritagepark.ca' in response.url:
            for events in response.css('div.pb-row.column-count-2'):

                item = EventItem()

                title = events.css('h3::text').get()
                if not title:
                    title = events.css('h3.tribe-events-single-event-title::text').get()

                date = events.css('h4::text').get()
                if not date:
                    date = events.css('h5::text').get()

                description = ''.join(events.css('p *::text').getall()).replace('\xa0', ' ').replace('Learn More', '')

                website_url = events.css('a.button.primary::attr(href)').get()
                # 'https://heritagepark.ca/events/childrens-festival/'

                image_url = events.css('img.img::attr(src)').get()
                # 'https://heritagepark.ca/wp-content/uploads/2024/05/20220724_HeritagePark_Day01_528-1.jpg'

                if title:
                    item['title'] = title
                    item['date'] = date
                    item['time'] = None
                    item['description'] = description
                    item['address'] = "1900 Heritage Dr SW, Calgary, AB"
                    item['venue_name'] = 'Heritage Park Historical Village'
                    item['image_url'] = image_url
                    item['website_url'] = website_url
                    yield item

        # ----- H.R. MacMillan Space Centre Logic ----- 7
        elif 'www.spacecentre.ca' in response.url:
            for events in response.css('div.elementor-column'):

                item = EventItem()

                title = events.css('h3.title::text').get()

                date = events.css('h3.heading-section-subtitle::text').get()

                temp_description = events.css('p.icon-box-description').get()

                website_url = events.css('a.icon-box-link::attr(href)').get()
                # 'https://museumofvancouver.ca/landseasky'

                image_url = events.css('img.attachment-large::attr(data-src)').get()
                # 'https://www.spacecentre.ca/wp-content/uploads/2024/03/Landseasky-Square-1024x1022.jpg'

                if title and date and temp_description and website_url and image_url:
                    item['title'] = title
                    item['date'] = date
                    item['time'] = None
                    description = temp_description.replace('<p class="icon-box-description">', '').replace('</p>',
                                                                                                           '').replace(
                        '<br>\n<br>\n', ' ').replace('\"', '').replace('<br>\n', '')
                    item['description'] = description
                    item['address'] = "1100 Chestnut St, Vancouver, BC"
                    item['venue_name'] = 'H.R. MacMillan Space Centre'
                    item['image_url'] = image_url
                    item['website_url'] = website_url
                    yield item

        # ----- Museum of Vancouver Logic ----- 8
        elif '' in response.url:
            for events in response.css('div.row.sqs-row'):

                item = EventItem()

                title = events.css('h1[style="white-space:pre-wrap;"]::text').get()


                date = events.css('p[style="white-space:pre-wrap;"] em::text').get()

                description = ''.join(events.css('p[style="white-space:pre-wrap;"] *::text').getall())

                website_url = events.css('a.sqs-block-button-element--medium::attr(href)').get()
                # 'https://museumofvancouver.ca/mirage'

                image_url = events.css('img[data-stretch="false"]::attr(src)').get()
                # 'https://images.squarespace-cdn.com/content/v1/58d29e6ccd0f6829bdf2f58f/37a7382a-82e8-4a74-9a52-8ac3527e4b27/Mirage-Social_1080x1080-smaller.jpg'

                if title and description:
                    item['title'] = title.replace('\u00A0', ' ')
                    item['date'] = date
                    item['time'] = None
                    item['description'] = description.replace('\xa0',' ')
                    item['address'] = "1100 Chestnut St, Vancouver, BC"
                    item['venue_name'] = 'Museum of Vancouver'
                    item['website_url'] = website_url
                    item['image_url'] = image_url
                    yield item
