from influxdb import InfluxDBClient
import sys


class Influx:
    def __init__(self):
        self.db = None
        self.db_val_x = None
        self.dataset = []

    def _db_connect(self, db_all, no_db, verbose_level):

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

    def db_interaction(self, db_all, stmt_x, db_level, verbose_level):

        db_host = db_all[0]
        db_port = db_all[1]
        db_user = db_all[2]
        db_password = db_all[3]
        db_table = db_all[4]
        db_database = db_all[5]

        if verbose_level > 2:
            print("stmt", stmt_x)

        try:
            if db_level == 0:  # create database
                self._db_connect(db_all, 1, verbose_level)  # open connection without database
                self.db.create_database(stmt_x)
                self.db.close()
            elif db_level == 1:  # write into database
                self._db_connect(db_all, 0, verbose_level)  # open connection with database
                self.db.write_points(stmt_x)
                self.db.close()
            elif db_level == 2:  # read from database
                self._db_connect(db_all, 0, verbose_level)  # open connection with database
                self.db_val_x = self.db.query(stmt_x)
                self.db.close()
            elif db_level == 3:  # kill table from database
                self._db_connect(db_all, 0, verbose_level)  # open connection with database
                self.db.drop_measurement(stmt_x)
                self.db.close()
            elif db_level == 4:  # open database
                self._db_connect(db_all, 0, verbose_level)  # open connection with database
            elif db_level == 5:  # close database
                self.db.close()
            elif db_level == 6:  # read from database without close Database
                self.db_val_x = self.db.query(stmt_x)

            else:
                print("unknown db_level for stmt: ", stmt_x)

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
            if sen_loc:
                json_body.append(
                    {
                        "measurement": db_table,
                        "fields": {
                            sen_loc: float(dataset[1])
                        }
                    })

            else:
                print('PANIC: unknown sensor ', dataset[0])

        print("0-script")
        if verbose_level > 1:
            print(json_body)

        self.db_interaction(db_all, json_body, 1, verbose_level)

    def read_records(self, db_lines, db_all, db_fields_str, verbose_level, db_fields):
        loop = True

        db_table = db_all[4]

        if verbose_level > 1:
            print("read_records")

        if verbose_level > 0:
            print("show last " + str(db_lines) + " record(s) from database")

        self.db_interaction(db_all, "X", 4, verbose_level)
        db_time_value = 10
        db_time_suffix = 'm'
        db_t_count = 0
        db_time_max = 104

        while loop:
            db_time = str(db_time_value) + db_time_suffix
            query_count = 'SELECT * FROM ' + db_table + ' WHERE TIME > now() - ' + db_time
            self.db_interaction(db_all, query_count, 6, verbose_level)
            if self.db_val_x:
                db_t_count = len(list(self.db_val_x)[0])

            if verbose_level > 1:
                print("db_time", db_time)
                print("db_time_value", db_time_value)
                print("db_time_suffix", db_time_suffix)
                print("db_t_count", db_t_count)
                print("query_count", query_count)

            if db_t_count >= db_lines:
                loop = False
            else:
                if db_time_value <= 50 and db_time_suffix == 'm':
                    db_time_value += 10
                elif db_time_value == 60 and db_time_suffix == 'm':
                    db_time_value = 1
                    db_time_suffix = 'h'

                elif db_time_value <= 23 and db_time_suffix == 'h':
                    db_time_value += 1
                elif db_time_value == 24 and db_time_suffix == 'h':
                    db_time_value = 1
                    db_time_suffix = 'd'

                elif db_time_value <= 6 and db_time_suffix == 'd':
                    db_time_value += 1
                elif db_time_value == 7 and db_time_suffix == 'd':
                    db_time_value = 1
                    db_time_suffix = 'w'

                elif db_time_value == db_time_max and db_time_suffix == 'w':
                    print("time value :", db_time)
                    print("Break Loop !")
                    break

                elif db_time_value >= 1 and db_time_suffix == 'w':
                    db_time_value += 1

                else:
                    print("db_time_value unknown break")
                    break

        self.db_interaction(db_all, "X", 5, verbose_level)

        if verbose_level > 1:
            print("db_value:", self.db_val_x)

        if self.db_val_x:
            if verbose_level > 0:
                print('Datum                             , ' + db_fields_str)
                print(
                    '-------------------------------------------------------'
                    '-------------------------------------------------------')

            if verbose_level > 1:
                print("db_lines: ", db_lines)
                print("db_t_count: ", db_t_count)
                print("db_fields: ", db_fields)
                print("db_fields_str: ", db_fields_str)

            if db_lines > db_t_count:
                count = db_t_count
            else:
                count = db_lines

            for x in range(0, count):
                output = []
                self.dataset = list(list(self.db_val_x)[0])[x]
                if verbose_level > 1:
                    print(x)
                    print(self.dataset)
                field_list = self.dataset.get("time")  # read timestamp
                output.append(field_list)  # put timestamp in to output
                if verbose_level > 1:
                    print("Field: time")
                    print("Field entry:", field_list)
                for y in range(len(db_fields)):
                    field = db_fields[y]
                    field_list = self.dataset.get(field)
                    output.append(field_list)
                    if verbose_level > 1:
                        print("Field:", field)
                        print("Field entry:", field_list)
                if verbose_level > 0:
                    print(output)

        else:
            print("no records retrieved from database")
            return 0

    @staticmethod
    def clean_records(db_fields, db_all, db_fields_str, verbose_level):

        if verbose_level > 1:
            print("Verbose Level:", verbose_level)
        print("no entries can be deleted from the database use 'influx' in the console")
        print('host       :', db_all[0])
        print('port       :', db_all[1])
        print('user       :', db_all[2])
        print('passwd     :', db_all[3])
        print('database   :', db_all[4])
        print('table      :', db_all[5])
        print('field      :', db_fields)
        print('field_str  :', db_fields_str)

    def kill_db_entries(self, db_all, verbose_level):

        db_table = db_all[4]
        db_database = db_all[5]
        print('DELETE ALL ENTRIES FROM DATABASE', db_table, 'from', db_database, )
        var = input('Enter yes: ')
        if var == 'yes':
            var = input('Confirm drop Database Entries Enter yes: ')
            if var == 'yes':
                stmt = 'DELETE FROM ' + db_table + ' WHERE 1'
                if verbose_level > 1:
                    print(stmt)
                self.db_interaction(db_all, stmt, 3, verbose_level)

        else:
            print('request cancelled')
