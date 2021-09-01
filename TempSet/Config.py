import time
import os


class Config:

    def __init__(self):
        self.input_ok = True
        self.db_all = []
        self.db_all_remote = []
        self.temp_all = []
        self.temp_all_remote = []
        self.db_fields = []
        self.db_fields_str = ""
        self.web_field_dict = {}
        self.web_alert_dict = {}
        self.sensor_dict = {}
        self.sensor_dict_offset = {}
        self.html_single_file = ""

    def input_config(self, config_file, db_all, temp_all):

        print("Write new config file", config_file)
        var = input("Enter yes: ")
        if var == "yes":

            var = input("Influxdb-Server address  (default [" + db_all[0] + "]):")
            if len(var) != 0:
                db_all[0] = var
            var = input("Influxdb-Server port     (default [" + db_all[1] + "]):")
            if len(var) != 0:
                db_all[1] = var
            var = input("Influxdb-Server user name    (default [" + db_all[2] + "]):")
            if len(var) != 0:
                db_all[2] = var
            var = input("Influxdb-Server password     (default [" + db_all[3] + "]):")
            if len(var) != 0:
                db_all[3] = var
            var = input("Influxdb-Server database     (default [" + db_all[4] + "]):")
            if len(var) != 0:
                db_all[4] = var
            var = input("Influxdb-Server table        (default [" + db_all[5] + "]):")
            if len(var) != 0:
                db_all[5] = var
            var = input("OW-Server address       (default [" + temp_all[0] + "]):")
            if len(var) != 0:
                temp_all[0] = var
            var = input("OW-Server port           (default [" + temp_all[1] + "]):")
            if len(var) != 0:
                temp_all[1] = var

            self.db_all = db_all
            self.temp_all = temp_all

            # db_all = [db_host, db_port, db_user, db_password, db_table, db_database]
            # db_host = db_all[0]
            # db_port = db_all[1]
            # db_user = db_all[2]
            # db_password = db_all[3]
            # db_table = db_all[4]
            # db_database = db_all[5]
            #
            # temp_all = [temp_host, temp_port]
            # temp_host = temp_all[0]
            # temp_port = temp_all[1]

            print('host       :', db_all[0])
            print('port       :', db_all[1])
            print('user       :', db_all[2])
            print('passwd     :', db_all[3])
            print('database   :', db_all[4])
            print('table      :', db_all[5])
            print('host       :', temp_all[0])
            print('port       :', temp_all[1])

            var = input("Enter ok: ")
            if var != "ok":
                print("no file created")
                self.input_ok = False

    def write_config(self, config_file, path, html_single_file, w1_slaves, verbose_level):

        db_host = self.db_all[0]
        db_port = self.db_all[1]
        db_user = self.db_all[2]
        db_password = self.db_all[3]
        db_table = self.db_all[4]
        db_database = self.db_all[5]

        temp_host = self.temp_all[0]
        temp_port = self.temp_all[1]

        print("creating config file now...")
        now = time.strftime("%d.%m.%Y - %H:%M:%S Uhr")
        with open(os.path.join(path, config_file), "w") as file_config:
            file_config.write("# config file for temp.py\n")
            file_config.write("# created on " + now + "\n")
            file_config.write("# -----------------------------------------------------------\n")
            file_config.write("# Web config file path/name \n")
            file_config.write("html_file " + html_single_file + "\n")
            file_config.write("# -----------------------------------------------------------\n")
            file_config.write("# Influxdb Server\n")
            file_config.write("# Syntax:\n")
            file_config.write("# Tag ID [normal] (Optional:[backup])\n")
            file_config.write("Host " + db_host + "\n")
            file_config.write("Port " + db_port + "\n")
            file_config.write("User " + db_user + "\n")
            file_config.write("Password " + db_password + "\n")
            file_config.write("Database " + db_database + "\n")
            file_config.write("Table " + db_table + "\n")
            file_config.write("# -----------------------------------------------------------\n")
            file_config.write("# OW Server\n")
            file_config.write("# Syntax:\n")
            file_config.write("# Tag ID [normal] (Optional:[backup])\n")
            file_config.write("Temp-Host " + temp_host + "\n")
            file_config.write("Temp-Port " + temp_port + "\n")
            file_config.write("# Database Field Key's")
            file_config.write("# -----------------------------------------------------------\n")
            file_config.write("dbfield tbd-1\n")
            file_config.write("dbfield tbd-2\n")
            file_config.write("dbfield tbd-3\n")
            file_config.write("dbfield tbd-4\n")
            file_config.write("dbfield tbd-5\n")
            file_config.write("dbfield tbd-6\n")
            file_config.write("dbfield tbd-7\n")
            file_config.write("dbfield tbd-8\n")
            file_config.write("# WEB Field Key's Syntax: \n")
            file_config.write("# web_field [dbfield] [Field Key]\n")
            file_config.write("# -----------------------------------------------------------\n")
            file_config.write("web_field tbd-1 tad-1\n")
            file_config.write("web_field tbd-2 tad-2\n")
            file_config.write("web_field tbd-3 tad-3\n")
            file_config.write("web_field tbd-4 tad-4\n")
            file_config.write("web_field tbd-5 tad-5\n")
            file_config.write("web_field tbd-6 tad-6\n")
            file_config.write("web_field tbd-7 tad-7\n")
            file_config.write("web_field tbd-8 tad-8\n")
            file_config.write("# WEB Alert Temp \n")
            file_config.write("# max temp per Sensor Syntax: \n")
            file_config.write("# web_alert [dbfield] [Temp-high] (Optional:[Temp-low])\n")
            file_config.write("# -----------------------------------------------------------\n")
            file_config.write(" web_alert tbd-1 0\n")
            file_config.write(" web_alert tbd-2 0\n")
            file_config.write(" web_alert tbd-3 0\n")
            file_config.write(" web_alert tbd-4 0\n")
            file_config.write(" web_alert tbd-5 0\n")
            file_config.write(" web_alert tbd-6 0\n")
            file_config.write(" web_alert tbd-7 0\n")
            file_config.write(" web_alert tbd-8 0\n")
            file_config.write("# Syntax: \n")
            file_config.write("# Sensor [Sensor ID] [Temp Offset] [Sensor Field in Database]\n")
            file_config.write("# -----------------------------------------------------------\n")
            print("look for connected sensors on OW Server")
            for w1_slave in w1_slaves:
                if verbose_level:
                    print(w1_slave)
                file_config.write("Sensor " + w1_slave + "  0   tbd-\n")

    @staticmethod
    def add_config(config_file, path, w1_slaves, verbose_level):

        now = time.strftime("%d.%m.%Y - %H:%M:%S Uhr")

        with open(os.path.join(path, config_file), "a") as file_config:
            file_config.write("\n# ----------------------------------------\n")
            file_config.write("# sensors added on " + now + "\n")
            file_config.write("# ----------------------------------------\n")
    
            if verbose_level > 0:
                print("Open 1-wire slaves list for reading")
    
            for w1_slave in w1_slaves:
                if verbose_level > 0:
                    print(w1_slave)
                file_config.write("#Sensor " + w1_slave + "\n")

    def read_config(self, init_level, config_file, path, db_all_remote, temp_all_remote, verbose_level):

        db_host = ""
        db_port = ""
        db_user = ""
        db_password = ""
        db_table = ""
        db_database = ""

        db_r_host = db_all_remote[0]
        db_r_port = db_all_remote[1]
        db_r_user = db_all_remote[2]
        db_r_password = db_all_remote[3]
        db_r_table = db_all_remote[4]
        db_r_database = db_all_remote[5]

        db_dict = {}
        db_fields = []
        db_fields_str = ""

        temp_host = ""
        temp_port = ""

        temp_r_host = temp_all_remote[0]
        temp_r_port = temp_all_remote[1]

        web_field_dict = {}
        web_alert_dict = {}

        sensor_list = []
        sensor_locations = []
        sensor_dict = {}
        sensor_offset = []
        sensor_dict_offset = {}

        html_single_file = ""

        now = time.strftime("%d.%m.%Y - %H:%M:%S Uhr")

        if verbose_level > 1:
            print("reading config file ", os.path.join(path, config_file))

        if verbose_level > 1:
            print("-------------------------------------", now)

        try:

            with open(config_file, "r") as file:
                settings = []
                for line in file:
                    if line[0] != "#":  # i.e. ignore comment lines
                        settings.append(line)

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
                        db_host = item1[1]
                        if len(item1) > 2:
                            db_r_host = item1[2]  # remote database
                    if item1[0] == "Port":
                        db_port = item1[1]
                        if len(item1) > 2:
                            db_r_port = item1[2]
                    if item1[0] == "Database":
                        db_database = item1[1]
                        if len(item1) > 2:
                            db_r_database = item1[2]
                    if item1[0] == "Table":
                        db_table = item1[1]
                        if len(item1) > 2:
                            db_r_table = item1[2]
                    if item1[0] == "User":
                        db_user = item1[1]
                        if len(item1) > 2:
                            db_r_user = item1[2]
                    if item1[0] == "Password":
                        db_password = item1[1]
                        if len(item1) > 2:
                            db_r_password = item1[2]
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
                    db_fields_str = str(db_fields[x])
                else:
                    db_fields_str = db_fields_str + ", " + str(db_fields[x])
                db_dict[db_fields[x]] = x
            if verbose_level > 2:
                print("all db fields: ", db_fields_str)

            self.db_all = [db_host, db_port, db_user, db_password, db_table, db_database]
            self.db_all_remote = [db_r_host, db_r_port, db_r_user, db_r_password, db_r_table, db_r_database]

            self.temp_all = [temp_host, temp_port]
            self.temp_all_remote = [temp_r_host, temp_r_port]

            self.db_fields = db_fields
            self.db_fields_str = db_fields_str

            self.web_alert_dict = web_alert_dict
            self.web_field_dict = web_field_dict

            self.sensor_dict = sensor_dict
            self.sensor_dict_offset = sensor_dict_offset

            self.html_single_file = os.path.join(os.path.dirname(config_file), html_single_file)

            if verbose_level > 1:
                print("Database  (local) : ", self.db_all)
                print("Database  (remote): ", self.db_all_remote)
                print("OW-Server (local) : ", self.temp_all)
                print("OW-Server (remote): ", self.temp_all_remote)

            if verbose_level > 2:
                print("all sensor list: ", sensor_list)
            if init_level == 0:  # during initial setup do not display panic messages
                for x in range(0, len(sensor_list)):
                    x_str = sensor_locations[x]
                    if str(db_dict.get(x_str)) == "None":
                        print("PANIC: Sensor", sensor_list[x], "is using unknown location", x_str)
                        if x == 0:
                            print("please assign one out of dbfield")
                            print(db_fields)

            if verbose_level > 1:
                print("html_single_file: ", html_single_file)
                print("sensor_dict:", sensor_dict)
                print("sensor_dict_offset:", sensor_dict_offset)
                print("db_fields:", db_fields)
                print("db_dict:", db_dict)
                print("web_field_dict", web_field_dict)
                print("web_alert_dict", web_alert_dict)

        except IOError:
            print("----------------------", now)
            print("Cannot find file: " + os.path.join(path, config_file))
