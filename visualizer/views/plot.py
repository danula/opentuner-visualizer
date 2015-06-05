from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

import constants
import json

import pickle
import zlib
import pandas as pd
import sqlite3 as lite

from collections import OrderedDict
from django.http import HttpResponse
from bokeh.plotting import *
from bokeh.models import HoverTool, TapTool, BoxSelectTool, LassoSelectTool, \
    OpenURL, ColumnDataSource, Callback, GlyphRenderer


def unpickle_data(data):
    try:
        data = zlib.decompress(data)
    except:
        pass
    return pickle.loads(data)


def get_data():
    with lite.connect(constants.database_url) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT result_id, generation, result.configuration_id as conf_id, time,requestor,was_new_best, "
            " configuration.data as conf_data "
            + " FROM result "
            + " JOIN desired_result ON desired_result.result_id = result.id  "
            + " JOIN configuration ON configuration.id =  result.configuration_id  "
            + " WHERE result.state='OK' "
        )
        rows = cur.fetchall()

    cols = ["result_id", "generation", "conf_id", "time", "requestor", "was_new_best", "conf_data"]
    data = pd.DataFrame(rows, columns=cols)[["result_id", "time", "was_new_best", "conf_id"]]

    grouped = data.groupby('was_new_best')

    colors = ["red" if (val == 1) else "blue" for val in data['was_new_best'].values]

    return data, grouped.get_group(1), colors


initialized = False
plot_id = 'opentuner2'

def initialize_plot():
    global initialized
    initialized = True
    data, best_data, colors = get_data()

    source = ColumnDataSource(
        data=dict(
            x=data['result_id'],
            y=data['time'],
            conf_id=data['conf_id'],
            fill_color=colors
        ),
        id=plot_id + 'source'
    )

    source_best = ColumnDataSource(
        data=dict(
            x=best_data['result_id'],
            y=best_data['time'],
            conf_id=best_data['conf_id']
        ),
        id=plot_id + 'source_best'
    )

    TOOLS = "resize,crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave,tap,box_select,lasso_select," \
            "poly_select"
    output_server(plot_id)
    p = figure(
        tools=TOOLS, title="OpenTuner",
        x_axis_label='Result id', y_axis_label='time',
        id=plot_id + 'figure'
    )

    p.circle('x', 'y', conf_id='conf_id', fill_color='fill_color', line_color=None, source=source, size=5)
    p.line('x', 'y', conf_id='conf_id', line_color="red", source=source_best, size=5)

    callback = Callback(args=dict(source=source), code="""
        var arr = cb_obj.get('selected')['1d'].indices;
        if(arr.length > 0) {
            var data = [];
            for(var i = 0; i<arr.length; ++i) {
                data.push(cb_obj.get('data')['x'][arr[i]]);
            }
            update_conf_details(data);
        }
    """)

    source.callback = callback

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
        ("Configuration ID", "@conf_id"),
        ("Result id", "@x"),
        ("Time", "@y")
    ])
    show(p)


def update_plot():
    output_server(plot_id)
    data, best_data, colors = get_data()

    source = ColumnDataSource(
        data=dict(
            x=data['result_id'],
            y=data['time'],
            conf_id=data['conf_id'],
            fill_color=colors
        ),
        id=plot_id + 'source'
    )

    source_best = ColumnDataSource(
        data=dict(
            x=best_data['result_id'],
            y=best_data['time'],
            conf_id=best_data['conf_id']
        ),
        id=plot_id + 'source_best'
    )

    cursession().store_objects(source)
    cursession().store_objects(source_best)

def get_plot_html():
    import uuid
    from bokeh.resources import Resources
    from bokeh.templates import AUTOLOAD_SERVER
    from bokeh.util.string import encode_utf8
    elementid = str(uuid.uuid4())
    resources = Resources(root_url=cursession().root_url, mode="server")
    tag = AUTOLOAD_SERVER.render(
        src_path = resources._autoload_path(elementid),
        elementid = elementid,
        modelid = plot_id + 'figure',
        root_url = resources.root_url,
        docid =  cursession().docid,
        docapikey = cursession().apikey,
        loglevel = resources.log_level,
        public = False
    )
    return encode_utf8(tag)

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
            "SELECT configuration.data as conf_data, result.id"
            + " FROM result "
            + " JOIN configuration ON configuration.id =  result.configuration_id  "
            + " WHERE result.state='OK' AND result.id in (%s)" % points_id
        )
        rows = cur.fetchall()
        data = [(unpickle_data(d[0]), d[1]) for d in rows]

        table_data = []

        for key in data[0][0]:
            record = {'name': key}
            for i in range(len(data)):
                record[str(data[i][1])] = data[i][0][key]
            table_data.append(record)

        response_data = {'data': table_data, 'columns': ['Name'] + [str(data[i][1]) for i in range(len(rows))]}

    return HttpResponse(json.dumps(response_data), content_type="application/json")

