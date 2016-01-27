import zlib
import pickle
import os
import json
import constants
import opentuner

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

def getZeroToOneValues(data):
    '''
    :param data: list of (configuration, configuration_id)
    :return: list of (configuration with values in range 0-1, configuration_id
    '''
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