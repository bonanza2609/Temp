from pyownet import protocol
import sys


version = 1.1


class SensorGateway:

    @staticmethod
    def version():
        print(str("version_sensor_gateway: " + str(version)))

    def __init__(self):
        self.sensor_list = None
        self.ow_proxy = None
        self.sensor_type = None
        self.vdd = None
        self.vad = None
        self.temp = None
        self.hum_2 = None
        self.hum = None
        self.value = None

    def temp_connect(self, temp_all):

        temp_host = temp_all[0]
        temp_port = temp_all[1]

        try:
            self.ow_proxy = protocol.proxy(temp_host, temp_port)

        except IOError:
            print("PANIC - cannot connect to sensor's")
            print('Error class:', sys.exc_info()[0])
            print('Error code :', sys.exc_info()[1])
            print('host       :', temp_host)
            print('port       :', temp_port)
            sys.exit(2)

        return ()

    def get_sensor_list(self, temp_all):

        self.temp_connect(temp_all)

        self.sensor_list = self.ow_proxy.dir()

    def _sensor_type(self, sensor_slave):

        self.sensor_type = self.ow_proxy.read(sensor_slave + "type").decode()

    def _sensor_ds2438(self, sensor_slave, sensor_slave_dict_offset, verbose_level):

        self.vdd = float(self.ow_proxy.read(sensor_slave + "VDD"))
        self.vad = float(self.ow_proxy.read(sensor_slave + "VAD"))
        self.temp = float(self.ow_proxy.read(sensor_slave + "temperature"))
        self.hum_2 = float(self.ow_proxy.read(sensor_slave + "humidity"))  # for testing
        self.hum = ((self.vad / self.vdd) - 0.16) / 0.00627 * (1.0546 - 0.00216 * self.temp)

        sen_off = str(sensor_slave_dict_offset.get(sensor_slave))  # assign the offset to the sensor
        if verbose_level > 1:
            print(sensor_slave, '-> Sensor ID:', sensor_slave, 'Offset:', sen_off)
        if sen_off == 'None':
            print('PANIC: unknown sensor ', sensor_slave)

        self.value = round(float(self.hum), 3) + float(sen_off)

        if verbose_level > 1:
            print("VDD:      ", self.vdd)
            print("VAD:      ", self.vad)
            print("temp:     ", self.temp)
            print("humidity_calc: ", self.hum)
            print("humidity_value: ", self.hum_2)
            print("offset:   ", sen_off)
            print("value:    ", self.value)

    def _sensor_ds18x20(self, sensor_slave, sensor_slave_dict_offset, verbose_level):

        self.temp = float(self.ow_proxy.read(sensor_slave + "temperature"))

        sen_off = str(sensor_slave_dict_offset.get(sensor_slave))  # assign the offset to the sensor
        if verbose_level > 1:
            print(sensor_slave, '-> Sensor ID:', sensor_slave, 'Offset:', sen_off)
        if sen_off == 'None':
            print('PANIC: unknown sensor ', sensor_slave)

        self.value = float(self.temp) + float(sen_off)

        if verbose_level > 1:
            print("temp:   ", self.temp)
            print("offset: ", sen_off)
            print("value:  ", self.value)
