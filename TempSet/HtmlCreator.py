from .Database import Influx
import sys


class HtmlCreator(Influx):

    def __init__(self):
        super(HtmlCreator, self).__init__()

    def write_html_single(self, file_name, db_all, db_fields_all,
                          verbose_level, db_fields, web_alert_dict, web_field_dict):

        if verbose_level > 1:
            print("read database")
        self.read_records(1, db_all, db_fields_all, verbose_level, db_fields)
        # dataset = read_records(1, db_all, db_fields_all, verbose_level, db_fields)
        if verbose_level > 3:
            print("Dataset-(html): ", self.dataset)

        self.write_html(file_name, self.dataset, verbose_level, db_fields, web_alert_dict, web_field_dict)

    @staticmethod
    def write_html(file_name, dataset, verbose_level, db_fields, web_alert_dict, web_field_dict):

        if verbose_level > 0:
            print("create html: ", file_name)

        if verbose_level > 2:
            print("file_name: ", file_name)
            print("dataset: ", dataset)
            print("db_fields: ", db_fields)
            print("web_alert_dict: ", web_alert_dict)
            print("web_field_dict: ", web_field_dict)

        try:
            with open(file_name, "w") as f:
                f.write("<!DOCTYPE html>" + "\n")
                f.write("<html>" + "\n")
                f.write(" <head>" + "\n")
                f.write("  <title>Temperatur</title>" + "\n")
                f.write("  <link rel='stylesheet' href='./temp-style.css' />" + "\n")
                f.write(" </head>" + "\n")
                f.write(" <body>" + "\n")
                date_time_string = dataset.get("time")
                f.write("  <h3>Zeit in UTC:  " + str(date_time_string) + "</h3>" + "\n")
                if verbose_level > 1:
                    print("date written html: ", str(date_time_string))
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

        except IOError:
            print("Error: can't open file " + file_name + " for writing")
            print("Please check if directory is existing")
            print('Error class:', sys.exc_info()[0])
            print('Error code :', sys.exc_info()[1])
