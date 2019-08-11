import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import sqlite3
import pandas as pd
import re
import os
from operator import __add__


# slug = 'wisconsin.html'
# jline = route_build_page(slug)

# data = jline['child_data']
# data = jline['data']

occupation_name = "Occupational Therapists"
area_name = "Riverside-San Bernardino-Ontario, CA"

_conn = sqlite3.connect( 'OE.db' )
_fig, _ax = plt.subplots()

def row_sum(row):
    return ''.join(row)

def generate_all_figures():
    df = get_all_data_for_figures()
    counter = 0
    grouped = df.groupby(['area_name','occupation_name'])['value'].max()
    grouped_df = grouped.reset_index()
    good_grouped_df = grouped_df[  grouped_df.value >750  ]
    good_grouped_df['area_name']+good_grouped_df['occupation_name']
    bool_suitable_data_from_main_df = (
        df['area_name']+df['occupation_name']
        ).isin( good_grouped_df['area_name']+good_grouped_df['occupation_name'] )
    sub_df = df[ bool_suitable_data_from_main_df ]
    sub_df.groupby(['area_name','occupation_name']).head(1).shape[0]
    indexed_df = sub_df.sort_values(['area_name','occupation_name','year']).set_index(['area_name','occupation_name','year'])
    for area_name in set( indexed_df.index.get_level_values(0) ):
        # area_name = 'Bloomington, IN'
        area_df = indexed_df.ix[area_name]
        for occupation_name in set( area_df.index.get_level_values(0) ):
            # occupation_name = 'Accountants and Auditors'
            area_occupation_df = area_df.ix[occupation_name]
            x_data = area_occupation_df.index
            y_data = area_occupation_df.value
            print(f'{area_name} {occupation_name} {counter}')
            plot_data(x_data,y_data,area_name,occupation_name)
            counter+=1


def get_all_data_for_figures():
    query = """SELECT o.code occupation_code,o.name occupation_name,
            a.code area_code,a.name area_name,
            v.value, v.year
        FROM value v, series_code sc, area_code a, occupation_code o
        WHERE v.series_code = sc.code
        AND sc.industry_code = '000000'
        AND sc.data_type = '01'
        AND sc.occupation_code = o.code
        AND sc.area_code = a.code
        ORDER BY 1,3,6 asc;"""
    cur = _conn.execute(query)
    results = cur.fetchall()
    df = pd.DataFrame( results )
    df.columns = ['occupation_code','occupation_name',
                    'area_code','area_name',
                    'value','year']
    df['value'] = df.value.apply( to_float )
    # df.pivot_table(index=['area_name','occupation_name'], columns=['year'], values=['value'])
    return df

def to_float(s):
    try:
        return float(s)
    except:
        return np.nan

def truncate_string(s,n=40):
    if len(s)<40:
        return s
    return s[:40]+'...'


def plot_data(x_data,y_data,area_name,occupation_name):
    if len(x_data) < 5:
        return
    figure_filename = make_filename_from_area_and_occupation_name(area_name, occupation_name)
    truncated_area_name = truncate_string(area_name)
    truncated_occupation_name = truncate_string(occupation_name)
    figure_path = f'images/{figure_filename}.png'
    if os.path.exists(figure_path):
        print(f'image exists {figure_path}')
        return
    title = f"{truncated_occupation_name} \nin {truncated_area_name}"
    y_ticks,y_limits = get_y_axis_ticks_and_limits(y_data)
    x_ticks,x_limits = get_x_axis_ticks_and_limits(x_data)
    plt.clf()
    is_thousands_necessary = max(y_data) > 10000
    thousands_plot_text = '\n(Thousands)' if is_thousands_necessary else ''
    thousands_divisor = 1000 if is_thousands_necessary else 1
    plt.ylim( y_limits )
    plt.yticks( y_ticks , 
                [f'{int(y_ticks[0]//thousands_divisor):,}',
                f'{int(y_ticks[1]//thousands_divisor):,}'], fontsize=12)
    plt.xlim( x_limits )
    plt.xticks( x_ticks , fontsize=12 )
    _ax.spines['right'].set_visible(False)
    _ax.spines['top'].set_visible(False)
    _fig.set_size_inches(6,3.5)
    plt.plot(x_data,y_data, linewidth=3)
    plt.title(title)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel(f'Number of Jobs{thousands_plot_text}', fontsize=12)
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'images/{figure_filename}.png')


def get_y_axis_ticks_and_limits(y_data):
    round_nums = np.array( sum( [[1*10**i,2*10**i,5*10**i] for i in range(8)], [] ) )
    min_y_value = min(y_data)
    max_y_value = max(y_data)
    round_divisor_index = np.argmax( [max_y_value//rn < 20 for rn in round_nums] )
    round_divisor = round_nums[round_divisor_index]
    max_y_tick = ( (max_y_value + round_divisor * 0.2)//round_divisor + 1 ) * round_divisor
    max_y_limit = max_y_tick*1.04
    min_y_tick =  min_y_value*0.8 // round_divisor * round_divisor
    min_y_limit = min_y_tick*0.96
    y_ticks = [min_y_tick, max_y_tick]
    y_limits = [min_y_limit, max_y_limit]
    return y_ticks,y_limits


def get_x_axis_ticks_and_limits(x_data):
    years = np.array( [ 2000,2005,2010,2015,2020 ] )
    min_x_value = min(x_data)
    max_x_value = max(x_data)
    min_x_limit = min_x_value - 1
    max_x_limit = max_x_value + 1
    x_limits = [min_x_limit, max_x_limit]
    min_x_tick_ind = np.argmax( years > min_x_limit )
    max_x_tick_ind = years.shape[0] - 1 - np.argmax( years[::-1] < max_x_limit )
    x_ticks = years[min_x_tick_ind: max_x_tick_ind+1 ]
    return x_ticks, x_limits


def make_filename_from_area_and_occupation_name(area_name,occupation_name):
    area_groups = re.findall( r'[a-z]+' , area_name.lower() )
    occupation_groups = re.findall( r'[a-z]+' , occupation_name.lower() )
    area_slug = '-'.join(area_groups)
    occupation_slug = '-'.join(occupation_groups)
    name = f'{area_slug}_{occupation_slug}'
    return name


