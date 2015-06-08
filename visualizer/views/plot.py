from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

import constants
import json

import pickle
import zlib
import pandas as pd
import sqlite3 as lite
import time

from collections import OrderedDict
from django.http import HttpResponse
from bokeh.plotting import *
from bokeh.embed import autoload_server
from bokeh.models import HoverTool, TapTool, OpenURL, ColumnDataSource, Callback, GlyphRenderer


def unpickle_data(data):
    try:
        data = zlib.decompress(data)
    except:
        pass
    return pickle.loads(data)


def get_data():

    with lite.connect(constants.database_url, detect_types=lite.PARSE_COLNAMES) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT result_id, generation, result.configuration_id as conf_id, time,requestor,was_new_best, "
            + " collection_date as 'ts [timestamp]', configuration.data as conf_data "
            + " FROM result "
            + " JOIN desired_result ON desired_result.result_id = result.id  "
            + " JOIN configuration ON configuration.id =  result.configuration_id  "
            + " WHERE result.state='OK' "
            + " ORDER BY collection_date"
        )
        rows = cur.fetchall()

    cols = ["result_id", "generation", "conf_id", "time", "requestor", "was_new_best", "timestamp", "conf_data"]
    data = pd.DataFrame(rows, columns=cols)[["result_id", "time", "was_new_best", "timestamp", "conf_id"]]

    grouped = data.groupby('was_new_best')

    colors = ["red" if (val == 1) else "blue" for val in data['was_new_best'].values]

    return data, grouped.get_group(1), colors

initialized = False

def timestamp(data):
    return (data - data[0])/1000000000

def initialize_plot():
    global p, source, source_best, initialized, cur_session
    initialized = True
    data, best_data, colors = get_data()
    source = ColumnDataSource(data=dict(
        x=timestamp(data['timestamp']),
        y=data['time'],
        conf_id=data['conf_id'],
        fill_color=colors
    ))

    source_best = ColumnDataSource(data=dict(
        x=timestamp(best_data['timestamp']),
        y=best_data['time'],
        conf_id=best_data['conf_id']
    ))

    TOOLS = "resize,crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave,tap," \
            "box_select,lasso_select,poly_select"
    output_server("opentuner2")
    p = figure(
        tools=TOOLS, title="OpenTuner",
        x_axis_label='Time in seconds', y_axis_label='Result Time'
    )

    p.circle('x', 'y', conf_id='conf_id', fill_color='fill_color', line_color=None, source=source, size=5)
    p.line('x', 'y', conf_id='conf_id', line_color="red", source=source_best, size=5)

    callback = Callback(args=dict(source=source), code="""
        var arr = cb_obj.get('selected')['1d'].indices;
        if(arr.length > 0) {
            var data = [];
            for(var i = 0; i<arr.length; ++i) {
                data.push(cb_obj.get('data')['conf_id'][arr[i]]);
            }
            update_conf_details(data);
        }
    """)

    source.callback=callback

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
        ("Configuration ID", "@conf_id"),
        ("Timestamp", "@x"),
        ("Time", "@y")
    ])
    show(p)
    cur_session = cursession()


def update_plot():
    global p, source, source_best
    data, best_data, colors = get_data()
    source.data['x'] = timestamp(data['timestamp'])
    source.data['y'] = data['time']
    source.data['conf_id'] = data['conf_id']
    source.data['fill_color'] = colors

    source_best.data['x'] = timestamp(best_data['timestamp'])
    source_best.data['y'] = best_data['time']
    source_best.data['conf_id'] = best_data['conf_id']

    cur_session.store_objects(source)
    cur_session.store_objects(source_best)


def get_plot_html():
    global p
    return autoload_server(p, cursession())


def index(request):
    global initialized
    if not initialized:
        initialize_plot()
    return render(request, 'plot.html', {'script_js': mark_safe(get_plot_html())})


def update(request):
    update_plot()
    return HttpResponse("success")


def config(request, points_id):
    print(points_id)
    with lite.connect(constants.database_url) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT configuration.data as conf_data, configuration.id"
            + " FROM configuration"
            + " WHERE configuration.id in (%s)" % points_id
        )
        rows = cur.fetchall()
        data = [(unpickle_data(d[0]), d[1]) for d in rows]

        table_data = []

        for key in data[0][0]:
            record = {'name': key}
            equal = True
            value = data[0][0][key]
            for i in range(len(data)):
                if (len(data) < 5):
                    record[str(data[i][1])] = data[i][0][key]
                #if value == 'default':
                #    value = data[i][0][key]
                #if equal and (data[i][0][key] != 'default') and (data[i][0][key] != data[0][0][key]):
                if equal and (data[i][0][key] != value):
                    equal = False

            record['equal'] = equal
            if (len(data) >= 5):
                if equal:
                    record['value'] = value
                else:
                    record['value'] = 'Unequal'
            table_data.append(record)

        def cmp_items(a, b):
            if a['equal'] :
                if b['equal'] :
                    return -1 if a['name'] < b['name'] else 1
                return -1
            if b['equal']:
                return 1
            return -1 if a['name'] < b['name'] else 1
        table_data.sort(cmp_items)
        if (len(data)<5):
            columns = [str(data[i][1]) for i in range(len(rows))]
        else:
            columns = ['Value']
        response_data = {'data': table_data, 'columns': ['Name'] + columns}

    return HttpResponse(json.dumps(response_data), content_type="application/json")

