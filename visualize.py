import constants

import pickle
import time
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


def get_configs():
    cur.execute("SELECT id, data FROM configuration")
    rows = cur.fetchall()
    configs = dict()
    for row in rows:
        try:
            a = pickle.loads(row[1])
            configs[row[0]] = a
        except:
            pass
    return configs

def get_data():
    cur.execute("SELECT result_id, generation, desired_result.configuration_id, time,requestor,was_new_best "
                + "FROM desired_result INNER JOIN result ON desired_result.result_id = result.id WHERE result.state='OK'")
    rows = cur.fetchall()

    cols = ["result_id", "generation", "configuration_id", "time", "requestor", "was_new_best"]
    data = pd.DataFrame(rows, columns=cols)[["result_id", "time", "was_new_best", "configuration_id"]]

    grouped = data.groupby('was_new_best')

    colors = ["red" if (val == 1) else "blue" for val in data['was_new_best'].values]

    return data, grouped.get_group(1), colors


data, best_data, colors = get_data()

source = ColumnDataSource(data=dict(
    x=data['result_id'],
    y=data['time'],
    conf_id=data['configuration_id'],
    fill_color=colors
))

source_best = ColumnDataSource(data=dict(
    x=best_data['result_id'],
    y=best_data['time'],
    conf_id=best_data['configuration_id']
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
        console.log(cb_obj.get('data')['x'][arr[0]]);
    }
    console.log(cb_obj.get('selected')['1d'].indices);
    /*callfunction(this);*/
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
    source.data['conf_id'] = data['configuration_id']
    source.data['fill_color'] = colors

    source_best.data['x'] = best_data['result_id']
    source_best.data['y'] = best_data['time']
    source_best.data['conf_id'] = best_data['configuration_id']

    cursession().store_objects(source)
    time.sleep(.50)
