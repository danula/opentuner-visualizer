import os
#database_url = "/home/isuru/Desktop/Dacapo_Tuned_DataCollection/10.8.106.242/ubuntu4.db"
# database_url = "/home/kasun/projects/sample/db/madawa-notebook.db"
# manipulator_url = os.path.join(os.path.join(os.path.dirname(database_url), os.pardir), "params")

import json
from visualizer import utils

def save_config(db, manipulator):
    with open("constants.json", "w") as f:
        j = {'database' : db, 'manipulator' :manipulator}
        f.write(json.dumps(j))


def load_config():
    with open("constants.json", "r") as f:
        return json.loads(f.read())

def get_database_url():
    return load_config()['database']

def get_manipulator():
    with open(load_config()['manipulator'], "r") as f1:
        return utils.unpickle_data(f1.read())