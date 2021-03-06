import sqlite3

from utils.log import get_logger
from datetime import datetime
import time

logger = get_logger('ExperimentData')
META_DATA_TABLE = 'experiment_meta_data'
TYPE_COL = 'type'
ID_COL = 'id'
DATE_COL = 'date'
PROCESSING_DATE = 'process_date'
INSERT_METADATA = 'INSERT INTO {} ({},{}) values (?,?)'.format(META_DATA_TABLE, TYPE_COL, DATE_COL)
RAW_EEG_TABLE = 'raw_eeg'
EEG_TYPE_COL = 'eeg_type'
SERVER_TIMESTAMP_COL = 'server_timestamp'
DEVICE_TIMESTAMP_COL = 'device_timestamp'
TRIAL_ID_COL = 'trial_id'
TP9 = 'tp9'
AF7 = 'af7'
AF8 = 'af8'
TP10 = 'tp10'
AUXR = 'auxr'

WAVE_EEG_TABLE = 'eeg_waves'
CUES_TABLE = 'cues_tables'
CUE_NAME_COL = 'cue_name'


def adapt_datetime(ts):
    return time.mktime(ts.timetuple())


def insert_raw_data(conn, ex_id, raw_eeg):
    INSERT_STM = '''INSERT INTO {} ({},{},{},{},{},{},{},{}) values (?,?,?,?,?,?,?,?)'''.format(
        RAW_EEG_TABLE, TRIAL_ID_COL, SERVER_TIMESTAMP_COL, DEVICE_TIMESTAMP_COL,
        TP9, AF7, AF8, TP10, AUXR)

    c = conn.cursor()
    err_count = 0
    for index, line in enumerate(raw_eeg):
        try:
            server_timestamp = line[0].server_timestamp
            device_timestamp = line[0].timetag_ntp
            e1 = line[1][0]
            e2 = line[1][1]
            e3 = line[1][2]
            e4 = line[1][3]
            e5 = line[1][4]
            c.execute(INSERT_STM, (ex_id, server_timestamp, device_timestamp, e1, e2, e3, e4, e5))
        except Exception as e:
            logger.error(
                'failed to parse line:' + str(line) + " at index:" + str(index) + " with message:" + e.message)
            err_count += 1
            continue

    conn.commit()


def insert_by_wave_type(conn, eeg_data, wave_type, ex_id):
    c = conn.cursor()
    err_count = 0
    INSERT_STM = '''INSERT INTO {} ({},{},{},{},{},{},{},{}) values (?,?,?,?,?,?,?,?)'''.format(
        WAVE_EEG_TABLE, TRIAL_ID_COL, SERVER_TIMESTAMP_COL, DEVICE_TIMESTAMP_COL, TYPE_COL,
        TP9, AF7, AF8, TP10)
    for index, line in enumerate(eeg_data.wave_data[wave_type]):
        try:
            server_timestamp = line[0].server_timestamp
            device_timestamp = line[0].timetag_ntp
            device_raw = datetime.utcfromtimestamp(float(line[0].raw_ntp_timestamp) / 1000)
            server_raw = datetime.utcfromtimestamp(float(line[0].raw_server_timestamp) / 1000)
            e1 = line[1][0]
            e2 = line[1][1]
            e3 = line[1][2]
            e4 = line[1][3]
            c.execute(INSERT_STM, (ex_id, server_raw, device_raw, wave_type, e1, e2, e3, e4))
        except Exception as e:
            logger.error(
                'failed to insert line:' + str(line) + " at index:" + str(index) + " with message:" + e.message)
            err_count += 1
            continue


def insert_cues(conn, cues, ex_id):
    c = conn.cursor()
    INSERT_STM = '''INSERT INTO {} ({},{},{}) values (?,?,?)'''.format(
        CUES_TABLE, TRIAL_ID_COL, SERVER_TIMESTAMP_COL, CUE_NAME_COL)
    for cue in cues:
        c.execute(INSERT_STM, (ex_id, datetime.utcfromtimestamp(long(cue[0]) / 1000.0), cue[1]))
    conn.commit()


def get_connection():
    # in memory
    # return sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    return sqlite3.connect('exdb.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)


def test():
    conn = get_connection()
    c = conn.cursor()
    for row in c.execute("select * from " + RAW_EEG_TABLE):
        print row


class ExperimentData:
    def __init__(self):
        conn = get_connection()
        c = conn.cursor()
        # id is auto incremented: http://sqlite.org/autoinc.html
        meta_data_table = '''CREATE TABLE IF NOT EXISTS {}
            ({} integer primary key, {} string, {} timestamp, {} timestamp DEFAULT CURRENT_TIMESTAMP)'''.format(
            META_DATA_TABLE, ID_COL, TYPE_COL, DATE_COL, PROCESSING_DATE)

        raw_eeg_table = '''CREATE TABLE IF NOT EXISTS {}
            ({} integer primary key, {} integer, {} timestamp, {} timestamp,
             {} double, {} double, {} double, {} double, {} double)'''.format(
            RAW_EEG_TABLE, ID_COL, TRIAL_ID_COL, SERVER_TIMESTAMP_COL, DEVICE_TIMESTAMP_COL,
            TP9, AF7, AF8, TP10,AUXR)

        wave_table = '''CREATE TABLE IF NOT EXISTS {}
            ({} integer primary key, {} integer, {} timestamp, {} timestamp, {} string,
            {} double, {} double, {} double, {} double)'''.format(
            WAVE_EEG_TABLE, ID_COL, TRIAL_ID_COL, SERVER_TIMESTAMP_COL, DEVICE_TIMESTAMP_COL, TYPE_COL,
            TP9, AF7, AF8, TP10)

        cues_table = '''CREATE TABLE IF NOT EXISTS {}
            ({} integer primary key, {} integer, {} timestamp, {} string)'''.format(
            CUES_TABLE, ID_COL, TRIAL_ID_COL, SERVER_TIMESTAMP_COL, CUE_NAME_COL)

        logger.info("create table:" + meta_data_table)
        logger.info("create table:" + raw_eeg_table)
        logger.info("create table:" + wave_table)
        logger.info("create table:" + cues_table)

        c.execute(meta_data_table)
        c.execute(raw_eeg_table)
        c.execute(wave_table)
        c.execute(cues_table)

        conn.commit()
        conn.close()

    def insert(self, input_parser):
        conn = get_connection()
        c = conn.cursor()
        ex_id = createNewExperiment(c, conn, input_parser)

        insert_raw_data(conn, ex_id, input_parser.eeg_data.raw_eeg)

        for key in input_parser.eeg_data.wave_data.keys():
            logger.info("inserting key:" + key)
            insert_by_wave_type(conn, input_parser.eeg_data, key, ex_id)

        insert_cues(conn, input_parser.cues, ex_id)
        conn.close()
        return ex_id


def createNewExperiment(c, conn, input_parser):
    experiment_type = input_parser.type
    date = "20" + input_parser.date + " " + input_parser.time.replace('-', ':') + ":00"
    logger.info("creating new experiment id with time " + str(date))
    c.execute(INSERT_METADATA, (experiment_type, date))
    conn.commit()
    ex_id = c.execute("select * from experiment_meta_data where date =? and type = ? order by id desc",
                      (date, experiment_type,)).fetchone()[0]

    logger.info("got exeprimed id:" + str(ex_id))
    return ex_id
