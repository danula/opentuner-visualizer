import csv
import os
import zlib
import pickle

import constants
import opentuner
import sqlite3 as lite

from opentuner.resultsdb.connect import connect


def unpickle_data(data):
    try:
        data = zlib.decompress(data)
    except:
        pass
    return pickle.loads(data)


engine = None
Session = None


def get_db_session():
    global engine, Session
    if engine is None:
        engine, Session = connect("sqlite:///" + constants.database_url)
        Session = Session()
    return engine, Session


def get_zero_to_one_values(data):
    """
    :param data: list of (configuration, configuration_id)
    :return: list of (configuration with values in range 0-1, configuration_id
    """
    with open(constants.manipulator_url, "r") as f1:
        manipulator = unpickle_data(f1.read())
        for p in manipulator.params:
            if p.is_primitive():
                for i in range(len(data)):
                    data[i][0][p.name] = p.get_unit_value(data[i][0])
                    # for d in data['conf_data']:
                    #    d[p.name] = p.get_unit_value(d)
            elif isinstance(p, opentuner.search.manipulator.EnumParameter):
                options = p.options
                for i in range(len(data)):
                    try:
                        data[i][0][p.name] = (options.index(p.get_value(data[i][0])) + 0.4999) / len(options)
                    except:
                        print("Invalid Configuration", p, p.name, data[i][0])
                        data[i][0][p.name] = 0
    return data


def generate_tuning_data(database_url, manipulator_url, project_name, analysis_name):
    with lite.connect(database_url) as con:
        cur = con.cursor()
        cur.execute(
                "SELECT configuration.data as conf_data, result.time" +
                " FROM configuration" +
                " JOIN result ON configuration.id =  result.configuration_id" +
                " WHERE result.state='OK'"
        )
    rows = cur.fetchall()
    data = [0] * len(rows)
    i = 0
    for d in rows:
        a = unpickle_data(d[0])
        a["time"] = d[1]
        data[i] = a
        i += 1

    with open(manipulator_url, "r") as f1:
        manipulator = unpickle_data(f1.read())
        for p in manipulator.params:
            if isinstance(p, opentuner.search.manipulator.EnumParameter):
                options = p.options
                for i in range(len(data)):
                    try:
                        data[i][p.name] = options.index(p.get_value(data[i]))
                    except:
                        pass

        location = os.path.join('tuning_data', project_name, analysis_name)
        if not os.path.exists(location):
            os.makedirs(location)
        with open(os.path.join(location, 'data_frame.csv'), 'wb') as f:
            w = csv.DictWriter(f, data[0].keys())
            w.writeheader()
            for d in data:
                w.writerow(d)
    return os.path.join(location, 'data_frame.csv')


def save_file(f, location):
    try:
        if not os.path.exists(location):
            os.makedirs(location)
        with open(os.path.join(location, f.name), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        return os.path.join(location, f.name)
    except EnvironmentError:
        return None
