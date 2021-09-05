#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Read 1-Wire sensors and write into database
#

import os
import sys
import time
import argparse  # analyze command line arguments

import TempSet

config_file = 'temp-config.txt'
html_single_file = 'www/temp-single.html'
html_multi_file = 'www/temp-multi.html'

# define range for faulty sensor data

dead_hi = 80.0
dead_lo = -30.0
error_low = -100
error_high = 125

db_host = "localhost"               # host - local database
db_port = "8086"                    # port
db_user = "influxdb-user"           # username
db_password = "influxdb_password"   # password
db_table = "temp-dat"               # Table
db_database = "temp"                # database
db_r_host = "127.0.0.1"             # host - Remote Database / optional
db_r_port = "8086"                  # port
db_r_user = "influxdb-user"         # username
db_r_password = "influx_password"   # password
db_r_table = "Temp-dat"             # Table
db_r_database = "Temp"              # database

db_all = [db_host, db_port, db_user, db_password, db_table, db_database]
db_all_remote = [db_r_host, db_r_port, db_r_user, db_r_password, db_r_table, db_r_database]

temp_host = "localhost"             # host - local temp server
temp_port = "4304"                  # port
temp_r_host = "127.0.0.1"           # host - Remote temp server
temp_r_port = "4304"                # port

temp_all = [temp_host, temp_port]
temp_all_remote = [temp_r_host, temp_r_port]

remote_set = 0      # default: [0] use Normal Database and Temp Server
setup_level = 0     # default: [0] do not read config file
read_sens = 1       # default: [1] read sensors
database_level = 1  # default: [1] write to database
verbose_level = 1   # default: [1] show status messages

version = '1.7'


# -------------------------------------------------------------------------------------------


parser = argparse.ArgumentParser(description="Read 1-wire sensors and write to database")

# argument with argument from type int

parser.add_argument("-r", "--read", help="get the [READ] last entries from the database", type=int)

group1 = parser.add_mutually_exclusive_group()
group1.add_argument("-v", "--verbose", default=False,
                    dest='verbose', help="increase output verbosity", type=int)

group1.add_argument("-q", "--quiet", action='store_const', dest='quiet',
                    const='value-to-store', help="no output")

group1.add_argument("-d", "--debug", action='store_const', dest='debug',
                    const='value-to-store', help="show debug messages")

parser.add_argument("-n", "--nodb", action='store_const', dest='nodb',
                    const='value-to-store', help="execute read but do not write into database")

parser.add_argument("-w", "--html_single", action='store_const', dest='html_single',
                    const='value-to-store', help="create web page(html)with last entry")

parser.add_argument("-wm", "--html_multi", dest='html_multi', type=str,
                    help="create web page(html)with last entry from multiple configuration files")

parser.add_argument("-k", "--kill", action='store_const', dest='kill',
                    const='value-to-store', help="kill all entries in database", )

parser.add_argument("-g", "--get", action='store_const', dest='get',
                    const='value-to-store', help="get sensors and append to config.txt", )

parser.add_argument("-s", "--setup", action='store_const', dest='setup',
                    const='value-to-store', help="create config file", )

parser.add_argument("-b", "--backup", action='store_const', dest='remote',
                    const='value-to-store', help="use remote database", )

parser.add_argument("-c", "--createdb", action='store_const', dest='create',
                    const='value-to-store', help="create database", )

parser.add_argument("-x", "--xxx", action='store_const', dest='xxx',
                    const='value-to-store', help="clean DB entry select by Time", )

parser.add_argument('--version', action='store_const', dest='version',
                    const='value-to-store', help="Version over view")

parser.add_argument('--conf', dest='conf', help="set config file", type=str)

args = parser.parse_args()

if args.verbose:
    verbose_level = args.verbose
if args.quiet:
    verbose_level = 0
if args.debug:
    verbose_level = 2
if args.nodb:
    database_level = 0
if args.setup:
    setup_level = 1


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def version_main(v_main):  # todo check if possible tu use with class's
    print("version_main: ", v_main)
    # print(version_db())
    # print(version_html())

    sys.exit(0)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

now = time.strftime("%d.%m.%Y - %H:%M:%S Uhr")
path = os.path.dirname(__file__)

if args.version:
    version_main(version)
    read_sens = 0

if args.conf:
    config_file = args.conf
    if verbose_level > 2:
        print("config_file", config_file)

if args.get:
    conf = TempSet.Config()
    sensor = TempSet.SensorGateway()
    conf.read_config(0, config_file, path, db_all_remote, temp_all_remote, verbose_level)
    sensor.get_sensor_list(conf.temp_all)
    conf.add_config(config_file, path, sensor.sensor_list, verbose_level)
    read_sens = 0

if args.setup:
    conf = TempSet.Config()
    conf.input_config(config_file, db_all, temp_all)
    if conf.input_ok:  # check if input correct
        sensor = TempSet.SensorGateway()
        sensor.get_sensor_list(conf.temp_all)
        conf.write_config(config_file, path, html_single_file, sensor.sensor_list, verbose_level)
        conf.read_config(1, config_file, path, db_all_remote, temp_all_remote, verbose_level)
        db = TempSet.Influx()
        db.create_database(conf.db_all, verbose_level)
    read_sens = 0

conf = TempSet.Config()
conf.read_config(0, config_file, path, db_all_remote, temp_all_remote, verbose_level)
db = TempSet.Influx()
h = TempSet.HtmlCreator()

if args.remote:
    conf.db_all = conf.db_all_remote
    conf.temp_all = conf.temp_all_remote
    remote_set = 1

if args.create:
    db.create_database(db_all, verbose_level)
    read_sens = 0

if args.read:
    db.read_records(args.read, conf.db_all, conf.db_fields_str, verbose_level, conf.db_fields)
    read_sens = 0

if args.kill:
    db.kill_db_entries(conf.db_all, verbose_level)
    read_sens = 0

if args.xxx:
    db.clean_records(conf.db_fields, conf.db_all, conf.db_fields_str, verbose_level)
    read_sens = 0

if args.html_single:
    h.write_html_single(conf.html_single_file, path, conf.db_all, conf.db_fields, conf.db_fields_str,
                        conf.web_alert_dict, conf.web_field_dict, verbose_level)
    read_sens = 0

if args.html_multi:
    config_files = args.html_multi
    multi_conf = []

    if verbose_level > 2:
        print("config_files: ", config_files)
    for file in config_files.split(","):

        conf.read_config(1, file, path, db_all_remote, temp_all_remote, verbose_level)
        multi = TempSet.ConfigMulti(conf.db_all, conf.db_all_remote, conf.db_fields,
                                    conf.db_fields_str, conf.web_alert_dict, conf.web_field_dict)

        multi_conf.append(multi)

    h.write_html_multi(html_multi_file, path, config_files, multi_conf, remote_set, verbose_level)
    read_sens = 0

if read_sens:
    if verbose_level > 0:
        print(sys.argv[0], " - reading sensors ...  ", now)
    read = TempSet.ReadSensor()
    read.read_sensors(1, conf.temp_all, conf.sensor_dict_offset, dead_lo, dead_hi, error_low, error_high, verbose_level)
    if database_level:
        db.write_database(read.sensor_count, read.sensor_data, conf.sensor_dict, conf.db_all, verbose_level)
    else:
        print("No Data writen in Database!")

# Quit python script
sys.exit(0)
