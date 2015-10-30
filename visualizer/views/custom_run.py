__author__ = 'kasun'

from datetime import datetime

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import desc, create_engine
from sqlalchemy.ext.declarative import declarative_base

from opentuner.resultsdb.models import _Meta, Base, Configuration, DesiredResult, TuningRun
from plot import unpickle_data
import constants

DB_VERSION = "0.0"


def connect(dbstr):
    engine = create_engine(dbstr, echo=False)
    connection = engine.connect()

    # handle case that the db was initialized before a version table existed yet
    if engine.dialect.has_table(connection, "program"):
        # if there are existing tables
        if not engine.dialect.has_table(connection, "_meta"):
            # if no version table, assume outdated db version and error
            connection.close()
            raise Exception("Your opentuner database is currently out of date. Save a back up and reinitialize")

    # else if we have the table already, make sure version matches
    if engine.dialect.has_table(connection, "_meta"):
        Session = scoped_session(sessionmaker(autocommit=False,
                                              autoflush=False,
                                              bind=engine))
    version = _Meta.get_version(Session)
    if not DB_VERSION == version:
        raise Exception(
            'Your opentuner database version {} is out of date with the current version {}'.format(version, DB_VERSION))

    declarative_base(cls=Base).metadata.create_all(engine)

    Session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))
    # mark database with current version
    _Meta.add_version(Session, DB_VERSION)
    Session.commit()

    return engine, Session, connection


def custom_run(data, isNewTuningRun):
    engine, Session = connect("sqlite:///" + constants.database_url)
    Session = Session()
    # conn.execute("PRAGMA busy_timeout = 300000")

    tuning_run_id = Session.query(TuningRun).order_by(desc(TuningRun.id)).first().id
    if isNewTuningRun:
        tuning_run_id = tuning_run_id + 1

    result = Session.query(Configuration)
    with open(constants.manipulator_url, "r") as f1:
        manipulator = unpickle_data(f1.read())

    cfg_old = result.order_by(desc(Configuration.id)).first()


    # data = cfg_old.data.copy()
    #
    # data['-faggressive-loop-optimizations'] = 'off'
    # data['-falign-functions'] = 'on'
    # data['-falign-jumps'] = 'on'
    # data['-funsafe-math-optimizations'] = 'off'
    # data['-falign-labels'] = 'off'
    # data['-falign-loops'] = 'off'
    # data['-fasynchronous-unwind-tables'] = 'off'
    # data['-fbranch-count-reg'] = 'off'

    hashv = manipulator.hash_config(data)

    cfg = Configuration.get(Session, cfg_old.program, hashv, data)

    dr = DesiredResult(configuration=cfg, requestor='visualizer', generation=0, request_date=datetime.now(),
                       tuning_run_id=tuning_run_id, state="REQUESTED")
    Session.add(dr)
    Session.commit()