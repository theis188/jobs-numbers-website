
import sqlite3
import pandas as pd
import re
import numpy as np

DB_PATH = '../OE.db'
COLUMN_ORDER = ['slug','area_code','occupation_code','area_name','occupation_name','type','url']
_conn = sqlite3.connect(DB_PATH)

def get_home_df():
    slug = ''
    home_df = pd.DataFrame({
        'slug':[slug],
        'area_code':['N0000000'],
        'area_name':['National'],
        'occupation_code':[np.nan],
        'occupation_name':[np.nan],
        'type':'home',
        'url':[make_url(slug)],
    })
    home_df = home_df[COLUMN_ORDER]
    return home_df

def get_location_df():
    location_data = get_all_metro_codes()
    location_df = pd.DataFrame( location_data )
    location_df.columns = ['area_code','area_name']
    location_df['occupation_code'] = np.nan
    location_df['occupation_name'] = np.nan
    location_df['type'] = 'location'
    location_df['slug'] = location_df.area_name.apply( generate_slug_from_name )
    location_df['url'] = location_df.slug.apply( make_url )
    location_df = location_df[COLUMN_ORDER]
    return location_df

def get_occupation_df():
    occ_data = get_all_occ_codes()
    occ_df = pd.DataFrame(occ_data)
    occ_df.columns = ['occupation_code','occupation_name']
    occ_df['area_code'] = 'N0000000'
    occ_df['area_name'] = 'National'
    occ_df['type'] = 'occupation'
    occ_df['slug'] = occ_df.occupation_name.apply( generate_slug_from_name )
    occ_df['url'] = occ_df.slug.apply( make_url  )
    occ_df = occ_df[COLUMN_ORDER]
    return occ_df

def get_state_df():
    state_data = get_all_state_codes()
    state_df = pd.DataFrame( state_data )
    state_df.columns = ['area_code','area_name']
    state_df['occupation_code'] = np.nan
    state_df['occupation_name'] = np.nan
    state_df['type'] = 'state'
    state_df['slug'] = state_df.area_name.apply( generate_slug_from_name )
    state_df['url'] = state_df.slug.apply( make_url )
    state_df = state_df[COLUMN_ORDER]
    return state_df

def get_location_occ_group_df():
    loc_occ_data = get_all_location_occ_group_codes()
    loc_occ_df = pd.DataFrame(loc_occ_data)
    loc_occ_df.columns = ['area_code','area_name','occupation_code','occupation_name']
    loc_occ_df['type'] = 'location_occ_group'
    loc_occ_df['slug'] = (loc_occ_df['area_name']+' '+loc_occ_df['occupation_name']).apply( generate_slug_from_name )
    loc_occ_df['url'] = loc_occ_df.slug.apply( make_url )
    loc_occ_df = loc_occ_df[COLUMN_ORDER]
    return loc_occ_df

def get_all_slugs():
    home_df = get_home_df()
    state_df = get_state_df()
    location_df = get_location_df()
    occ_df = get_occupation_df()
    loc_occ_df = get_location_occ_group_df()
    ret_df = pd.concat([home_df, state_df, location_df, loc_occ_df])
    ret_df.to_sql( 'sitemap', _conn, if_exists='replace', index=False )

def generate_slug_from_name(location):
    chunks = re.findall( r'[a-z]+', location.lower() )
    slug = '-'.join(chunks) + '.html'
    return slug

def make_url(slug):
    ret = f'www.jobs-numbers.com/{slug}'
    return ret

def get_all_metro_codes():
    query = """SELECT code,name from area_code
                WHERE area_type_code IN ('M','N');"""
    cur = _conn.execute(query)
    results = cur.fetchall()
    return results

def get_all_state_codes():
    query = """SELECT code,name from area_code
                WHERE area_type_code='S';"""
    cur = _conn.execute(query)
    results = cur.fetchall()
    return results

def get_all_location_occ_group_codes():
    query = """
    SELECT distinct sc.area_code,ac.name,sc.occupation_code,oc.name from series_code sc
    JOIN area_code ac
    ON ac.code = sc.area_code
    JOIN occupation_code oc
    ON oc.code = sc.occupation_code
    WHERE sc.occupation_code LIKE '__0000';"""
    cur = _conn.execute(query)
    results = cur.fetchall()
    return results

def get_all_occ_codes():
    query = """SELECT code,name from occupation_code;"""
    cur = _conn.execute(query)
    results = cur.fetchall()
    return results
