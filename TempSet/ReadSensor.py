from .SensorGateway import SensorGateway
import sys


class ReadSensor(SensorGateway):

    sensor_type = None
    sensor_id = None
    vdd = None
    vad = None
    temp = None
    hum_2 = None
    hum = None
    value = None

    def __init__(self):
        super().__init__()
        pass
    
    def _sensor_ds2438(self, sensor_slave, sensor_slave_dict_offset, verbose_level):
        
        self.vdd = float(self.ow_proxy.read(sensor_slave + "VDD"))
        self.vad = float(self.ow_proxy.read(sensor_slave + "VAD"))
        self.temp = float(self.ow_proxy.read(sensor_slave + "temperature"))
        self.hum_2 = float(self.ow_proxy.read(sensor_slave + "humidity"))  # for testing
        self.hum = ((self.vad / self.vdd) - 0.16) / 0.00627 * (1.0546 - 0.00216 * self.temp)

        dataset = sensor_slave
        sen_off = str(sensor_slave_dict_offset.get(dataset))  # sensor dem offset zuordnen
        if verbose_level > 1:
            print(dataset, '-> Sensor ID:', dataset, 'Offset:', sen_off)
        if sen_off == 'None':
            print('PANIC: unknown sensor ', dataset)

        self.value = round(float(self.hum), 3) + float(sen_off)

        if verbose_level > 1:
            print("VDD:      ", self.vdd)
            print("VAD:      ", self.vad)
            print("temp:     ", self.temp)
            print("humidity_clac: ", self.hum)
            print("humidity_value: ", self.hum_2)
            print("offset:   ", sen_off)
            print("value:    ", self.value)
            
    def _sensor_ds18x20(self, sensor_slave, sensor_slave_dict_offset, verbose_level):
        
        self.temp = float(self.ow_proxy.read(sensor_slave + "temperature"))

        dataset = sensor_slave
        sen_off = str(sensor_slave_dict_offset.get(dataset))  # sensor dem offset zuordnen
        if verbose_level > 1:
            print(dataset, '-> Sensor ID:', dataset, 'Offset:', sen_off)
        if sen_off == 'None':
            print('PANIC: unknown sensor ', dataset)

        self.value = float(self.temp) + float(sen_off)

        if verbose_level > 1:
            print("temp:   ", self.temp)
            print("offset: ", sen_off)
            print("value:  ", self.value)

    def sensor_read(self, sensor_slave, sensor_slave_dict_offset, temp_all, verbose_level):

        self.temp_connect(temp_all)

        self.sensor_id = sensor_slave  # id of 1-wire sensor
        self.sensor_type = self.ow_proxy.read(sensor_slave + "type")  # type of 1-wire sensor
        self.sensor_type = self.sensor_type.decode()  # decode bytes of type

        try:

            if self.sensor_type == "DS2438":
                self._sensor_ds2438(sensor_slave, sensor_slave_dict_offset, verbose_level)
            else:
                self._sensor_ds18x20(sensor_slave, sensor_slave_dict_offset, verbose_level)
        except IOError:
            print("PANIC read_sensor - Cannot find file >" + sensor_slave + "< on OW Server")
            print("No sensor attached")
            print("check with > owdir")
            sys.exit(1)
