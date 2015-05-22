import constants

import pickle
import time
import zlib
import pandas as pd
import sqlite3 as lite
import webbrowser
from os import path
from collections import OrderedDict

from bokeh.plotting import *
from bokeh.embed import autoload_server
from bokeh.models import HoverTool, TapTool, OpenURL, ColumnDataSource, Callback, GlyphRenderer

con = lite.connect(constants.database_url)
cur = con.cursor()


def unpickle_data(data):
    try:
        data = zlib.decompress(data)
    except:
        pass
    return pickle.loads(data)


def get_data():
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
    data = pd.DataFrame(rows, columns=cols)[["result_id", "time", "was_new_best", "conf_id", "conf_data"]]

    for i, val in enumerate(data['conf_data']):
        data['conf_data'][i] = unpickle_data(val)

    grouped = data.groupby('was_new_best')

    colors = ["red" if (val == 1) else "blue" for val in data['was_new_best'].values]

    return data, grouped.get_group(1), colors


data, best_data, colors = get_data()

print(data)
source = ColumnDataSource(data=dict(
    x=data['result_id'],
    y=data['time'],
    conf_id=data['conf_id'],
    conf_data=data['conf_data'],
    fill_color=colors
))

source_best = ColumnDataSource(data=dict(
    x=best_data['result_id'],
    y=best_data['time'],
    conf_id=best_data['conf_id'],
    conf_data=data['conf_data']
))

TOOLS = "resize,crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave,tap"
print("asd")
output_server("opentuner2")
print("asd")
p = figure(
    tools=TOOLS, title="OpenTuner",
    x_axis_label='Result id', y_axis_label='time'
)

p.circle('x', 'y', conf_id='conf_id', fill_color='fill_color', line_color=None, source=source, size=3)
p.line('x', 'y', conf_id='conf_id', line_color="red", source=source_best, size=3)

callback = Callback(args=dict(source=source), code="""
    var arr = cb_obj.get('selected')['1d'].indices;
    if(arr.length > 0) {
        var d = cb_obj.get('data')['conf_data'][arr[0]];
        update_conf_details(d);
        console.log(d);
    }
""")

taptool = p.select(dict(type=TapTool))
taptool.action = callback

hover = p.select(dict(type=HoverTool))
hover.tooltips = OrderedDict([
    ("Configuration ID", "@conf_id"),
    ("Result id", "@x"),
    ("Time", "@y")
])

# TODO: fix this
with open('plot.html.in') as filein:
    src = filein.read()
    src = src.replace('$script_js$', autoload_server(p, cursession()))
    with open('plot.html', 'w') as fileout:
        fileout.write(src)

url = "file:" + path.dirname(path.realpath(__file__)) + "/plot.html"
webbrowser.open(url, new=2)

show(p)

while True:
    data, best_data, colors = get_data()
    source.data['x'] = data['result_id']
    source.data['y'] = data['time']
    source.data['conf_id'] = data['conf_id']
    source.data['fill_color'] = colors

    source_best.data['x'] = best_data['result_id']
    source_best.data['y'] = best_data['time']
    source_best.data['conf_id'] = best_data['conf_id']

    cursession().store_objects(source)
    time.sleep(.50)
