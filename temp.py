#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Read 1-Wire sensors and write into database
#

# from influxdb import InfluxDBClient
# import ow
# import os
# import sys  # Import sys module
# import datetime
from pyownet import protocol
import time
import argparse  # analyze command line arguments

from temp_html import *
from temp_database import *

config_file = 'temp-config.txt'
html_single_file = 'www/temp-single-2.html'
html_multi_file = 'www/temp-multi.html'

db_fields = []              # list of database fields
db_dict = {}                # dictionary
web_field_dict = {}         # dictionary
web_alert_dict = {}         # dictionary
sensor_list = []            # list of sensors
sensor_locations = []       # list of locations
sensor_dict = {}            # dictionary -> sensor : location
sensor_offset = []          # sensor offset
sensor_dict_offset = {}     # dictionary -> sensor : offset

# define range for faulty sensor data
dead_max = 110
dead_hi = 80.0
dead_lo = -30.0
error_low = -100
error_high = 125

db_Host = "localhost"               # host - local database
db_User = "influxdb-user"           # username
db_Password = "influxdb_password"   # password
db_Database = "temp"                # datenbank
db_Table = "tempdat"                # Table
db_Port = "8086"                    # port
db_RHost = "127.0.0.1"              # host - Remote Database / optional
db_RUser = "influxdb-user"          # username
db_RPassword = "influx_password"    # password
db_RDatabase = "Temp"               # datenbank
db_RTable = "Tempdat"               # Table
db_RPort = "8086"                   # port
db_fields_all = ""
db = ""

temp_host = "localhost"             # host - local temp server
temp_port = "4304"                  # port
temp_r_host = "127.0.0.1"            # host - Remote temp server
temp_r_port = "4304"                 # port

db_all = [db_Table, db_Database, db_Host, db_User, db_Password, db_Port]
db_all_local = [db_Table, db_Database, db_Host, db_User, db_Password, db_Port]
db_all_remote = [db_RTable, db_RDatabase, db_RHost, db_RUser, db_RPassword, db_RPort]

temp_all = [temp_host, temp_port]
temp_all_local = [temp_host, temp_port]
temp_all_remote = [temp_r_host, temp_r_port]

sensordata = []
data_temp = []
remote_set = 0

verbose_level = 1  # default: show status messages
database_level = 1  # default: write to database
config_level = 0  # default: do not read config file
setup_level = 0  # default: do not read config file
read10_level = 0  # default: do not read
remote_level = 0  # default: use local database
read_sens = 1

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
                    help="create web page(html)with last entry from multiple configfiles")

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
                    const='value-to-store', help="clean DB entrie select by Time", )

parser.add_argument('--version', action='store_const', dest='version',
                    const='value-to-store', help="Version over view")

parser.add_argument('--conf', dest='conf', help="set config flie", type=str)

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


def version_main(v_main):
    print("version_main: ", v_main)
    print("version_db  : ", version_db())
    print("version_html: ", version_html())

    sys.exit(0)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def temp_connect(temp_all):
    global owproxy
    temp_host = temp_all[0]
    temp_port = temp_all[1]

    try:
        owproxy = protocol.proxy(temp_host, temp_port)

    except:
          print("PANIC - cannot connect to database")
          print('Error class:', sys.exc_info()[0])
          print('Error code :', sys.exc_info()[1])
          print('host       :', temp_host)
          print('port       :', temp_port)
          sys.exit(2)

    return (0)

# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


def write_config():
    global db_Host
    global db_Database
    global db_User
    global db_Password
    global db_Table
    global db_fields_all
    global db_Port
    global db_all

    global temp_host
    global temp_port
    global temp_all

    print("Write new config file", config_file)
    var = input("Enter yes: ")
    if var == "yes":

        var = input("Influxdb-Serverhost address  (default [" + db_Host + "]):")
        if len(var) != 0:
            db_Host = var
        var = input("Influxdb-Serverhost port     (default [" + db_Port + "]):")
        if len(var) != 0:
            db_Port = var
        var = input("Influxdb-Server user name    (default [" + db_User + "]):")
        if len(var) != 0:
            db_User = var
        var = input("Influxdb-Server password     (default [" + db_Password + "]):")
        if len(var) != 0:
            db_Password = var
        var = input("Influxdb-Server database     (default [" + db_Database + "]):")
        if len(var) != 0:
            db_Database = var
        var = input("Influxdb-Server table        (default [" + db_Table + "]):")
        if len(var) != 0:
            db_Table = var
        var = input("OW-Serverhost addresse       (default [" + temp_host + "]):")
        if len(var) != 0:
            temp_host = var
        var = input("OW-Serverhost port           (default [" + temp_port + "]):")
        if len(var) != 0:
            temp_port = var

        print(
            "check: " + db_Host + " " + db_Port + " " + db_User + " " + db_Password + " " + db_Database + " " + db_Table
            + " " + temp_host + " " + temp_port)
        var = input("Enter ok: ")
        if var != "ok":
            print("no file created")
            return (1)

        print("creating config file now...")
        now = time.strftime("%d.%m.%Y - %H:%M:%S Uhr")
        file_config = open(config_file, "w")
        file_config.write("# config file for temp.py\n")
        file_config.write("# created on " + now + "\n")
        file_config.write("# -----------------------------------------------------------\n")
        file_config.write("# Web config file path/name \n")
        file_config.write("html_file www/temp-single.html\n")
        file_config.write("# -----------------------------------------------------------\n")
        file_config.write("# Influxdb Server\n")
        file_config.write("# Syntax:\n")
        file_config.write("# Tag ID [normal] (Optional:[backup])\n")
        file_config.write("Host " + db_Host + "\n")
        file_config.write("Port " + db_Port + "\n")
        file_config.write("User " + db_User + "\n")
        file_config.write("Password " + db_Password + "\n")
        file_config.write("Database " + db_Database + "\n")
        file_config.write("Table " + db_Table + "\n")
        file_config.write("# -----------------------------------------------------------\n")
        file_config.write("# OW Server\n")
        file_config.write("# Syntax:\n")
        file_config.write("# Tag ID [normal] (Optional:[backup])\n")
        file_config.write("Temp-Host " + temp_host + "\n")
        file_config.write("Temp-Port " + temp_port + "\n")
        file_config.write("# Database Field Key's")
        file_config.write("# -----------------------------------------------------------\n")
        file_config.write("dbfield tbd\n")
        file_config.write("dbfield tbd\n")
        file_config.write("dbfield tbd\n")
        file_config.write("dbfield tbd\n")
        file_config.write("dbfield tbd\n")
        file_config.write("dbfield tbd\n")
        file_config.write("dbfield tbd\n")
        file_config.write("dbfield tbd\n")
        file_config.write("# WEB Field Key's Syntax: \n")
        file_config.write("# web_field [dbfield] [Field Key]\n")
        file_config.write("# -----------------------------------------------------------\n")
        file_config.write("web_field tbd tbd\n")
        file_config.write("web_field tbd tbd\n")
        file_config.write("web_field tbd tbd\n")
        file_config.write("web_field tbd tbd\n")
        file_config.write("web_field tbd tbd\n")
        file_config.write("web_field tbd tbd\n")
        file_config.write("web_field tbd tbd\n")
        file_config.write("# WEB Alert Temp \n")
        file_config.write("# max temp per Sensor Syntax: \n")
        file_config.write("# web_alert [dbfield] [Temp-high] (Optional:[Temp-low])\n")
        file_config.write("# -----------------------------------------------------------\n")
        file_config.write(" web_alert tbd 0\n")
        file_config.write(" web_alert tbd 0\n")
        file_config.write(" web_alert tbd 0\n")
        file_config.write(" web_alert tbd 0\n")
        file_config.write(" web_alert tbd 0\n")
        file_config.write(" web_alert tbd 0\n")
        file_config.write(" web_alert tbd 0\n")
        file_config.write(" web_alert tbd 0\n")
        file_config.write("# Syntax: \n")
        file_config.write("# Sensor [Sensor ID] [Temp Offset] [Sensor Field in Database]\n")
        file_config.write("# -----------------------------------------------------------\n")
        print("look for connected sensors on OW Server")
        temp_all = [temp_host, temp_port]
        temp_connect(temp_all)
        sensorlist = owproxy.dir()  # get sensor
        for sensor in sensorlist:
            w1_slave = sensor._path
            if verbose_level:
                print(w1_slave)
            file_config.write("Sensor " + w1_slave + "  0   tbd\n")
        file_config.close
    else:
        print("request cancelled check OW Server address")
        return ()

    return ()


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


def add_config():
    global temp_host
    global temp_port
    global temp_all

    global temp_r_host
    global temp_r_port
    global temp_all_remote

    now = time.strftime("%d.%m.%Y - %H:%M:%S Uhr")

    try:

        file = open(config_file, "r")
        settings = []  # Erstellt ein Variablenarray, das die Einstellungen speichert
        for line in file:  #
            if line[0] != "#":  # i.e. ignore comment lines
                settings.append(line)
        file.close

        for x in range(0, len(settings)):
            line = settings[x]
            if verbose_level > 3:
                print(x, ": ", line)
            item1 = line.split()
            if len(item1) > 1:  # need 4 items for sensor: tag, value1, value2, value3
                if verbose_level > 2:
                    print(item1[0], item1[1], len(item1))
                if item1[0] == "Temp-Host":
                    temp_host = item1[1]
                    if len(item1) > 2:
                        temp_r_host = item1[2]
                if item1[0] == "Temp-Port":
                    temp_port = item1[1]
                    if len(item1) > 2:
                        temp_r_port = item1[2]

        temp_all = [temp_host, temp_port]
        temp_all_remote = [temp_r_host, temp_r_port]

    except IOError:
        print("----------------------", now)
        print("Cannot find file: " + config_file)

    file_config = open(config_file, "a")
    file_config.write("\n# ----------------------------------------\n")
    file_config.write("# sensors added on " + now + "\n")
    file_config.write("# ----------------------------------------\n")

    if verbose_level > 0:
        print("Open 1-wire slaves list for reading")
    temp_connect(temp_all)
    sensorlist = owproxy.dir()  # get sensor
    # Repeat following steps with each 1-wire slave
    for sensor in sensorlist:
        w1_slave = sensor._path  # Extract 1-wire slave
        if verbose_level > 0:
            print(w1_slave)
        file_config.write("#Sensor " + w1_slave + "\n")

    file_config.close()

    sys.exit(0)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def read_config(init_level, config_file):
    global html_single_file

    global db_Host
    global db_Database
    global db_User
    global db_Password
    global db_Table
    global db_Port
    global db_all

    global db_RHost
    global db_RDatabase
    global db_RUser
    global db_RPassword
    global db_RTable
    global db_RPort
    global db_all_remote

    global db_fields_all

    global temp_host
    global temp_port
    global temp_all

    global temp_r_host
    global temp_r_port
    global temp_all_remote

    config_dict = {}

    error_level = 0

    if verbose_level > 1:
        print("reading config file ", config_file)
    now = time.strftime("%d.%m.%Y - %H:%M:%S Uhr")
    if verbose_level > 1:
        print("-------------------------------------", now)

    try:

        file = open(config_file, "r")
        settings = []  # Erstellt ein Variablenarray, das die Einstellungen speichert
        for line in file:  #
            if line[0] != "#":  # i.e. ignore comment lines
                settings.append(line)
        file.close

        for x in range(0, len(settings)):
            line = settings[x]
            if verbose_level > 3:
                print(x, ": ", line)
            item1 = line.split()
            if len(item1) > 1:  # need 4 items for sensor: tag, value1, value2, value3
                if verbose_level > 2:
                    print(item1[0], item1[1], len(item1))
                if item1[0] == "html_file":
                    html_single_file = item1[1]
                if item1[0] == "Host":
                    db_Host = item1[1]
                    if len(item1) > 2:
                        db_RHost = item1[2]  # remote database
                if item1[0] == "Port":
                    db_Port = item1[1]
                    if len(item1) > 2:
                        db_RPort = item1[2]
                if item1[0] == "Database":
                    db_Database = item1[1]
                    if len(item1) > 2:
                        db_RDatabase = item1[2]
                if item1[0] == "Table":
                    db_Table = item1[1]
                    if len(item1) > 2:
                        db_RTable = item1[2]
                if item1[0] == "User":
                    db_User = item1[1]
                    if len(item1) > 2:
                        db_RUser = item1[2]
                if item1[0] == "Password":
                    db_Password = item1[1]
                    if len(item1) > 2:
                        db_RPassword = item1[2]
                if item1[0] == "Temp-Host":
                    temp_host = item1[1]
                    if len(item1) > 2:
                        temp_r_host = item1[2]
                if item1[0] == "Temp-Port":
                    temp_port = item1[1]
                    if len(item1) > 2:
                        temp_r_port = item1[2]
                if item1[0] == "dbfield":
                    db_fields.append(item1[1])
                if len(item1) > 2:
                    if item1[0] == "web_field":
                        web_field_dict[item1[1]] = item1[2]
                    if item1[0] == "web_alert":
                        if len(item1) > 3:
                            web_alert_dict[item1[1]] = item1[2], item1[3]
                        else:
                            web_alert_dict[item1[1]] = item1[2]
                if len(item1) > 3:
                    if item1[0] == "Sensor":
                        if verbose_level > 2:
                            print("Sensor", item1[1], "Offset:", item1[2], "Field:", item1[3])
                        sensor_list.append(item1[1])
                        sensor_locations.append(item1[3])
                        sensor_dict[item1[1]] = item1[3]
                        sensor_offset.append(item1[2])
                        sensor_dict_offset[item1[1]] = item1[2]

        for x in range(0, len(db_fields)):
            if verbose_level > 2:
                print("db_fields: ", db_fields[x])
            if x == 0:
                db_fields_all = str(db_fields[x])
            else:
                db_fields_all = db_fields_all + ", " + str(db_fields[x])
            db_dict[db_fields[x]] = x
        if verbose_level > 2:
            print("all db fields: ", db_fields_all)

        db_all = [db_Table, db_Database, db_Host, db_User, db_Password, db_Port]
        db_all_remote = [db_RTable, db_RDatabase, db_RHost, db_RUser, db_RPassword, db_RPort]

        temp_all = [temp_host, temp_port]
        temp_all_remote = [temp_r_host, temp_r_port]

        if verbose_level > 1:
            print("Database (local) : ", db_all)
            print("Database (remote): ", db_all_remote)

        if verbose_level > 2:
            print("all sensor list: ", sensor_list)
        if init_level == 0:  # during initital setup do not display panic messages
            for x in range(0, len(sensor_list)):
                x_str = sensor_locations[x]
                if str(db_dict.get(x_str)) == "None":
                    print("PANIC: Sensor", sensor_list[x], "is using unknown location", x_str)
                    if x == 0:
                        print("please assign one out of dbfield")
                        print(db_fields)

        # config dict for muli web output
        config_dict = {'db_all': db_all, 'db_all_remote': db_all_remote, 'db_fields': db_fields,
                       'db_fields_all': db_fields_all, 'web_field_dict': web_field_dict,
                       'web_alert_dict': web_alert_dict}

        if verbose_level > 1:
            print("html_single_file: ", html_single_file)
            print("sensor_dict:", sensor_dict)
            print("sensor_dict_offset:", sensor_dict_offset)
            print("db_fields:", db_fields)
            print("db_dict:", db_dict)
            print("web_field_dict", web_field_dict)
            print("web_alert_dict", web_alert_dict)
            print("config_dict: ", config_dict)

        if error_level > 0:
            print("please edit config file " + config_file + " and assign one out of dbfield")
            print("e.g. Sensor " + sensor_list[x] + " " + db_fields[0])
            print("available fields: " + str(db_fields))
            sys.exit(0)

    except IOError:
        print("----------------------", now)
        print("Cannot find file: " + config_file)
    return (config_dict)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def read_sensor(sensor_slave, sensor_slave_dict_offset):
    # Open 1-wire slave file

    try:

        sensor_id = sensor_slave  # id of 1-wire sensor
        sensor_tpye = owproxy.read(sensor_slave + "type")  # type of 1-wire sensor
        sensor_tpye = sensor_tpye.decode()  # decode bytes of type

        if verbose_level > 2:
            print("ID: ", sensor_id)
            print("Type: ", str(sensor_tpye))

        if sensor_tpye == "DS2438":
            # DS2438 humidity HIH4000
            vdd = float(owproxy.read(sensor_slave + "VDD"))
            vad = float(owproxy.read(sensor_slave + "VAD"))
            temp = float(owproxy.read(sensor_slave + "temperature"))
            hum_2 = float(owproxy.read(sensor_slave + "humidity"))  # for testing
            hum = ((vad / vdd) - 0.16) / 0.00627 * (1.0546 - 0.00216 * temp)

            dataset = sensor_slave
            sen_off = str(sensor_slave_dict_offset.get(dataset))  # sensor dem offset zuordnen
            if verbose_level > 1:
                print(dataset, '-> Sensor ID:', dataset, 'Offset:', sen_off)
            if sen_off == 'None':
                print('PANIC: unknown sensor ', dataset)

            value = round(float(hum), 3) + float(sen_off)

            if verbose_level > 1:
                print("VDD:      ", vdd)
                print("VAD:      ", vad)
                print("temp:     ", temp)
                print("humidity_clac: ", hum)
                print("humidity_value: ", hum_2)
                print("offset:   ", sen_off)
                print("value:    ", value)

        else:
            # DS18S20  DS18B20
            temp = float(owproxy.read(sensor_slave + "temperature"))

            dataset = sensor_slave
            sen_off = str(sensor_slave_dict_offset.get(dataset))  # sensor dem offset zuordnen
            if verbose_level > 1:
                print(dataset, '-> Sensor ID:', dataset, 'Offset:', sen_off)
            if sen_off == 'None':
                print('PANIC: unknown sensor ', dataset)

            value = float(temp) + float(sen_off)

            if verbose_level > 1:
                print("temp:   ", temp)
                print("offset: ", sen_off)
                print("value:  ", value)

    except IOError:
        print("PANIC read_sensor - Cannot find file >" + sensor_slave + "< on OW Server")
        print("No sensor attached")
        print("check with > owdir")
        sys.exit(1)

    return (value, sensor_id, sensor_tpye)  # exit function read_sensor


# -------------------------------------------------------------------------------------------

def read_sensors(read_level, temp_all, sensor_slaves_dict_offset):
    sensor_count = 0
    temp_connect(temp_all)
    sensor_slaves = owproxy.dir()
    # Open 1-wire slaves list for reading
    try:

        w1_slaves = sensor_slaves

        # Print header for results table
        if verbose_level > 0:
            print('Sensor ID       |   Wert')
            print('------------------------------')

        # Repeat following steps with each 1-wire slave
        for sensor in w1_slaves:
            w1_slave = sensor
            time.sleep(0.2)
            read_value = read_sensor(w1_slave, sensor_slaves_dict_offset)  # call read function
            value = read_value[0]
            sensor_id = read_value[1]
            sensor_type = read_value[2]
            # check for faulty data
            if value <= dead_lo or value >= dead_hi or value > dead_max or value < error_low or value > error_high:
                if verbose_level > 1:
                    print("Panic", value)
                time.sleep(0.5)
                value = read_sensor(w1_slave, sensor_slaves_dict_offset)
                if verbose_level > 1:
                    print("2nd try", value)

            if value <= dead_lo or value >= dead_hi or value > dead_max:  # check for faulty data
                if verbose_level > 0:
                    print("Panic", value)
                time.sleep(1.5)
                value = read_sensor(w1_slave, sensor_slaves_dict_offset)
                if verbose_level > 0:
                    print("3rd try", value)

            if verbose_level > 0:
                if sensor_type == 'DS2438':
                    # DS2438
                    print(str(sensor_id) + ' | {:5.2f} {}'.format(value, '%rH'))  # Print value
                else:
                    print(str(sensor_id) + ' | {:5.3f} {}'.format(value, '°C'))  # Print value
            sensor_count = sensor_count + 1

            if value < error_low or value > error_high:
                value = "none"  # ???

            if read_level:
                sensordata.append((sensor_id, value))  # store value in database
        if verbose_level > 2:
            print("sensors detected: ", sensor_count)
            print("sensordata: ", sensordata)
        return (sensor_count)  # exit function read_sensors

    except IOError:
        print("----------------------", now)
        print("read_sensors - Cannot find file: ", sensor_slaves)
    return ()


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

now = time.strftime("%d.%m.%Y - %H:%M:%S Uhr")

if args.version:
    version_main(version)

if args.conf:
    config_file = args.conf
    if verbose_level > 2:
        print("config_file", config_file)

if args.get:
    add_config()

if args.setup:
    return_val = write_config()
    if return_val == 0:
        print("read config file which has been created")
        read_config(1, config_file)
        print("create database incl. tables")
        create_database(db_all, db_fields_all, verbose_level)
    sys.exit(0)

return_val = read_config(0, config_file)  # db_all,db_fields_all,verbose_level)
if verbose_level > 3:
    print("return_val:: ", return_val)

if return_val == {}:
    print("Error: cannot find config file " + config_file)
    print("Please run >temp.py --setup")
    sys.exit(0)


if args.remote:
    db_all = db_all_remote
    remote_set = 1

if args.create:
    create_database(db_all, db_fields_all, verbose_level)
    read_sens = 0

if args.read:
    read_records(args.read, db_all, db_fields_all, verbose_level, db_fields)
    read_sens = 0

if args.kill:
    kill_dbentries(db_all, verbose_level)
    read_sens = 0

if args.xxx:
    clean_records(db_fields, db_all, db_fields_all, verbose_level)
    read_sens = 0

if args.html_single:
    write_html_single(html_single_file, db_all, db_fields_all, verbose_level, db_fields, web_alert_dict, web_field_dict)
    read_sens = 0

if args.html_multi:
    config_files = args.html_multi
    array2 = []

    if verbose_level > 2:
        print("config_files: ", config_files)
    for x in config_files.split(","):
        db_fields = []  # list of database fields
        db_dict = {}  # dictionary
        web_field_dict = {}  # dictionary
        web_alert_dict = {}  # dictionary
        sensor_list = []  # list of sensors
        sensor_locations = []  # list of locations
        sensor_dict = {}  # dictionary -> sensor : location
        sensor_offset = []  # sensor offset
        sensor_dict_offset = {}  # dictionary -> sensor : offset

        array1 = read_config(1, x)
        if verbose_level > 2:
            print("Array1: ", array1)
        array2.append(array1)
        if verbose_level > 2:
            print("Array2: ", array2)
    write_html_multi(html_multi_file, verbose_level, array2, remote_set)
    read_sens = 0

if read_sens:
    if verbose_level > 0:
        print(sys.argv[0], " - reading sensors ...  ", now)
    read_items = read_sensors(1, temp_all, sensor_dict_offset)  # read + collect data
    if database_level:
        write_database(read_items, sensordata, sensor_dict, db_all, verbose_level)

# Quit python script
sys.exit(0)
