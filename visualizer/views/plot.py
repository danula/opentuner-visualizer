import json
import sqlite3 as lite
from collections import OrderedDict
from copy import deepcopy

import numpy as np
import opentuner
import pandas as pd
from bokeh.embed import autoload_server
from bokeh.models import HoverTool, Callback
from bokeh.plotting import *
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

import constants
from visualizer.utils import unpickle_data, get_zero_to_one_values


def get_color_numeric(val, parameter):
    t = parameter.get_unit_value(val) * 255
    return "#%02x%02x%02x" % (t, 255 - t, 0)


def get_color_enum(val, parameter):
    t = 255 * (parameter.options.index(parameter.get_value(val)) + 0.4999) / len(parameter.options)
    print(t)
    return "#%02x%02x%02x" % (t, 255 - t, 0)


def get_data():
    global highlighted_flags
    print(constants.database_url)
    with lite.connect(constants.database_url, detect_types=lite.PARSE_COLNAMES) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT result_id, generation, result.configuration_id as conf_id, time,requestor,was_new_best, "
            + " collection_date as 'ts [timestamp]', configuration.data as conf_data"
            + " FROM result "
            + " JOIN desired_result ON desired_result.result_id = result.id  "
            + " JOIN configuration ON configuration.id =  result.configuration_id  "
            + " WHERE result.state='OK' AND time < 1000000 "
            # Add this line for JVM
            # + " AND result.tuning_run_id=3"
            + " ORDER BY collection_date"
        )
        rows = cur.fetchall()

    cols = ["result_id", "generation", "conf_id", "time", "requestor", "was_new_best", "timestamp", "conf_data"]
    data = pd.DataFrame(rows, columns=cols)[["result_id", "time", "was_new_best", "timestamp", "conf_id", "conf_data"]]

    grouped = data.groupby('was_new_best')

    if highlighted_flags is None:
        colors = ["red" if (val == 1) else "blue" for val in data['was_new_best'].values]
    else:
        configurations = [unpickle_data(val) for val in data['conf_data'].values]
        values = [0 for val in configurations]
        #for uniform colour
        # values2 = [0 for val in configurations]
        parameter_count = 0
        for parameter in manipulator.params:
            if parameter.name in highlighted_flags:
                if parameter.is_primitive():
                    values_temp = [parameter.get_unit_value(config) for config in configurations]
                    # values_temp2 = [parameter.get_unit_value(config) for config in configurations]
                elif isinstance(parameter, opentuner.search.manipulator.EnumParameter):
                    values_temp = [(parameter.options.index(parameter.get_value(val)) + 0.4999) / len(parameter.options) for val in configurations]
                    # values_temp = [ parameter.options.index(parameter.get_value(val)) for val in configurations]
                else:
                    continue
                parameter_count = parameter_count + 1
                if highlighted_flags[parameter.name] == "ON":
                    values = [values[i]+values_temp[i] for i in range(len(values))]
                elif highlighted_flags[parameter.name] == "OFF":
                    values = [values[i]+1-values_temp[i] for i in range(len(values))]
        print(parameter_count)
        if parameter_count == 0:
            colors = ["red" if (val == 1) else "blue" for val in data['was_new_best'].values]
        else:
            colors = ["#%02x%02x%02x" % (t*255/parameter_count, 255 - 255*t/parameter_count, 0) for t in values]
            # colors = ["#%02x%02x%02x" % (t, t, t) for t in values2]

    return data, grouped.get_group(1), colors


initialized = False


def timestamp(data):
    return (data - data[0]) / 1000000000


def initialize_plot():
    global p, source, source_best, initialized, cur_session, highlighted_flags, manipulator
    with open(constants.manipulator_url, "r") as f1:
        manipulator = unpickle_data(f1.read())
        print(manipulator)
    highlighted_flags = None
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
        tools=TOOLS,
        logo=None,
        border_fill="whitesmoke",
        x_axis_label='OpenTuner Running Time (Sec)',
        y_axis_label='Execution Time (Sec)'
    )
    p.xaxis.axis_label_text_font_size = "10pt"
    p.xaxis.axis_label_text_font = "roboto condensed"
    p.yaxis.axis_label_text_font_size = "10pt"
    p.yaxis.axis_label_text_font = "roboto condensed"

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

    source.callback = callback

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
        ("Configuration ID", "@conf_id"),
        ("Timestamp", "@x"),
        ("Time", "@y")
    ])
    push()
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


def index(request, project):
    global initialized
    if not initialized:
        initialize_plot()
    else:
        update_plot()
    # for analysis in project.analysis_set.all:
    #     print(analysis.name)
    return render(request, 'plot.html', {'script_js': mark_safe(get_plot_html()), 'project': project})


def update(request):
    update_plot()
    return HttpResponse("success")


def get_flags(request):
    with lite.connect(constants.database_url) as con:
        cur = con.cursor()
    cur.execute(
        "SELECT configuration.data as conf_data"
        + " FROM configuration"
        + " WHERE configuration.id =1"
    )
    rows = cur.fetchall()
    data = [(unpickle_data(d[0])) for d in rows]

    flags = []
    for key in data[0]:
        flags.append({'value': key, 'label': key, 'status': 1})

    return HttpResponse(json.dumps(flags), content_type="application/json")


def highlight_flag(request):
    global highlighted_flags
    if request.GET.get('flags', '') == "":
        highlighted_flags = None
    else:
        highlighted_flags = dict(zip(request.GET.get('flags', '').split(","), request.GET.get('status', '').split(",")))
    print(highlighted_flags)
    update_plot()
    return HttpResponse("success")


def config2(request, points_id):
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
        flags = []
        table_data = []
        for key in data[0][0]:
            record = {'name': key}
            flags.append({'value': key, 'label': key, 'status': 1})
            equal = True
            value = data[0][0][key]
            values = {}
            max = 0
            for i in range(len(data)):
                if (len(data) < 5):
                    record[str(data[i][1])] = data[i][0][key]

                if (data[i][0][key] not in values):
                    values[data[i][0][key]] = 1
                else:
                    values[data[i][0][key]] = values[data[i][0][key]] + 1

                if values[data[i][0][key]] > max:
                    max = values[data[i][0][key]]

                # if value == 'default':
                # value = data[i][0][key]
                # if equal and (data[i][0][key] != 'default') and (data[i][0][key] != data[0][0][key]):
                if equal and (data[i][0][key] != value):
                    equal = False

            record['max_count'] = max
            record['equal'] = equal
            record['value'] = str(values)
            # if equal:
            # record['value'] = value
            # else:
            # record['value'] = 'Unequal'
            table_data.append(record)

        def cmp_items(a, b):
            if a['max_count'] > b['max_count']:
                return -1
            elif a['max_count'] < b['max_count']:
                return 1
            else:
                return -1 if a['name'] < b['name'] else 1

        table_data.sort(cmp_items)
        if (len(data) < 5):
            columns = [str(data[i][1]) for i in range(len(rows))]
        else:
            columns = ['Value']
        response_data = {'data': table_data, 'columns': ['Name'] + columns, 'flags': flags}
        print(flags)

    return HttpResponse(json.dumps(response_data), content_type="application/json")

def config3(request, points_id1,points_id2):
    with lite.connect(constants.database_url) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT configuration.data as conf_data, configuration.id"
            + " FROM configuration"
            + " WHERE configuration.id in (%s)" % points_id1
        )
        rows1 = cur.fetchall()
        data1 = [(unpickle_data(d[0]), d[1]) for d in rows1]
        cur.execute(
            "SELECT configuration.data as conf_data, configuration.id"
            + " FROM configuration"
            + " WHERE configuration.id in (%s)" % points_id2
        )
        rows2 = cur.fetchall()
        data2 = [(unpickle_data(d[0]), d[1]) for d in rows2]

        data12 = get_zero_to_one_values(deepcopy(data1))
        data22 = get_zero_to_one_values(deepcopy(data2))

        table_data = []
        for key in data1[0][0]:
            record = {'name': key}
            data13 = []
            data23 = []
            values1 = {}
            values2 = {}
            for i in range(len(data1)):
                if data1[i][0][key] == 'off':
                    data13.append(1)
                elif data1[i][0][key] == 'on':
                    data13.append(0)
                else:
                    data13.append(data12[i][0][key])

                if data1[i][0][key] not in values1:
                    values1[data1[i][0][key]] = 1
                else:
                    values1[data1[i][0][key]] += 1

            for i in range(len(data2)):
                if data2[i][0][key] == 'off':
                    data23.append(1)
                elif data2[i][0][key] == 'on':
                    data23.append(0)
                else:
                    data23.append(data22[i][0][key])

                if data2[i][0][key] not in values2:
                    values2[data2[i][0][key]] = 1
                else:
                    values2[data2[i][0][key]] += 1

            a = np.array(data13)
            record['stdev1'] = np.std(a)
            b = np.array(data23)
            record['stdev2'] = np.std(b)
            record['meandiff'] = abs(np.mean(a)-np.mean(b))
            record['first'] = str(values1)
            record['second'] = str(values2)
            table_data.append(record)

        def cmp_items(a, b):
            if a['stdev1'] > b['stdev1']:
                return 1
            elif a['stdev1'] < b['stdev1']:
                return -1
            elif a['stdev2'] > b['stdev2']:
                return 1
            elif a['stdev2'] < b['stdev2']:
                return -1
            elif a['meandiff'] < b['meandiff']:
                return 1
            elif a['meandiff'] > b['meandiff']:
                return -1

            else:
                return -1 if a['name'] < b['name'] else 1

        table_data.sort(cmp_items)
        columns = ['First', 'Second']
        response_data = {'data': table_data, 'columns': ['Name'] + columns}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


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
        data2 = get_zero_to_one_values(deepcopy(data))

        for key in data[0][0]:
            record = {'name': key}
            equal = True
            value = data[0][0][key]
            values = {}
            data1 = []
            max = 0
            for i in range(len(data)):
                if (len(data) < 5):
                    record[str(data[i][1])] = data[i][0][key]

                if data[i][0][key] == 'off':
                    data1.append(1)
                elif data[i][0][key] == 'on':
                    data1.append(0)
                else:
                    data1.append(data2[i][0][key])

                if (data[i][0][key] not in values):
                    values[data[i][0][key]] = 1
                else:
                    values[data[i][0][key]] = values[data[i][0][key]] + 1

                if values[data[i][0][key]] > max:
                    max = values[data[i][0][key]]

                # if value == 'default':
                #    value = data[i][0][key]
                #if equal and (data[i][0][key] != 'default') and (data[i][0][key] != data[0][0][key]):
                if equal and (data[i][0][key] != value):
                    equal = False

            record['max_count'] = max
            record['equal'] = equal
            record['value'] = str(values)

            a = np.array(data1)
            record['stdev'] = np.std(a)
            table_data.append(record)

        def cmp_items(a, b):
            if a['stdev'] > b['stdev']:
                return 1
            elif a['stdev'] < b['stdev']:
                return -1
            else:
                return -1 if a['name'] < b['name'] else 1

        table_data.sort(cmp_items)
        if (len(data) < 5):
            columns = [str(data[i][1]) for i in range(len(rows))]
        else:
            columns = ['Value']
        response_data = {'data': table_data, 'columns': ['Name'] + columns}

    return HttpResponse(json.dumps(response_data), content_type="application/json")

