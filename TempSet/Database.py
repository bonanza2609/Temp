from influxdb import InfluxDBClient
import sys


class Influx:
    def __init__(self):
        self.db = None
        self.db_val_x = None

    def db_connect(self, db_all, no_db, verbose_level):

        db_host = db_all[0]
        db_port = db_all[1]
        db_user = db_all[2]
        db_password = db_all[3]
        db_table = db_all[4]
        db_database = db_all[5]

        try:
            if no_db:
                if verbose_level > 0:
                    print("connect to host >", db_host, "< w/o database")
                self.db = InfluxDBClient(host=db_host, port=db_port, username=db_user, password=db_password)
            else:
                if verbose_level > 0:
                    print("connect to host >", db_host, "< and database >", db_database, "<")
                self.db = InfluxDBClient(host=db_host, port=db_port, username=db_user, password=db_password,
                                         database=db_database)

        except IOError:
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

    def db_interaction(self, db_all, stmt_x, int_level, verbose_level):

        db_host = db_all[0]
        db_port = db_all[1]
        db_user = db_all[2]
        db_password = db_all[3]
        db_table = db_all[4]
        db_database = db_all[5]

        if verbose_level > 2:
            print("stmt", stmt_x)

        self.db_connect(db_all, 1, verbose_level)  # open connection without databases

        try:
            if int_level == 0:  # create database
                self.db_connect(db_all, 1, verbose_level)  # open connection without databases
                self.db.create_database(stmt_x)
                self.db.close()
            elif int_level == 1:  # write into database
                self.db_connect(db_all, 0, verbose_level)  # open connection with databases
                self.db.write_points(stmt_x)
                self.db.close()
            elif int_level == 2:  # read from database
                self.db_connect(db_all, 0, verbose_level)  # open connection with databases
                self.db_val_x = self.db.query(stmt_x)
                self.db.close()
            elif int_level == 3:  # kill table from database
                self.db_connect(db_all, 0, verbose_level)  # open connection with databases
                self.db.drop_measurement(stmt_x)
                self.db.close()
            else:
                print("unknown int_level for stmt: ", stmt_x)

        except IOError:
            print('PANIC - cannot interact with database table')
            print('Error class:', sys.exc_info()[0])
            print('Error code :', sys.exc_info()[1])
            print('Statement :', stmt_x)
            print('host       :', db_host)
            print('port       :', db_port)
            print('user       :', db_user)
            print('passwd     :', db_password)
            print('database   :', db_database)
            print('table      :', db_table)

            sys.exit(2)

        if verbose_level > 2:
            print("db_val:", self.db_val_x)

    def create_database(self, db_all, verbose_level):

        db_database = db_all[5]

        # create database ;
        print('CREATE DATABASE', db_database)
        var = input('Enter yes: ')
        if var == 'yes':
            stmt = 'CREATE DATABASE IF NOT EXISTS ' + db_database
            if verbose_level > 1:
                print(stmt)
            self.db_interaction(db_all, stmt, 0, verbose_level)

    def write_database(self, read_items, sensor_data, sensor_dict, db_all, verbose_level):
        json_body = []
        db_table = db_all[4]

        if verbose_level > 1:
            print("read_items: ", read_items)  # sensor_dict = dictionary -> sensor : location
        for x in range(0, read_items):  # sensordata = sensor , temp
            dataset = sensor_data[x]  # wert aus sensor daten holen
            sen_loc = str(sensor_dict.get(dataset[0]))  # wert der location zuordnen
            if verbose_level > 1:
                print(dataset, '-> Sensor ID:', dataset[0], 'temp.: ', dataset[1], 'location:', sen_loc)
            if sen_loc == 'None':
                print('PANIC: unknown sensor ', dataset[0])
            elif x == 0:  # verarbeitet des ersten datensatzes # todo check ?
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

        self.db_interaction(db_all, json_body, 1, verbose_level)

    def read_records(self, db_lines, db_all, db_fields_all, verbose_level, db_fields):  # todo at work

        db_table = db_all[4]

        if verbose_level > 1:
            print("read_records")

        if verbose_level > 0:
            print("show last " + str(db_lines) + " record(s) from database")

        query_count = 'SELECT * FROM ' + db_table
        if verbose_level > 1:
            print("query_count:", query_count)

        self.db_interaction(db_all, query_count, 2, verbose_level)
        results_count = self.db_val_x

        # results_count = db.query(query_count)  # holt altuelle anzahl an einträgen aus datenbank
        # db.close()

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

        self.db_interaction(db_all, stmt, 2, verbose_level)
        dbval = self.db_val_x

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
