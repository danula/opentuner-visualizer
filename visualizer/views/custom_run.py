__author__ = 'kasun'

from datetime import datetime

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import desc, create_engine
from sqlalchemy.ext.declarative import declarative_base

from opentuner.resultsdb.models import _Meta, Base, Configuration, DesiredResult, TuningRun
from opentuner.resultsdb.connect import connect
from plot import unpickle_data
import constants

DB_VERSION = "0.0"

def custom_run(data, is_new_tuning_run):
    engine, Session = connect("sqlite:///" + constants.database_url)
    Session = Session()
    # conn.execute("PRAGMA busy_timeout = 300000")

    tuning_run_id = Session.query(TuningRun).order_by(desc(TuningRun.id)).first().id
    if is_new_tuning_run:
        tuning_run_id = tuning_run_id + 1

    result = Session.query(Configuration)
    with open(constants.manipulator_url, "r") as f1:
        manipulator = unpickle_data(f1.read())

    cfg_old = result.order_by(desc(Configuration.id)).first()
    hashv = manipulator.hash_config(data)

    cfg = Configuration.get(Session, cfg_old.program, hashv, data)

    dr = DesiredResult(configuration=cfg, requestor='visualizer', generation=0, request_date=datetime.now(),
                       tuning_run_id=tuning_run_id, state="REQUESTED")
    Session.add(dr)
    Session.commit()