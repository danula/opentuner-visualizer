from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
import pickle
import zlib
import sqlite3 as lite
from collections import OrderedDict
from django.http import HttpResponse

import pandas as pd
import numpy as np
from sklearn import manifold
from sklearn.metrics import euclidean_distances
from sklearn.decomposition import PCA
from bokeh.plotting import *
from bokeh.embed import autoload_server
from bokeh.models import HoverTool, ColumnDataSource, Callback

import constants
import opentuner


def unpickle_data(data):
    try:
        data = zlib.decompress(data)
    except:
        pass
    return pickle.loads(data)


def get_data():
    global highlighted_flags

    with lite.connect(constants.database_url, detect_types=lite.PARSE_COLNAMES) as con:
        cur = con.cursor()
        cur.execute(
            "SELECT result_id, generation, result.configuration_id as conf_id,time,requestor,was_new_best, "
            + " collection_date as 'ts [timestamp]', configuration.data as conf_data "
            + " FROM result "
            + " JOIN desired_result ON desired_result.result_id = result.id  "
            + " JOIN configuration ON configuration.id =  result.configuration_id  "
            + " WHERE result.state='OK' AND time < 1000000 "
            # Add this line for JVM
            + " AND result.tuning_run_id=3 "
            + " ORDER BY collection_date"
        )
        rows = cur.fetchall()

    cols = ["result_id", "generation", "conf_id", "time", "requestor", "was_new_best", "timestamp", "conf_data"]
    data = pd.DataFrame(rows, columns=cols)[["result_id", "time", "was_new_best", "timestamp", "conf_id", "conf_data"]]
    for i, val in enumerate(data['conf_data']):
        data['conf_data'][i] = unpickle_data(val)
    grouped = data.groupby('was_new_best')
    print("**************************")
    print(highlighted_flags)
    print("**************************!!!!!!!!!!!!")
    if highlighted_flags is None:
        def to_int(x):
            try:
                return int(max(0, min(255, x)))
            except OverflowError:
                return 255

        # colors = ["red" if (val == 1) else "blue" for val in data['was_new_best'].values]
        x = data['time']
        print(x)
        colors = ["#%02x%02x%02x" % (255 - to_int(r), to_int(r), 0) for r in np.floor(256*(x-x.min())/(x.max()/2-x.min()))]
        print(colors)
    else:
        configurations = [unpickle_data(val) for val in data['conf_data'].values]
        values = [0 for val in configurations]
        parameter_count = 0
        for parameter in manipulator.params:
            if parameter.name in highlighted_flags:
                if parameter.is_primitive():
                    values_temp = [parameter.get_unit_value(config) for config in configurations]
                elif isinstance(parameter, opentuner.search.manipulator.EnumParameter):
                    values_temp = [(parameter.options.index(parameter.get_value(val)) + 0.4999) / len(parameter.options) for val in configurations]
                else:
                    continue
                parameter_count = parameter_count + 1
                if (highlighted_flags[parameter.name] == "1"):
                    values = [values[i]+values_temp[i] for i in range(len(values))]
                else:
                    values = [values[i]+1-values_temp[i] for i in range(len(values))]
        print(parameter_count)
        if parameter_count == 0:
            def to_int(x):
                try:
                    return int(max(0, min(255, x)))
                except OverflowError:
                    return 255

            # colors = ["red" if (val == 1) else "blue" for val in data['was_new_best'].values]
            x = data['time']
            print(x)
            colors = ["#%02x%02x%02x" % (255 - to_int(r), to_int(r), 0) for r in np.floor(256*(x-x.min())/(x.max()/2-x.min()))]
            print(colors)
        else:
            colors = ["#%02x%02x%02x" % (t*255/parameter_count, 255 - 255*t/parameter_count, 0) for t in values]


    # def to_int(x):
    #     try:
    #         return int(max(0, min(255, x)))
    #     except OverflowError:
    #         return 255
    #
    # # colors = ["red" if (val == 1) else "blue" for val in data['was_new_best'].values]
    # x = data['time']
    # print(x)
    # colors = ["#%02x%02x%02x" % (255 - to_int(r), to_int(r), 0) for r in np.floor(256*(x-x.min())/(x.max()/2-x.min()))]
    # print(colors)
    return data, grouped.get_group(1), colors


def get_configs(data):
    with open(constants.manipulator_url, "r") as f1:
        manipulator = unpickle_data(f1.read())
        for p in manipulator.params:
            if p.is_primitive():
                for d in data['conf_data']:
                    # d[p.name] = p.get_unit_value(d)
                    d[p.name] = p.get_value(d)
            elif isinstance(p, opentuner.search.manipulator.EnumParameter):
                options = p.options
                for d in data['conf_data']:
                    try:
                        # d[p.name] = (options.index(p.get_value(d)) + 0.4999) / len(options)
                        d[p.name] = options.index(p.get_value(d))
                    except:
                        print("Invalid Configuration", p, p.name, d)
                        d[p.name] = 0

    dims = data['conf_data'][0].__len__()
    print data.__len__()
    keys = data['conf_data'][0].keys()
    confs = np.ndarray(shape=(data.__len__(), dims), dtype=float)
    col = []
    for p, d in enumerate(data['conf_data']):
        if data['time'][p] > 0.175:
            col.append('g')
        else:
            col.append('r')
        for j, k in enumerate(keys):
            confs[p][j] = d[k]

    data2 = data[["result_id", "time"]]
    data_frame = pd.DataFrame(columns=keys, data=confs)
    data_frame = pd.concat([data2, data_frame], axis=1)
    data_frame.to_csv("data_frame.csv")

    return data, dims, confs, col


def mds(dims, confs):
    seed = np.random.RandomState(seed=dims)

    X_true = confs
    # Center the data
    X_true -= X_true.mean()

    similarities = euclidean_distances(X_true)

    print "##########"

    # Add noise to the similarities

    mds = manifold.MDS(n_components=2, max_iter=3000, eps=1e-9, random_state=seed, dissimilarity="precomputed",
                       n_jobs=-1)
    pos = mds.fit(similarities).embedding_

    # nmds = manifold.MDS(n_components=2, metric=False, max_iter=3000, eps=1e-12,dissimilarity="precomputed", random_state=seed, n_jobs=1,n_init=1)
    # npos = nmds.fit_transform(similarities, init=pos)



    print "##########"
    # Rescale the data
    pos *= np.sqrt((X_true ** 2).sum()) / np.sqrt((pos ** 2).sum())

    # Rotate the data
    clf = PCA(n_components=2)
    #X_true = clf.fit_transform(X_true)

    pos = clf.fit_transform(pos)

    return pos


def isomap(dims, confs):
    seed = np.random.RandomState(seed=dims)

    X_true = confs
    # Center the data
    X_true -= X_true.mean()

    similarities = euclidean_distances(X_true)

    print "##########"

    # Add noise to the similarities

    imap = manifold.Isomap(n_components=2, max_iter=3000)
    pos = imap.fit(X_true).embedding_

    # nmds = manifold.MDS(n_components=2, metric=False, max_iter=3000, eps=1e-12,dissimilarity="precomputed", random_state=seed, n_jobs=1,n_init=1)
    # npos = nmds.fit_transform(similarities, init=pos)


    print "##########"
    # Rescale the data
    pos *= np.sqrt((X_true ** 2).sum()) / np.sqrt((pos ** 2).sum())

    # Rotate the data
    clf = PCA(n_components=2)
    # X_true = clf.fit_transform(X_true)

    pos = clf.fit_transform(pos)

    return pos


def tsne(dims, confs):
    seed = np.random.RandomState(seed=dims)

    X_true = confs
    # Center the data
    X_true -= X_true.mean()

    similarities = euclidean_distances(X_true)

    print "##########"

    # Add noise to the similarities

    imap = manifold.TSNE(n_components=2, random_state=seed, metric="precomputed")
    pos = imap.fit_transform(similarities)

    # nmds = manifold.MDS(n_components=2, metric=False, max_iter=3000, eps=1e-12,dissimilarity="precomputed", random_state=seed, n_jobs=1,n_init=1)
    # npos = nmds.fit_transform(similarities, init=pos)


    print "##########"
    # Rescale the data
    pos *= np.sqrt((X_true ** 2).sum()) / np.sqrt((pos ** 2).sum())

    # Rotate the data
    clf = PCA(n_components=2)
    #X_true = clf.fit_transform(X_true)

    pos = clf.fit_transform(pos)

    return pos


initialized = False


def timestamp(data):
    return (data - data[0]) / 1000000000

def initialize_plot():
    global p, source, source_best, initialized, cur_session, manipulator, highlighted_flags
    with open(constants.manipulator_url, "r") as f1:
        manipulator = unpickle_data(f1.read())
        print(manipulator)
    highlighted_flags = None
    initialized = True
    data, best_data, colors = get_data()
    data, dims, confs, col = get_configs(data)
    # data.to_csv("data.csv")
    # np.savetxt("confs.csv", confs, delimiter=",")
    pos = mds(dims, confs)
    # pos = isomap(dims, confs)
    # pos = tsne(dims, confs)


    source = ColumnDataSource(data=dict(
        x=timestamp(data['timestamp']),
        y=data['time'],
        x1=pos[:, 0],
        y1=pos[:, 1],
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
        x_axis_label='x axis', y_axis_label='y axis'
    )

    p.circle('x1', 'y1', conf_id='conf_id', fill_color='fill_color', line_color=None, source=source, size=5)
    # p.line('x', 'y', conf_id='conf_id', line_color="red", source=source_best, size=5)

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

def highlight_flag(request):
    global highlighted_flags
    if request.GET.get('flags', '') == "":
        highlighted_flags = None
    else:
        highlighted_flags = dict(zip(request.GET.get('flags', '').split(","), request.GET.get('status', '').split(",")))
    print(highlighted_flags)
    update_plot()
    return HttpResponse("success")

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

        table_data = []
        for key in data[0][0]:
            record = {'name': key}
            equal = True
            value = data[0][0][key]
            for i in range(len(data)):
                if len(data) < 5:
                    record[str(data[i][1])] = data[i][0][key]
                # if value == 'default':
                # value = data[i][0][key]
                # if equal and (data[i][0][key] != 'default') and (data[i][0][key] != data[0][0][key]):
                if equal and (data[i][0][key] != value):
                    equal = False

            record['equal'] = equal
            if len(data) >= 5:
                if equal:
                    record['value'] = value
                else:
                    record['value'] = 'Unequal'
            table_data.append(record)

        def cmp_items(a, b):
            if a['equal']:
                if b['equal']:
                    return -1 if a['name'] < b['name'] else 1
                return -1
            if b['equal']:
                return 1
            return -1 if a['name'] < b['name'] else 1

        table_data.sort(cmp_items)
        if len(data) < 5:
            columns = [str(data[i][1]) for i in range(len(rows))]
        else:
            columns = ['Value']
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
        for key in data[0][0]:
            record = {'name': key}
            value = data[0][0][key]
            for i in range(len(data)):
                if len(data) < 5:
                    record[str(data[i][1])] = data[i][0][key]
                # if value == 'default':
                # value = data[i][0][key]
                # if equal and (data[i][0][key] != 'default') and (data[i][0][key] != data[0][0][key]):
                if equal and (data[i][0][key] != value):
                    equal = False

            values = [4,6,8,2,3]
            record['stdev'] = np.std(values)

            table_data.append(record)

        def cmp_items(a, b):
            return -1 if a['stdev'] < b['stdev'] else 1

        table_data.sort(cmp_items)
        columns = ['Value']
        response_data = {'data': table_data, 'columns': ['Name'] + columns}

    return HttpResponse(json.dumps(response_data), content_type="application/json")

