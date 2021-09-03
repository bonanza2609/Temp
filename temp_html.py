#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Embedded file name: ./temp_html.py

# import os
# import sys  # Import sys module
# import datetime
from temp_database import read_records
import TempSet

config_fiels = []

version = '1.7'


# -------------------------------------------------------------------------------------------

def version_html():
    v_html = str("version_html:" + str(version))
    return (v_html)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def write_html_multi(html_multi_file, verbose_level, config_files, remote_set):
    if verbose_level > 1:
        print("read database's")

    file_name = html_multi_file

    dataset_multi = {}
    db_fields_multi = []
    web_alert_dict_multi = {}
    web_field_dict_multi = {}

    for x in range(len(config_files)):
        conf = config_files[x]
        db_all = conf.get("db_all")
        db_all_remote = conf.get("db_all_remote")
        db_fields = conf.get("db_fields")
        db_fields_all = conf.get("db_fields_all")
        web_alert_dict = conf.get("web_alert_dict")
        web_field_dict = conf.get("web_field_dict")
        if verbose_level > 3:
            print("conf: ", conf)
            print("db_all: ", db_all)
            print("db_all_remote: ", db_all_remote)
            print("db_fields: ", db_fields)
            print("db_fields_all: ", db_fields_all)
            print("web_alert_dict: ", web_alert_dict)
            print("web_field_dict: ", web_field_dict)
        if remote_set == 1:
            db_all = db_all_remote
        dataset = read_records(1, db_all, db_fields_all, verbose_level, db_fields)
        if verbose_level > 3:
            print("Dataset-(html): ", dataset)
        dataset_multi.update(dataset)
        db_fields_multi.extend(db_fields)
        web_alert_dict_multi.update(web_alert_dict)
        web_field_dict_multi.update(web_field_dict)

    if verbose_level > 2:
        print("Dataset-(Multi-html): ", dataset_multi)
        print("db_fields_multi: ", db_fields_multi)
        print("web_alert_dict_multi: ", web_alert_dict_multi)
        print("web_field_dict_multi: ", web_field_dict_multi)
        print("file_name: ", file_name)

    write_html(file_name, dataset_multi, verbose_level, db_fields_multi, web_alert_dict_multi, web_field_dict_multi)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def write_html_single(file_name, db_all, db_fields_all, verbose_level, db_fields, web_alert_dict, web_field_dict):
    if verbose_level > 1:
        print("read database")
    db = TempSet.Influx()
    db.read_records(1, db_all, db_fields_all,verbose_level, db_fields)
    # dataset = read_records(1, db_all, db_fields_all, verbose_level, db_fields)
    if verbose_level > 3:
        print("Dataset-(html): ", db.dataset)

    write_html(file_name, db.dataset, verbose_level, db_fields, web_alert_dict, web_field_dict)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def write_html(file_name, dataset, verbose_level, db_fields, web_alert_dict, web_field_dict):
    # Erstellt eine Datei und Öffnet sie zum beschreiben (writing 'w')
    if verbose_level > 0:
        print("create html: ", file_name)

    if verbose_level > 2:
        print("file_name: ", file_name)
        print("dataset: ", dataset)
        print("db_fields: ", db_fields)
        print("web_alert_dict: ", web_alert_dict)
        print("web_field_dict: ", web_field_dict)

    try:

        f = open(file_name, 'w')

        f.write("<!DOCTYPE html>" + "\n")
        f.write("<html>" + "\n")
        f.write(" <head>" + "\n")
        f.write("  <title>Temperatur</title>" + "\n")
        f.write("  <link rel='stylesheet' href='./temp-style.css' />" + "\n")
        f.write(" </head>" + "\n")
        f.write(" <body>" + "\n")
        datetimestring = dataset.get("time")
        f.write("  <h3>Zeit in UTC:  " + str(datetimestring) + "</h3>" + "\n")
        if verbose_level > 1:
            print("date written html: ", str(datetimestring))
        f.write("  <div class='values'>" + "\n")

        for x in range(len(db_fields)):
            field = db_fields[x]
            field_list = dataset.get(field)
            web_tag = web_field_dict.get(field)
            web_alert_temp = web_alert_dict.get(field)
            if verbose_level > 2:
                print("field_list", field_list)
                print("field_list(type", type(field_list))

            if field_list:
                if type(web_alert_temp) == tuple:  # (value 0 / value 1)
                    web_alert_temp_high = web_alert_temp[0]
                    web_alert_temp_low = web_alert_temp[1]
                else:
                    web_alert_temp_high = web_alert_temp
                    web_alert_temp_low = -99999
                if verbose_level > 2:
                    print("field_list(in-temp)", field_list)
                value1 = float(field_list) - float(web_alert_temp_high)
                value2 = float(field_list) - float(web_alert_temp_high) + 1
                value3 = float(field_list) - float(web_alert_temp_low)
                if verbose_level > 2:
                    print("value1: ", value1)
                    print("value2: ", value2)
                    print("value3: ", value3)
                if value1 >= 0:
                    field_id = "box-red"
                elif value2 >= 0:
                    field_id = "box-orange"
                elif value3 <= 0:
                    field_id = "box-blue"
                else:
                    field_id = "box"

                field_list = round(field_list, 1)
            else:
                field_id = "box-none"

            if verbose_level > 1:
                print("Field-(html):", field)
                print("Field entry-(html):", field_list)
                print("WEB-TAG (html):", web_tag)
                print("WEB-Alert-Temp (html):", web_alert_temp)
                print("Field-ID (html):", field_id)

            f.write("   <div class='value'>\n"
                    "    <div class='" + field_id + "'>\n"
                    "     <div class='tag'>" + str(web_tag) + "</div>\n"
                    "     <div class='field'>" + str(field_list) + "  &deg;C</div>\n"
                    "    </div>\n"
                    "   </div>\n")

        f.write("  </div>" + "\n")
        f.write(" </body>" + "\n")
        f.write("</html>")

        # Die Datei schlie�en
        f.close()

    except IOError:
        print("Error: can't open file " + file_name + " for writing")
        print("Please check if directory is existing")

    return ()
