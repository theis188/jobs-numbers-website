
import redis
import json
import sqlite3
from collections import defaultdict
import pandas as pd
import time
import requests

print(__name__)

from redis_caching import route_build_page

DB_PATH = 'OE.db'

_conn = sqlite3.connect(DB_PATH)

def get_all_slugs():
    query = """SELECT slug
                FROM sitemap;"""
    cur = _conn.execute(query)
    results = cur.fetchall()
    ret = [row[0] for row in results]
    return ret

# if __name__ == '__main__':
all_slugs = get_all_slugs()

for k,slug in enumerate(all_slugs):
    print(k,slug)
    _=route_build_page( slug )