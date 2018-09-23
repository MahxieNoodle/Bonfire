import asyncio
import rethinkdb as r
from datetime import datetime
from .checks import required_tables

from . import config


async def _convert_to_list(cursor):
    # This method is here because atm, AsyncioCursor is not iterable
    # For our purposes, we want a list, so we need to do this manually
    cursor_list = []
    while True:
        try:
            val = await cursor.next()
            cursor_list.append(val)
        except r.ReqlCursorEmpty:
            break
    return cursor_list


class Cache:
    """A class to hold the cached database entries"""

    def __init__(self, table, key, db, loop):
        self.table = table  # The name of the database table
        self.key = key  # The name of primary key
        self.db = db  # The database class connections are made through
        self.loop = loop
        self.values = {}  # The values returned from the database
        self.refreshed_time = None
        self.loop.create_task(self.refresh_task())

    async def refresh(self):
        self.values = await self.db.query(r.table(self.table).group(self.key)[0])
        self.refreshed_time = datetime.now()

    async def refresh_task(self):
        await self.check_refresh()
        await asyncio.sleep(60)

    async def check_refresh(self):
        if self.refreshed_time is None:
            await self.refresh()
        else:
            difference = datetime.now() - self.refreshed_time
            if difference.total_seconds() > 300:
                await self.refresh()

    def get(self, key=None, pluck=None):
        """This simulates the database call, to make it easier to get the data"""
        value = self.values
        if key:
            value = value.get(str(key))
            if pluck:
                value = value.get(pluck)

        return value


class DB:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.opts = config.db_opts
        self.cache = {}

        for table, key in required_tables.items():
            self.cache[table] = Cache(table, key, self, self.loop)

    async def query(self, query):
        """Lets you run a manual query"""
        r.set_loop_type("asyncio")
        conn = await r.connect(**self.opts)
        try:
            cursor = await query.run(conn)
        except (r.ReqlOpFailedError, r.ReqlNonExistenceError):
            cursor = None
        if isinstance(cursor, r.Cursor):
            cursor = await _convert_to_list(cursor)
        await conn.close()
        return cursor

#    def save(self, table, content):
#        """A synchronous task to throw saving content into a task"""
#        self.loop.create_task(self._save(table, content))

    async def save(self, table, content):
        """Saves data in the table"""

        index = await self.query(r.table(table).info())
        index = index.get("primary_key")
        key = content.get(index)
        if key:
            cur_content = await self.query(r.table(table).get(key))
            if cur_content:
                # We have content...we either need to update it, or replace
                # Update will typically be more common so lets try that first
                result = await self.query(r.table(table).get(key).update(content))
                if result.get('replaced', 0) == 0 and result.get('unchanged', 0) == 0:
                    await self.query(r.table(table).get(key).replace(content))
            else:
                await self.query(r.table(table).insert(content))
        else:
            await self.query(r.table(table).insert(content))

        await self.cache.get(table).refresh()

    def load(self, table, **kwargs):
        return self.cache.get(table).get(**kwargs)

    async def actual_load(self, table, key=None, table_filter=None, pluck=None):
        """Loads the specified content from the specific table"""
        query = r.table(table)

        # If a key has been provided, get content with that key
        if key:
            query = query.get(str(key))
        # A key and a filter shouldn't be combined for any case we'll ever use, so seperate these
        elif table_filter:
            query = query.filter(table_filter)

        # If we want to pluck something specific, do that
        if pluck:
            query = query.pluck(pluck).values()[0]

        cursor = await self.query(query)

        return cursor
