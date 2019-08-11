
import redis
import json
import sqlite3
from collections import defaultdict
import pandas as pd
import time
import os

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
_r = redis.Redis(connection_pool=pool)

dirpath = os.path.dirname(os.path.abspath(__file__))
DB_NAME = 'OE.db'
DB_PATH = os.path.join( dirpath, DB_NAME )


def make_key(fun,args):
    args_str = '-'.join( args )
    ret = f'{fun.__name__}_{args_str}'
    return ret

def get_results_from_sql_query(query,params=[]):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(query,params)
    results = cur.fetchall()
    conn.close()
    return results

def redis_cache(query_fun):
    def wrapper_fun(*args):
        key = make_key( query_fun, args )
        print(key)
        if _r.exists(key):
            print('cached',key)
            return _r.get(key)
        else:
            ret = query_fun(*args)
            _r.set(key,ret)
            print('uncached',key)
            return ret
    return wrapper_fun

def json_formatter(fun):
    def wrapper(*args):
        s = fun(*args)
        ret = json.loads(s)
        return ret
    return wrapper

def string_formatter(fun):
    def wrapper(*args):
        obj = fun(*args)
        ret = json.dumps(obj)
        return ret
    return wrapper

def timer(fun):
    def wrapper(*args):
        start = time.time()
        ret = fun(*args)
        end = time.time()
        print(f'complete in {end-start}s')
        return ret
    return wrapper

@timer
@json_formatter
@redis_cache
@string_formatter
def route_build_page(slug):
    page = {}
    route_map = {
        'home':build_home_page,
        'state':build_state_page,
        'location':build_location_page,
        'location_occ_group':build_location_occ_group_page,
        'sitemap':get_sitemap_query,
    }
    try:
        type_str = get_type_str(slug)
        fun = route_map[ type_str ]
        page = fun(slug)
        page['type'] = type_str
    except (KeyError, IndexError):
        page = {'type':'404'}
    return page

def get_type_str(slug):
    CHECK_FIRST = {
        '':'home',
        '/':'home',
        'index.html':'home',
        'sitemap':'sitemap',
    }
    if slug in CHECK_FIRST:
        return CHECK_FIRST[slug]
    query = """SELECT type
    FROM sitemap
    WHERE slug=?;"""
    results = get_results_from_sql_query(query,params=[slug])
    ret = results[0][0]
    return ret

### HOME PAGE

def build_home_page(slug):
    state_links = get_all_state_links()
    occ_links = get_national_occupations_for_homepage()
    ret = {
        'state_links':state_links,
        'occupation_links':occ_links,
    }
    return ret

def get_all_state_links():
    query = """SELECT s.url,s.area_name
        FROM sitemap s
        WHERE type='state'
        ;"""
    results = get_results_from_sql_query(query)
    ret = [{'url':url,'name':name} for url,name in results]
    return ret

def get_national_occupations_for_homepage():
    query = """SELECT url,occupation_name
    FROM sitemap
    WHERE occupation_code LIKE '__0000'
    AND area_code = 'N0000000'
    AND type='location_occ_group';
    """
    results = get_results_from_sql_query(query)
    ret = [{'url':url,'name':name} for url,name in results]
    return ret

### LOCATION PAGE

def build_location_page(slug):
    title = get_area_name_from_sitemap_slug(slug)
    data = get_location_data(slug)
    url = get_url_from_sitemap_slug(slug)
    ## related_locations
    ret = {
        'title':title,
        'data':data,
        'url':url,
    }
    return ret

def get_area_name_from_sitemap_slug(slug):
    query = """SELECT area_name from sitemap
                WHERE slug=?;"""
    results = get_results_from_sql_query(query,params=[slug])
    ret = results[0][0]
    return ret

def get_url_from_sitemap_slug(slug):
    query = """SELECT url from sitemap
                WHERE slug=?;"""
    results = get_results_from_sql_query(query,params=[slug])
    ret = results[0][0]
    return ret

def get_location_data(slug):
    query = """SELECT o.code,o.name,v.year,v.value
    FROM value v, series_code sc, occupation_code o
    WHERE v.series_code IN (
        SELECT sc.code from 
        series_code sc, occupation_code o, sitemap sm
        WHERE o.code = sc.occupation_code
        AND o.code LIKE '__0000'
        AND sm.area_code=sc.area_code
        AND sm.slug=?
        and sc.industry_code='000000'
        and sc.data_type='01'
    )
    AND v.series_code = sc.code
    AND o.code = sc.occupation_code
    order by 1 asc, 2 asc
    ;"""
    results = get_results_from_sql_query(query,params=[slug])
    ret = structure_location_data_query(results,slug)
    return ret

def get_location_occ_group_url_dict_from_loc_slug(slug):
    query = """SELECT s.url,s.occupation_name FROM sitemap s
        JOIN sitemap s2
        ON s.area_code = s2.area_code
        WHERE s.type='location_occ_group'
        AND s2.slug=?;"""
    results = get_results_from_sql_query(query,params=[slug])
    ret = {name:url for url,name in results}
    return ret

def get_location_entry_from_code_df(arg_code_df,occ_url_dict):
        x_data = list(arg_code_df.index)
        y_data = list(arg_code_df['value'])
        name = arg_code_df.ix[:,'name'].iloc[0]
        url = occ_url_dict[name]
        ret = {
            'x_data':x_data,
            'y_data':y_data,
            'name':name,
            'url':url,
        }
        return ret

def structure_location_data_query(results,slug):
    occ_url_dict = get_location_occ_group_url_dict_from_loc_slug(slug)
    ret = {}
    ret_data = []
    df = pd.DataFrame(results)
    df.columns = ['code','name','year','value']
    df['year'] = df['year'].astype('int64')
    df['first_two'] = df.code.apply( lambda x: x[:2] )
    indexed_df = df.set_index(['first_two','code','year'])
    all_first_two = sorted(list(set( indexed_df.index.get_level_values(0) )))
    for first_two in all_first_two:
        sub_df = indexed_df.ix[first_two]
        sub_codes_set = set( sub_df.index.get_level_values(0) )
        major_code = first_two + '0000'
        code_df = sub_df.ix[major_code].sort_values('year')
        major_entry = get_location_entry_from_code_df(code_df,occ_url_dict)
        # for code in rest_of_codes:
        #     code_df = sub_df.ix[ code ].sort_values('year')
        #     code_entry = get_location_entry_from_code_df(code_df)
        #     child_occs.append( code_entry )
        # sub_ret['child_occs'] = child_occs
        ret_data.append( major_entry )
    return ret_data

### STATE
def build_state_page(slug):
    page = build_location_page(slug)
    metro_data = get_metros_in_state(slug)
    page['metros'] = metro_data
    return page

def get_metros_in_state(slug):
    query = """SELECT s2.area_name,s2.url
                FROM area_code ac
                JOIN sitemap s
                ON s.area_code = ac.code
                JOIN area_code ac2
                ON ac.state_code = ac2.state_code
                JOIN sitemap s2
                ON ac2.code = s2.area_code
                AND s2.type = 'location'
                WHERE s.slug=?;"""
    results = get_results_from_sql_query(query,params=[slug])
    ret = [{'name':name, 'url':url } for name,url in results ]
    return ret    

### LOCATION_OCC_GROUP

def build_location_occ_group_page(slug):
    query = """SELECT o.code,o.name,v.year,v.value 
    FROM value v, occupation_code o, series_code sc
    WHERE v.series_code IN
    (
        SELECT sc.code FROM series_code sc
        WHERE sc.area_code = (SELECT area_code from sitemap where slug = ? )
        AND sc.occupation_code IN (
            SELECT code from occupation_code o
            WHERE substr(code,1,2) = (
                SELECT substr(occupation_code,1,2) FROM sitemap 
                WHERE slug = ?
            )
        )
        AND SC.industry_code = '000000'
    )
    AND sc.code = v.series_code
    AND o.code = sc.occupation_code
    order by 1 asc, 2 asc;"""
    results = get_results_from_sql_query(query,params=[slug,slug])
    ret = structure_location_occ_group_data_query(results,slug)
    area_name = get_area_name_from_sitemap_slug(slug)
    occ_name = get_occupation_name_from_sitemap_slug(slug)
    ret['title'] = occ_name + ' Statistics in ' + area_name
    ret['area_name'] = area_name
    ret['occupation_name'] = occ_name
    return ret

def get_location_entry_from_code_df_occ_grp(arg_code_df):
        x_data = list(arg_code_df.index)
        y_data = list(arg_code_df['value'])
        name = arg_code_df.ix[:,'name'].iloc[0]
        ret = {
            'x_data':x_data,
            'y_data':y_data,
            'name':name,
        }
        return ret

def structure_location_occ_group_data_query(results,slug):
    df = pd.DataFrame(results)
    df.columns = ['code','name','year','value']
    df['year'] = df['year'].astype('int64')
    df = df.sort_values( ['code','year'] )
    indexed_df = df.set_index(['code','year'])
    all_codes = set( df.code )
    any_code = df.code[0]
    parent_code = any_code[:2]+'0000'
    code_df = indexed_df.ix[parent_code]
    ret = {
        'parent_data':get_location_entry_from_code_df_occ_grp(code_df)
    }
    child_occs = []
    rest_codes = all_codes - {parent_code}
    for code in sorted(rest_codes):
        sub_df = indexed_df.ix[code]
        child_datum = get_location_entry_from_code_df_occ_grp(sub_df)
        child_occs.append(child_datum)
    ret['child_data'] = child_occs
    return ret

def get_occupation_name_from_sitemap_slug(slug):
    query = """SELECT occupation_name from sitemap
                WHERE slug=?;"""
    results = get_results_from_sql_query(query,params=[slug])
    ret = results[0][0]
    return ret

### SITEMAP

def get_sitemap_query(*args):
    query = """SELECT url from sitemap;"""
    results = get_results_from_sql_query(query,params=[])
    urls = [r[0] for r in results]
    return {'urls':urls}
    
### OCCUPATION

def build_occupation_page(slug):
    pass ## todo

if __name__ == '__main__':
    print(os.path.abspath(__file__))


