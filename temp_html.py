#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Embedded file name: ./temp_html.py

# import os
# import sys  # Import sys module
# import datetime
from temp_database import read_records

config_fiels = []

version = '1.7'


# -------------------------------------------------------------------------------------------

def version_html():
    version_h = version
    return version_h


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
    dataset = read_records(1, db_all, db_fields_all, verbose_level, db_fields)
    if verbose_level > 3:
        print("Dataset-(html): ", dataset)

    write_html(file_name, dataset, verbose_level, db_fields, web_alert_dict, web_field_dict)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

def write_html(file_name, dataset, verbose_level, db_fields, web_alert_dict, web_field_dict):
    # Erstellt eine Datei und Öffnet sie zum beschreiben (writing 'w')
    if verbose_level > 0:
        print("create html: ", file_name)

    colums = 3  # set up colums of web Page 2 or 3

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
        f.write("  <style type='text/css'>" + "\n")
        f.write(
            "   body { background-color: dimgrey; text-align: center; font-family: Verdana, Geneva, Tahoma, sans-serif; color: white }" + "\n")
        f.write("   #werte { position: relative; margin-left: 2%; margin-top: 1% }" + "\n")
        f.write(
            "   #box { border: 5px solid darkgreen; background-color: lightgreen; font-size: 27px; font-weight: 900; color:black }" + "\n")
        f.write(
            "   #box-orange { border: 5px solid darkorange; background-color: peachpuff; font-size: 27px; font-weight: 900; color: black }" + "\n")
        f.write(
            "   #box-red { border: 5px solid darkred; background-color: lightpink; font-size: 27px; font-weight: 900; color: black }" + "\n")
        f.write(
            "   #box-blue { border: 5px solid darkblue; background-color: lightblue; font-size: 27px; font-weight: 900; color: black }" + "\n")
        f.write(
            "   #box-none { border: 5px solid darkgray; background-color: lightgray; font-size: 27px; font-weight: 900; color: black }" + "\n")  # !!
        if colums == 3:
            f.write("   #tag { float: center; margin-top: -0.5em }" + "\n")
            f.write("   #field { float: center; font-size: 32px }" + "\n")
            f.write(
                "   .wert { float: left; height: 3.218em; width: 31%; margin-right: 0.5%; margin-bottom: 1%; margin-left: 0.5%; }" + "\n")
        else:
            f.write("   #tag { float: left; margin-left: 0.5em }" + "\n")
            f.write("   #field { float: right; margin-right: 0.5em; font-size: 32px }" + "\n")
            f.write(
                "   .wert { float: left; height: 3.218em; width: 47%; margin-right: 0.5%; margin-bottom: 1%; margin-left: 0.5%; }" + "\n")
        f.write("  </style>" + "\n")
        f.write(" </head>" + "\n")
        f.write(" <body>" + "\n")
        datetimestring = dataset.get("time")
        f.write("  <h3>Zeit in UTC:  " + str(datetimestring) + "</h3>" + "\n")
        if verbose_level > 1:
            print("date written html: ", str(datetimestring))
        f.write("  <div id='werte'>" + "\n")

        for x in range(len(db_fields)):
            field = db_fields[x]
            field_list = dataset.get(field)
            web_tag = web_field_dict.get(field)
            web_alert_temp = web_alert_dict.get(field)
            if verbose_level > 2:
                print("field_list", field_list)
                print("field_list(type", type(field_list))
            if field_list != None:
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
                else:
                    if value2 >= 0:
                        field_id = "box-orange"
                    else:
                        if value3 <= 0:
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

            f.write("   <div id='" + field_id + "' class='wert'><p><div id='tag'>" + str(
                web_tag) + "</div>    <div id='field'>" + str(field_list) + "  &deg;C</div></p></div>" + "\n")

        f.write("  </div>" + "\n")
        f.write(" </body>" + "\n")
        f.write("</html>")

        # Die Datei schlie�en
        f.close()

    except:
        print("Error: can't open file " + file_name + " for writing")
        print("Please check if directory is existing")

    return ()
