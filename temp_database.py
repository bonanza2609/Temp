#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# 
# Embedded file name: ./temp_database.py

import sys
# import time
# import types
import datetime
from datetime import timedelta
import pytz
from influxdb import InfluxDBClient

# from influxdb import DataFrameClient

version = '1.3'


# -------------------------------------------------------------------------------------------


def db_connect(db_all, nodb, verbose_level):
    global db
    db_host = db_all[0]
    db_port = db_all[1]
    db_user = db_all[2]
    db_password = db_all[3]
    db_table = db_all[4]
    db_database = db_all[5]

    try:
        if (nodb):
            if verbose_level > 0:
                print("connect to host >", db_host, "< w/o database")
            db = InfluxDBClient(host=db_host, port=db_port, username=db_user, password=db_password)
        else:
            if verbose_level > 0:
                print("connect to host >", db_host, "< and database >", db_database, "<")
            db = InfluxDBClient(host=db_host, port=db_port, username=db_user, password=db_password,
                                database=db_database)

    except:
        print('PANIC - cannot connect to database')
        print('Error class:', sys.exc_info()[0])
        print('Error code :', sys.exc_info()[1])
        print('host       :', db_host)
        print('port       :', db_port)
        print('user       :', db_user)
        print('passwd     :', db_password)
        print('database   :', db_database)
        print('table      :', db_table)
        sys.exit(2)

    return ()


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


def create_database(db_all, verbose_level):
    db_database = db_all[1]
    db_table = db_all[0]
    db_host = db_all[2]
    db_user = db_all[3]
    db_password = db_all[4]
    db_port = db_all[5]

    try:

        db_connect(db_all, 1, verbose_level)  # öffne verbindung ohne datenbank

        # create database avrio ;
        # grant usage on *.* to root@localhost identified by ‘nxt2008’;    
        # grant all privileges on avrio.* to root@localhost ;
        print('CREATE DATABASE', db_database)
        var = input('Enter yes: ')
        if var == 'yes':
            stmt = 'CREATE DATABASE IF NOT EXISTS ' + db_database
            if verbose_level > 1:
                print(stmt)
            db.create_database(db_database)
            db.close()

    except:
        print('PANIC - cannot connect to database')
        print('Error class:', sys.exc_info()[0])
        print('Error code :', sys.exc_info()[1])
        print('host       :', db_host)
        print('port       :', db_port)
        print('user       :', db_user)
        print('passwd     :', db_password)
        print('database   :', db_database)
        print('table      :', db_table)
        sys.exit(2)

    return ()


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def write_database(read_items, sensordata, sensor_dict, db_all, verbose_level):
    json_body = []

    db_host = db_all[0]
    db_port = db_all[1]
    db_user = db_all[2]
    db_password = db_all[3]
    db_table = db_all[4]
    db_database = db_all[5]
    db_connect(db_all, 0, verbose_level)

    try:

        if verbose_level > 1:
            print("read_items: ", read_items)  # sensor_dict = dictionary -> sensor : location
        for x in range(0, read_items):  # sensordata = sensor , temp
            dataset = sensordata[x]  # wert aus sensor daten holen
            sen_loc = str(sensor_dict.get(dataset[0]))  # wert der location zuordnen
            if verbose_level > 1:
                print(dataset, '-> Sensor ID:', dataset[0], 'temp.: ', dataset[1], 'location:', sen_loc)
            if sen_loc == 'None':
                print('PANIC: unknown sensor ', dataset[0])
            elif x == 0:  # verarbeitet des ersten datensatzes
                json_body.append(
                    {
                        "measurement": db_table,
                        "fields": {
                            sen_loc: float(dataset[1])
                        }
                    })

            else:  # Verarbeiten der restlichen datensätze
                json_body.append(
                    {
                        "measurement": db_table,
                        "fields": {
                            sen_loc: float(dataset[1])
                        }
                    })

        print("0-script")
        if verbose_level > 1:
            print(json_body)

        db.write_points(json_body)
        db.close()

    except:
        print('PANIC - cannot connect to database')
        print('Error class:', sys.exc_info()[0])
        print('Error code :', sys.exc_info()[1])
        print('host       :', db_host)
        print('port       :', db_port)
        print('user       :', db_user)
        print('passwd     :', db_password)
        print('database   :', db_database)
        print('table      :', db_table)
        sys.exit(2)

    return ()


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


def read_records(db_lines, db_all, db_fields_all, verbose_level, db_fields):
    db_host = db_all[0]
    db_port = db_all[1]
    db_user = db_all[2]
    db_password = db_all[3]
    db_table = db_all[4]
    db_database = db_all[5]
    db_connect(db_all, 0, verbose_level)
    dbval = 0

    if verbose_level > 1:
        print("read_records")

    if verbose_level > 0:
        print("show last " + str(db_lines) + " record(s) from database")

    query_count = 'SELECT * FROM ' + db_table
    if verbose_level > 1:
        print("query_count:", query_count)

    results_count = db.query(query_count)  # holt altuelle anzahl an einträgen aus datenbank
    db.close()

    for x in results_count:  # umrechnung der totalen anzahl und der gewünschten anzahl
        count = list(x)
        total_count = len(count)
        if verbose_level > 1:
            print("count:", len(count))
            print("total_count:", total_count)

    db_offset = str(total_count - db_lines)
    if verbose_level > 1:
        print("db_offset:", db_offset)

    stmt = 'SELECT * FROM ' + db_table + ' LIMIT ' + str(db_lines) + ' OFFSET ' + db_offset
    if verbose_level > 1:
        print("stmt:", stmt)

    try:
        dbval = db.query(stmt)
        db.close()

    except:
        print('PANIC - cannot read from database table')
        print('Error class:', sys.exc_info()[0])
        print('Error code :', sys.exc_info()[1])
        print('host       :', db_host)
        print('port       :', db_port)
        print('user       :', db_user)
        print('passwd     :', db_password)
        print('database   :', db_database)
        print('table      :', db_table)
        sys.exit(2)

    if verbose_level > 1:
        print("dbval:", dbval)

    if dbval != 0:
        if verbose_level > 0:
            print('Datum                             , ' + db_fields_all)
            print(
                '----------------------------------------------------------------------------------------------------')

        if verbose_level > 1:
            print("db_lines: ", db_lines)
            print("db_fields: ", db_fields)
            print("db_fields_all: ", db_fields_all)

        for x in dbval:
            array = list(x)
            for x in range(0, db_lines):
                output = []
                dataset = list(array)[x]
                if verbose_level > 1:
                    print(x)
                    print(dataset)
                field_list = dataset.get("time")  # read timestamp
                output.append(field_list)  # put timestamp in to output
                if verbose_level > 1:
                    print("Field: time")
                    print("Field entry:", field_list)
                for y in range(len(db_fields)):
                    field = db_fields[y]
                    field_list = dataset.get(field)
                    output.append(field_list)
                    if verbose_level > 1:
                        print("Field:", field)
                        print("Field entry:", field_list)
                if verbose_level > 0:
                    print(output)

        return (dataset)
    else:
        print("no records retrieved from database")
        return 0


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


def clean_records(db_fields, db_all, db_fields_all, verbose_level):  # TODO function not work correctly
    print(db_all)

    db_host = db_all[0]
    db_port = db_all[1]
    db_user = db_all[2]
    db_password = db_all[3]
    db_table = db_all[4]
    db_database = db_all[5]
    db_connect(db_all, 0, verbose_level)
    dbval = 0
    dbval_2 = 0
    dbval_3 = 0

    date_time_str = ''
    date_time_zero_str = '1970-01-01 00:00:00.000'
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    date_format_2 = '%Y-%m-%dT%H:%M:%S.%fZ'
    local_timezone = "Europe/Berlin"

    time_range = 3

    print("Please enter the time of the data point in the 'YYYY-MM-DD hh:mm:ss.nnnnnnnn' format you want to delete")
    date_time_str = "2021-08-18 13:45:46.613377"  # input('Enter Time: ') # todo remove

    local = pytz.timezone(local_timezone)
    naive = datetime.datetime.strptime(date_time_str, date_format)
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    utc_dt_none = utc_dt.replace(tzinfo=None)  # remove timezone from datetime

    utc_dt_1 = utc_dt_none + timedelta(minutes=time_range)
    utc_dt_2 = utc_dt_none - timedelta(minutes=time_range)

    if verbose_level > 4:
        print('date_time_str', date_time_str)
        print('naive', naive)
        print('local', local)
        print('local_dt', local_dt)
        print('utc_dt', utc_dt)
        print('+', utc_dt_1)
        print('-', utc_dt_2)

    def time_to_stamp(utc_dt, date_time_zero_str, date_format, verbose_level):  # datetime to timestamp
        utc_zero = datetime.datetime.strptime(date_time_zero_str, date_format)  # transform datetime zero
        delta = utc_dt - utc_zero  # time delta

        if verbose_level > 3:
            print("date_time_zero_str", date_time_zero_str)
            print("utc_zero:", utc_zero)
            print("utc_dt", utc_dt)
            print("delta", delta)

        input_hour = utc_dt.hour
        input_minute = utc_dt.minute
        input_second = utc_dt.second
        input_microsecond = utc_dt.microsecond

        if verbose_level > 2:
            print("input_hour", input_hour)
            print("input_minute", input_minute)
            print("input_second", input_second)
            print("input_microsecond", input_microsecond)

        output_1 = float(input_microsecond) / 1000000000
        output_2 = (output_1 + float(input_second)) / 60
        output_3 = (output_2 + float(input_minute)) / 60
        output_4 = (output_3 + float(input_hour)) / 24
        output_5 = output_4 * 86400000000000  # /1000/100/100/100/60/60/24
        output_6 = delta.days * 86400000000000  # /1000/100/100/100/60/60/24
        output_7 = int(output_5) + int(output_6)

        if verbose_level > 3:
            print(float(output_1))
            print(float(output_2))
            print(float(output_3))
            print(float(output_4))
            print(int(output_5))
            print(int(output_6))
            print(int(output_7))

        return (int(output_7))

    def time_to_stamp_2(iso_time, date_time_zero_str, date_format, verbose_level):  # ist time to timestamp

        array_1 = iso_time.split('-')
        array_2 = array_1[2].split('T')
        array_3 = array_2[1].split(':')
        array_4 = array_3[2].split('.')
        array_5 = array_4[1].split('Z')
        array_6 = array_1[0] + '-' + array_1[1] + '-' + array_2[0] + ' ' + array_3[0] + ':' + array_3[1] + ':' + array_4[0] + '.000'

        array_count = len(array_5[0])

        if array_count < 9:
            dif = 9 - array_count
            add_dif = 1
            for x in range(0, dif):
                add_dif = add_dif * 10
            array_dif = int(array_5[0]) * add_dif
            if verbose_level > 3:
                print("differenc", dif)
                print("add_dif", add_dif)
        else:
            array_dif = array_5[0]

        if verbose_level > 3:
            print(array_count)
            print(array_dif)

        if verbose_level > 3:
            print(array_1[0])  # Year  
            print(array_1[1])  # Month
            print(array_2[0])  # Day
            print(array_3[0])  # Hour
            print(array_3[1])  # Minute
            print(array_4[0])  # Second
            print(array_dif)  # Microsecond
            print(array_6)  # datetime for delta.days

        utc_zero = datetime.datetime.strptime(date_time_zero_str, date_format)  # transform datetime zero
        iso_time_dt = datetime.datetime.strptime(array_6, date_format)
        delta = iso_time_dt - utc_zero  # time delta

        if verbose_level > 3:
            print("date_time_zero_str", date_time_zero_str)
            print("utc_zero:", utc_zero)
            print("iso_time_dt", iso_time_dt)
            print("delta", delta)

        input_hour = array_3[0]
        input_minute = array_3[1]
        input_second = array_4[0]
        input_microsecond = array_dif

        if verbose_level > 2:
            print("input_hour", input_hour)
            print("input_minute", input_minute)
            print("input_second", input_second)
            print("input_microsecond", input_microsecond)

        output_1 = float(input_microsecond) / 1000000000
        output_2 = (output_1 + float(input_second)) / 60
        output_3 = (output_2 + float(input_minute)) / 60
        output_4 = (output_3 + float(input_hour)) / 24
        output_5 = output_4 * 86400000000000  # /1000/100/100/100/60/60/24
        output_6 = delta.days * 86400000000000  # /1000/100/100/100/60/60/24
        output_7 = int(output_5) + int(output_6)

        if verbose_level > 3:
            print(float(output_1))
            print(float(output_2))
            print(float(output_3))
            print(float(output_4))
            print(int(output_5))
            print(int(output_6))
            print(int(output_7))

        return (int(output_7))

    def output_data(dbval):
        if dbval != 0:
            if verbose_level > 0:
                print('Datum UTC                         , ' + db_fields_all)
                print('----------------------------------------------------------------------------------------------------')

            for x in dbval:
                array = list(x)
                db_lines = len(array)

                if verbose_level > 1:
                    print("db_lines: ", db_lines)

                time_stamps = []

                for x in range(0, db_lines):
                    output = []
                    dataset = list(array)[x]
                    if verbose_level > 1:
                        print("x", x)
                        print("dataset", dataset)
                    output.append(x)
                    field_list = dataset.get("time")  # read timestamp
                    output.append(field_list)  # put timestamp in to output
                    time_list = dataset.get("time")
                    time_stamps.append(time_list)
                    if verbose_level > 1:
                        print("Field: time")
                        print("Field entry:", field_list)
                    for y in range(len(db_fields)):
                        field = db_fields[y]
                        field_list = dataset.get(field)
                        output.append(field_list)
                        if verbose_level > 1:
                            print("Field:", field)
                            print("Field entry:", field_list)
                    print(output)
            return (time_stamps)

    def db_interaction(stmt_x):

        if verbose_level > 2:
            print("stmt", stmt_x)

        try:
            dbval_x = db.query(stmt_x)
            db.close()

        except:
            print('PANIC - cannot read from database table')
            print('Error class:', sys.exc_info()[0])
            print('Error code :', sys.exc_info()[1])
            print('host       :', db_host)
            print('port       :', db_port)
            print('user       :', db_user)
            print('passwd     :', db_password)
            print('database   :', db_database)
            print('table      :', db_table)
            sys.exit(2)

        if verbose_level > 2:
            print("dbval:", dbval_x)

        return (dbval_x)

    timestamp_str_1 = str(time_to_stamp(utc_dt_1, date_time_zero_str, date_format, verbose_level))
    timestamp_str_2 = str(time_to_stamp(utc_dt_2, date_time_zero_str, date_format, verbose_level))

    if verbose_level > 1:
        print("timestamp_str_1[+]", timestamp_str_1)
        print("timestamp_str_2[-]", timestamp_str_2)

    stmt = 'SELECT * FROM ' + db_table + ' WHERE time <= ' + timestamp_str_1 + ' AND time >= ' + timestamp_str_2 + ' '

    dbval = db_interaction(stmt)

    if verbose_level > 1:
        print("dbval:", dbval)

    time_stamps = output_data(dbval)

    print("Please enter the position of the desired line")
    pos = int(input('Enter pos.: '))

    if verbose_level > 1:
        print("dbval_2:", dbval_2)
        print("time_stamps:", time_stamps)
        print("Position:", pos)
        print("time_stamp Pos.:", time_stamps[pos])

    output_time_1 = time_stamps[pos]
    timestamp_str_3 = str(time_to_stamp_2(output_time_1, date_time_zero_str, date_format, verbose_level))
    # todo timestamp_str_3 result wrong timestamp

    if verbose_level > 1:
        print("timestamp_str_3", timestamp_str_3)

    stmt_2 = 'SELECT * FROM ' + db_table + ' WHERE time = ' + timestamp_str_3 + '  '  # todo data string incorrect

    dbval_2 = db_interaction(stmt_2)

    if verbose_level > 1:
        print("dbval_2:", dbval_2)

    time_stamps_2 = output_data(dbval_2)  # todo database result empty wye ?
    timestamp_str_4 = str(time_to_stamp_2(time_stamps_2[0], date_time_zero_str, date_format, verbose_level))

    if verbose_level > 1:
        print("timestamp_str_4", timestamp_str_4)

    print('DELETE Timestamp ', time_stamps_2, 'FROM DATABASE', db_database, 'from', db_table, )
    var = input('Enter yes: ')
    if var == 'yes':
        var = input('Confirm drop Database Entries Enter yes: ')
        if var == 'yes':
            stmt_3 = 'DELETE FROM ' + db_table + ' WHERE TIME = ' + timestamp_str_4 + ' '
            if verbose_level > 1:
                print("stmt_3:", stmt_3)
            dbval_3 = db_interaction(stmt_3)
            print("OK done")
    else:
        print('request cancelled')
    sys.exit(0)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


def kill_dbentries(db_all, verbose_level):
    db_table = db_all[4]
    db_database = db_all[5]
    print('DELETE ALL ENTRIES FROM DATABASE', db_table, 'from', db_database, )
    var = input('Enter yes: ')
    if var == 'yes':
        var = input('Confirm drop Database Entries Enter yes: ')
        if var == 'yes':
            db_connect(db_all, 0, verbose_level)
            stmt = 'DELETE FROM ' + db_table + ' WHERE 1'
            if verbose_level > 1:
                print(stmt)
            db.drop_measurement(db_table)
            db.close()
    else:
        print('request cancelled')
    sys.exit(0)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


def version_db():
    v_db = str("version_db:" + str(version))
    return (v_db)


# -------------------------------------------------------------------------------------------
