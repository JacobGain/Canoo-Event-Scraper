import scrapy
import sqlite3
from scrapy.loader import ItemLoader
from eventscraper.items import EventItem
from datetime import datetime


class EventSpiderNew(scrapy.Spider):
    name = 'testing' # temporary name (change from 'testing'), see line 25 in run_spiders.py

    def __init__(self, url=None, *args, **kwargs):
        super(EventSpiderNew, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.title_key = None
        self.date_key = None
        self.time_key = None
        self.description_key = None
        self.address_hardcode_key = None
        self.venue_name_hardcode_key = None
        self.image_url_key = None
        self.website_url_key = None
        self.outer_loop_key = None

        db_file = 'canooevents.db'
        self.con = sqlite3.connect(db_file)  # creates the connection
        self.cur = self.con.cursor()  # creates the cursor, used to execute commands on db
        self.create_table()

    def create_table(self):
        try:
            # self.cur.execute("DROP TABLE IF EXISTS domain_logic")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS domain_logic
            (domain TEXT PRIMARY KEY, title_key TEXT, date_key TEXT, time_key TEXT, description_key TEXT, 
            address_hardcode TEXT, venue_name_hardcode TEXT, image_url_key TEXT, website_url_key TEXT, 
            outer_loop_key TEXT)""")

        except sqlite3.Error as e:
            print("Error creating table:", e)

    def get_keys_by_domain(self, response):
        domain = response.url.strip()
        # print("Domain to match:", domain)
        try:
            self.cur.execute("""SELECT * FROM domain_logic WHERE domain=?""",
                             (domain,))
            result = self.cur.fetchone()
            # print(result)
            if result:
                # print("Domain keys found in database:", result)
                # result[0] is each domain <https://www.example.com/events>
                self.title_key = result[1] if result[1] is not None else None
                self.date_key = result[2] if result[2] is not None else None
                self.time_key = result[3] if result[3] is not None else None
                self.description_key = result[4] if result[4] is not None else None
                self.address_hardcode_key = result[5] if result[5] is not None else None
                self.venue_name_hardcode_key = result[6] if result[6] is not None else None
                self.image_url_key = result[7] if result[7] is not None else None
                self.website_url_key = result[8] if result[8] is not None else None
                self.outer_loop_key = result[9] if result[9] is not None else None
            else:
                self.logger.error(f"No matching domain found for {domain}")
        except sqlite3.Error as e:
            print("Error fetching domain keys:", e)

    def parse(self, response):

        self.get_keys_by_domain(response)

        for events in response.css(self.outer_loop_key):
            il = ItemLoader(item=EventItem(), selector=events)
            # ----- THEMUSEUM -----
            if 'themuseum.ca' in response.url:
                # this has to be in the parse method, otherwise there is no way to get the events for this venue
                date = events.css(self.date_key).get()
                for event in events.css('div.em-event.em-item'):
                    new_loader = ItemLoader(item=EventItem(), selector=event)
                    new_loader.add_css('title', self.title_key)
                    new_loader.add_css('time', self.time_key)
                    new_loader.add_css('description', self.description_key)
                    new_loader.add_value('address', self.address_hardcode_key)
                    new_loader.add_value('venue_name', self.venue_name_hardcode_key)
                    new_loader.add_css('image_url', self.image_url_key)
                    new_loader.add_css('website_url', self.website_url_key)
                    new_loader.add_value('date', date)

                    item_loader = self.modify_data(response, new_loader, event)

                    if item_loader:
                        yield item_loader.load_item()
            else:
                il.add_css('title', self.title_key)
                il.add_css('date', self.date_key)
                il.add_css('time', self.time_key)
                il.add_css('description', self.description_key)
                il.add_value('address', self.address_hardcode_key)
                il.add_value('venue_name', self.venue_name_hardcode_key)
                il.add_css('image_url', self.image_url_key)
                il.add_css('website_url', self.website_url_key)

                item_loader = self.modify_data(response, il, events)

                if item_loader:
                    yield item_loader.load_item()

    def modify_data(self, response, item_loader, events):

        # method that handles the specific conditions for certain websites
        temp_title = item_loader.get_output_value('title') or None
        temp_date = item_loader.get_output_value('date') or None
        temp_time = item_loader.get_output_value('time') or None
        temp_description = item_loader.get_output_value('description') or None
        image_url = item_loader.get_output_value('image_url') or None
        website_url = item_loader.get_output_value('website_url') or None

        if temp_title:  # inside this block is the specific changes for the sites that need to be handled

            # ----- Toronto Zoo -----
            if 'torontozoo' in response.url:
                date = ''.join(events.css('div.colEtxtborder ::text').getall()).strip().split('\r\n')[1]
                item_loader.replace_value('date', date)
                image_url = image_url.replace("background-image:url(", '').replace(');', '')
                item_loader.replace_value('image_url', 'https://www.torontozoo.com' + image_url)
                item_loader.replace_value('website_url', 'https://www.torontozoo.com' + website_url)

            # ----- Ontario Science Centre -----
            elif 'www.ontariosciencecentre.ca' in response.url:
                item_loader.replace_value('website_url', 'https://www.ontariosciencecentre.com' + website_url)

            # ----- TELUS Spark Science Centre -----
            elif 'sparkscience' in response.url:
                item_loader.replace_value('image_url',
                                          image_url.replace("background-image: url('", '').replace("');", ''))
                item_loader.replace_value('website_url', 'https://www.sparkscience.com' + website_url)
                item_loader.replace_value('date', temp_date.replace('\r\n', '').strip())

            # ----- Art Gallery of Ontario -----
            elif 'ago.ca' in response.url:
                item_loader.replace_value('image_url', 'https://ago.ca' + image_url)
                item_loader.replace_value('website_url', 'https://ago.ca' + website_url)

            # ----- Canadian Museum of Nature -----
            elif 'nature.ca' in response.url:
                if temp_date:
                    item_loader.replace_value('date', temp_date.replace('\xa0', ' '))

            # ----- Heritage Park Historical Village -----
            elif 'heritagepark.ca' in response.url:
                description = (
                    ''.join(events.css('p *::text').getall()).replace('\xa0', ' ').replace(
                        'Learn More', ''))
                item_loader.replace_value('description', description)
                if not temp_date:
                    date = response.css(f'{self.outer_loop_key} h5::text').get()
                    item_loader.replace_value('date', date)

            # ----- H.R. MacMillan Space Centre -----
            elif 'www.spacecentre.ca' in response.url:
                if temp_title and temp_date and temp_description and website_url and image_url:
                    description = temp_description.replace('<p class="icon-box-description">', '').replace('</p>',
                                                                                                           '').replace(
                        '<br>\n<br>\n', ' ').replace('\"', '').replace(
                        '<br>\n', '')
                    item_loader.replace_value('description', description)
                    return item_loader
                else:
                    return None

            # ----- Museum of Vancouver -----
            elif 'museumofvancouver.ca' in response.url:
                if temp_title and temp_description:
                    item_loader.replace_value('title', temp_title.replace('\u00A0', ' '))
                    description = ''.join(events.css('p[style="white-space:pre-wrap;"] *::text').getall())
                    item_loader.replace_value('description', description.replace('\xa0', ' '))
                    return item_loader
                else:
                    return None

            # ----- National Gallery of Canada -----
            elif 'www.gallery.ca' in response.url:
                # no additional logic needed
                return item_loader

            # ----- Canadian War Museum -----
            elif 'www.warmuseum.ca' in response.url:
                if temp_title and temp_date:
                    image_url.replace('background-image:url(', '').replace(');', '')
                    item_loader.replace_value('image_url', image_url)
                    if 'https://' not in website_url:
                        item_loader.replace_value('website_url', 'https://www.historymuseum.ca/' + website_url)
                    return item_loader
                else:
                    return None

            # ----- Royal Alberta Museum -----
            elif 'royalalbertamuseum.ca' in response.url:
                parts = temp_title.split('from')

                title = parts[0].strip()

                date = (parts[1].split(' - '))[0].strip()
                event_date = datetime.strptime(date, '%m/%d/%Y')
                today = datetime.today()

                if event_date >= today:
                    event_date = event_date.strftime('%A, %B %d, %Y')
                    item_loader.replace_value('date', event_date)
                    item_loader.replace_value('title', title)
                    item_loader.replace_value('website_url', 'https://royalalbertamuseum.ca' + website_url)
                    return item_loader
                else:
                    return None

            # ----- Manitoba Children's Museum -----
            elif 'childrensmuseum.com' in response.url:
                item_loader.replace_value('title', temp_title.strip())
                item_loader.replace_value('description', temp_description.replace('\xa0', ' '))

                temp_date = (events.css('time.tribe-events-calendar-list__event-datetime ::text').getall())

                temp_date = ''.join(temp_date).replace('\n', '').replace('\t', '')

                if '@' in temp_date:
                    item_loader.replace_value('date', temp_date.split(' @ ')[0])
                    item_loader.replace_value('time', temp_date.split(' @ ')[1])
                else:
                    item_loader.replace_value('date', temp_date)

            # ----- Canadian Museum of History -----
            elif 'www.historymuseum.ca' in response.url:
                if temp_title and temp_date:
                    image_url = image_url.replace('background-image:url(', '').replace(');', '')
                    item_loader.replace_value('image_url', image_url)
                    if 'https://' not in website_url:
                        item_loader.replace_value('website_url', 'https://www.historymuseum.ca' + website_url)
                    return item_loader
                else:
                    return None

            # ----- Montreal Museum of Fine Arts -----
            elif 'www.mbam' in response.url:
                if ('Until' not in temp_date) and ('-' not in temp_date):
                    return None
                else:
                    item_loader.replace_value('website_url', 'https://www.mbam.qc.ca/' + website_url)

            # ----- Montreal Science Centre -----
            elif 'www.montrealsciencecentre.com' in response.url:
                item_loader.replace_value('title', temp_title.strip())
                date = ''.join(events.css('div.block-featured-content__date').getall())
                date = date.replace('\n', '').replace('<div class="block-featured-content__date">', '').replace(
                    '<span>', '').replace('</span>', '').replace('</div>', '').strip()
                item_loader.replace_value('date', date)
                item_loader.replace_value('image_url', image_url.replace('background-image: url(',
                                                                         'https://www.montrealsciencecentre.com').replace(
                    ');', ''))

            # ----- Montreal Museum of Archaeology and History -----
            elif 'pacmusee.qc' in response.url:
                date = ''.join(events.css('span.inline-block.margin-left-smallest::text').getall())
                item_loader.replace_value('date', date)
                item_loader.replace_value('image_url', 'https://pacmusee.qc.ca' + image_url)
                item_loader.replace_value('website_url', 'https://pacmusee.qc.ca' + website_url)

            # ----- Canadian Museum for Human Rights -----
            elif 'humanrights.ca' in response.url:
                if temp_date and image_url:
                    item_loader.replace_value('date', temp_date.replace('\xa0', ' ').strip())
                    item_loader.replace_value('title', temp_title.replace('\xa0', ' ').strip())
                    item_loader.replace_value('image_url', 'https://humanrights.ca' + image_url)
                else:
                    return None

            # ----- Manitoba Museum -----
            elif 'manitobamuseum.ca' in response.url:
                item_loader.replace_value('title', temp_title.strip())
                item_loader.replace_value('description', temp_description.replace('\xa0', ' '))
                date = ''.join(events.css('time.tribe-events-calendar-list__event-datetime ::text').getall()).strip()
                item_loader.replace_value('date', date.split(' @ ')[0])
                item_loader.replace_value('time', date.split(' @ ')[1])

            # ----- Bata Shoe Museum -----
            elif 'batashoemuseum.ca' in response.url:
                item_loader.replace_value('title', temp_title.strip())
                item_loader.replace_value('description', temp_description.replace('\xa0', ' '))
                date = ''.join(events.css('time.tribe-events-calendar-list__event-datetime ::text').getall()).strip()
                item_loader.replace_value('date', date)

            # ----- Studio Bell -----
            elif 'studiobell.ca' in response.url:
                item_loader.replace_value('time', temp_time.strip())

            # ----- Gardiner Museum -----
            elif 'gardinermuseum.on.ca' in response.url:
                item_loader.replace_value('title', temp_title.replace('\xa0', '').strip())
                item_loader.replace_value('description', temp_description.replace('\xa0', '').strip())

            # ----- The Military Museums -----
            elif 'themilitarymuseums.ca' in response.url:
                item_loader.replace_value('description', ' '.join(events.css('p::text').getall()))
                if image_url:
                    item_loader.replace_value('image_url', 'https://themilitarymuseums.ca' + image_url)

            # ----- Maritime Museum of the Atlantic -----
            elif 'maritimemuseum.novascoia.ca' in response.url:
                item_loader.replace_value('website_url', 'https://maritimemuseum.novascotia.ca/' + website_url)
                time = ''.join(events.css('div.views-row::text').getall()).split('FREE')[0].strip()
                item_loader.replace_value('time', time)

            # ----- Royal Aviation Museum of Western Canada -----
            elif 'royalaviationmuseum.com' in response.url:
                item_loader.replace_value('title', temp_title.replace('\xa0', '').strip())

                end_date = events.css('span.tribe-event-date-end::text').get()
                if not end_date:
                    end_date = events.css('span.tribe-event-time::text').get()
                date = temp_date + ' - ' + end_date
                item_loader.replace_value('date', date)

                item_loader.replace_value('description', temp_description.replace('\xa0', ' '))

            # ----- MNDBAQ -----
            elif 'mndbaq.org' in response.url:
                title2 = events.css('h3::text').get() or ""
                item_loader.replace_value('title', temp_title + " " + title2)

                if not temp_date:
                    date = events.css('div.salle::text').get()
                    item_loader.replace_value('date', date)

                description = ''.join(events.css('p *::text').getall()).replace('\r\n', '')
                item_loader.replace_value('description', description)

                item_loader.replace_value('website_url', 'https://www.mnbaq.org' + website_url)
                image_url = image_url.replace('background-size: cover; background-image: url(', '').replace(');', '')
                item_loader.replace_value('image_url', image_url)

            # ----- Museum of Immigration at Pier 21 -----
            elif 'pier21' in response.url:
                time = ' '.join(events.css('p.card-text::text').getall()).strip()
                item_loader.replace_value('time', time)

                if image_url:
                    item_loader.replace_value('image_url', 'https://pier21.ca' + image_url)

            # ----- McMichael Canadian Art Collection -----
            elif 'mcmichael.com' in response.url:
                date2 = events.css('span.tribe-event-date-end::text').get()
                if date2:
                    date = temp_date + " - " + date2
                    item_loader.replace_value('date', date)

                image_url = image_url.replace('background-image: url(', '').replace('); -webkit-background-size: cover; background-size: cover; background-position: center center;', '')
                item_loader.replace_value('image_url', image_url)

            # ----- FortWhyte Alive -----
            elif 'fortwhyte.org' in response.url:
                time2 = events.css('span.tribe-event-time::text').get()
                if time2:
                    temp_title = temp_time + " - " + time2

                date = temp_time.split(' @ ')[0]
                time = temp_time.split(' @ ')[1]

                item_loader.replace_value('date', date)
                item_loader.replace_value('time', time)
                item_loader.replace_value('title', temp_title.strip())

            # ----- London Children's Museum -----
            elif 'londonchildrensmusuem' in response.url:
                date = ''.join(events.css('h4.field-content.date *::text').getall()).replace('\n', '')
                item_loader.replace_value('date', date)

                item_loader.replace_value('website_url', 'https://www.londonchildrensmuseum.ca' + website_url)
                item_loader.replace_value('image_url', 'https://www.londonchildrensmuseum.ca' + image_url)

            # ----- Toronto Railway Museum -----
            elif 'torontorailwaymuseum.com' in response.url:
                date = ''.join(events.css('time.tribe-events-calendar-list__event-datetime *::text').getall()).strip()
                item_loader.replace_value('date', date)

                item_loader.replace_value('title', temp_title.strip())
                item_loader.replace_value('description', temp_description.replace('\xa0', '').strip())

            # ----- THEMUSEUM -----
            elif 'themuseum.ca' in response.url:
                item_loader.replace_value('time', temp_time.replace('\u200a', '').replace('\u2009', '').strip())
                item_loader.replace_value('description', temp_description.replace('\xa0', '').replace('\u200B', '').strip())

            # ----- Museum of Contemporary Art Toronto -----
            elif 'moca.ca' in response.url:
                date2 = events.css('div[data-id="f8a1d2e"] div.jet-listing-dynamic-field__content::text').get()
                if date2:
                    temp_date = temp_date + date2
                item_loader.replace_value('date', temp_date.replace('\xa0', ' ').strip())

                time2 = events.css('div[data-id="aca0fe3"] div.jet-listing-dynamic-field__content::text').get()
                if time2:
                    temp_time = temp_time + time2

                if temp_time:
                    item_loader.replace_value('time', temp_time.replace('\xa0', ' ').strip())

                if not image_url:
                    image_url = events.css('img::attr(src)').get()
                    item_loader.replace_value('image_url', image_url)

            # ----- Canadian Automotive Museum -----
            elif 'canadianautomotivemuseum.com' in response.url:

                date = ' - '.join(events.css('time.event-date::text').getall())

                time = ' - '.join(events.css('span.eventlist-meta-time time.event-time-12hr::text').getall())

                if not time:
                    time1 = events.css('time.event-time-12hr-start::text').get()
                    time2 = events.css('time.event-time-12hr-end::text').get()
                    time = time1 + " - " + time2

                item_loader.replace_value('date', date)
                item_loader.replace_value('time', time)
                item_loader.replace_value('website_url', 'https://www.canadianautomotivemuseum.com' + website_url)

            # ----- Art Gallery of Alberta -----
            elif 'youraga.ca' in response.url:
                date2 = events.css('span.end-date::text').get()
                if date2:
                    temp_date = temp_date + " - " + date2

                description = ''.join(
                    events.css('div.field.field--name-field-exh-teaser div.field-data *::text').getall())
                item_loader.replace_value('description', description.replace('\xa0', ' ').strip())

                item_loader.replace_value('title', temp_title.replace('\xa0', '').strip())
                item_loader.replace_value('date', temp_date.replace('\xa0', '').strip())
                item_loader.replace_value('website_url', 'https://www.youraga.ca' + website_url)
                item_loader.replace_value('image_url', 'https://www.youraga.ca' + image_url)

            return item_loader

        else:
            return None

    def close_spider(self, spider):
        self.con.close()
