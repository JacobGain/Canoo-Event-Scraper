from itemadapter import ItemAdapter
import sqlite3
import uuid


class EventscraperPipeline:

    def __init__(self):
        db_file = 'canooevents.db'
        self.con = sqlite3.connect(db_file)
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        # use the below line to reset the table at the beginning of each run during testing
        # self.cur.execute("DROP TABLE IF EXISTS events")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS events
        (id TEXT PRIMARY KEY, title TEXT, date TEXT, time TEXT, description TEXT, address TEXT, venue_name TEXT, image_url TEXT,
        website_url TEXT)""")

    def generate_event_id(self, item): # generated using title, date, img and website urls. If any of them change, it is classified as a new event
        unique_string = (
            f"{item.get('title', '')}_{item.get('date', '')}_{item.get('address', '')}_{item.get('venue_name', '')}_{item.get('image_url', '')}_{item.get('website_url', '')}")
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Set default values for missing fields
        title = adapter.get('title') or None
        date = adapter.get('date') or None
        time = adapter.get('time') or None
        description = adapter.get('description') or None
        address = adapter.get('address') or None
        venue_name = adapter.get('venue_name') or None
        image_url = adapter.get('image_url') or None
        website_url = adapter.get('website_url') or None

        unique_event_id = self.generate_event_id(adapter.asdict())

        self.cur.execute("SELECT id FROM events WHERE id=?", (unique_event_id,))
        existing_event = self.cur.fetchone()

        if existing_event:
            self.cur.execute("""UPDATE events SET title=?, date=?, time=?, description=?, address=?, venue_name=?, image_url=?, website_url=?
                                WHERE id=?""",
                             (title, date, time, description, address, venue_name, image_url, website_url,
                              unique_event_id))
            print(f"Event with id {unique_event_id} updated successfully.")
        else:
            self.cur.execute("""INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?)""",
                             (unique_event_id, title, date, time, description, address, venue_name, image_url,
                              website_url))
            print(f"Event with id {unique_event_id} stored successfully.")

        self.con.commit()
        return item

    def close_spider(self, spider):
        self.con.close()
