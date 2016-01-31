from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

import constants
import json

import pickle
import zlib
import pandas as pd
import sqlite3 as lite
import numpy as np
import time
import opentuner

from collections import OrderedDict
from django.http import HttpResponse
from bokeh.plotting import *
from bokeh.embed import autoload_server
from bokeh.models import HoverTool, TapTool, OpenURL, ColumnDataSource, Callback, GlyphRenderer
from copy import deepcopy
from visualizer.utils import unpickle_data, get_zero_to_one_values
from sklearn.linear_model import (RandomizedLasso, lasso_stability_path,
                                  LassoLarsCV)

def get_data():
    with lite.connect(constants.database_url, detect_types=lite.PARSE_COLNAMES) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT result_id, generation, result.configuration_id as conf_id, time,requestor,was_new_best, "
            + " collection_date as 'ts [timestamp]', configuration.data as conf_data "
            + " FROM result "
            + " JOIN desired_result ON desired_result.result_id = result.id  "
            + " JOIN configuration ON configuration.id =  result.configuration_id  "
            + " WHERE result.state='OK' AND time < 1000000 "
            # Add this line for JVM
            + " AND result.tuning_run_id=1 "
            + " ORDER BY collection_date"
        )
        rows = cur.fetchall()

    cols = ["result_id", "generation", "conf_id", "time", "requestor", "was_new_best", "timestamp", "conf_data"]
    data = pd.DataFrame(rows, columns=cols)[["result_id", "time", "was_new_best", "timestamp", "conf_id", "conf_data"]]
    for i, val in enumerate(data['conf_data']):
        data['conf_data'][i] = unpickle_data(val)
    return data

def get_configs(data):
    with open(constants.manipulator_url, "r") as f1:
        manipulator = unpickle_data(f1.read())
        keys = [0]*len(manipulator.params)
        confs = np.ndarray(shape=(len(data), len(keys)), dtype=float)
        for j, p in enumerate(manipulator.params):
            keys[j] = p.name
            if p.is_primitive():
                for i, d in enumerate(data['conf_data']):
                    print(i, j)
                    confs[i][j] = p.get_unit_value(d)
            elif isinstance(p, opentuner.search.manipulator.EnumParameter):
                options = p.options
                for i, d in enumerate(data['conf_data']):
                    try:
                        confs[i][j] = (options.index(p.get_value(d)) + 0.4999) / len(options)
                    except:
                        #print("Invalid Configuration", p, p.name, d)
                        confs[i][j] = 0
    return confs, keys

initialized = False


def timestamp(data):
    return (data - data[0]) / 1000000000


def initialize_plot():
    global p, source, source_best, initialized, cur_session, highlighted_flags, manipulator
    highlighted_flags = None
    initialized = True
    data = get_data()
    confs, keys = get_configs(data)
    TOOLS = "resize,crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave,tap," \
            "box_select,lasso_select,poly_select"

    output_server("opentuner3")
    p = figure(
        tools=TOOLS, title="OpenTuner",
        x_axis_label='Square(alpha/alpha_max)', y_axis_label='Stability score'
    )

    alpha_grid, scores_path = lasso_stability_path(confs, data['time'], random_state=42, eps=0.05)

    print("==========================================================")
    print(scores_path)
    print(type(scores_path))
    print("alpha_grid")
    print(alpha_grid)
    print(alpha_grid[1:].shape)
    print("scores_path")
    print(scores_path.T[1:].shape)
    print(len(keys))
    print("==========================================================")
    # import matplotlib.pyplot as plt
    # plt.plot(alpha_grid[1:] ** .333, scores_path.T[1:], 'r')
    for i in range(len(keys)):
        found = False
        print(keys[i])
        data = ColumnDataSource(data=dict(
            x=((alpha_grid[1:])**2.00).tolist(),
            y=scores_path[i][1:],
            conf_id=keys[i]
        ))
        p.line('x', 'y', conf_id='conf_id', line_color="red", source=data, size=5)


    hover = p.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
         ("Configuration ID", "@x"),
         ("Timestamp", "@conf_id")
    ])
    show(p)
    cur_session = cursession()


def get_plot_html():
    global p
    return autoload_server(p, cursession())


def index(request):
    global initialized
    if not initialized:
        initialize_plot()
    return render(request, 'plot.html', {'script_js': mark_safe(get_plot_html())})
