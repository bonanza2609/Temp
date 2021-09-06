from .SensorGateway import SensorGateway
import sys
import time


class ReadSensor(SensorGateway):

    def __init__(self):
        super().__init__()
        self.sensor_data = []
        self.sensor_type = None
        self.sensor_id = None
        self.vdd = None
        self.vad = None
        self.temp = None
        self.hum_2 = None
        self.hum = None
        self.value = None
        self.sensor_count = 0

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

    def read_sensor(self, sensor_slave, sensor_slave_dict_offset, temp_all, verbose_level):

        self.temp_connect(temp_all)

        self.sensor_id = sensor_slave  # id of 1-wire sensor
        self.sensor_type = self.ow_proxy.read(sensor_slave + "type").decode()  # type of 1-wire sensor

        try:

            if self.sensor_type == "DS2438":
                self._sensor_ds2438(sensor_slave, sensor_slave_dict_offset, verbose_level)
            elif self.sensor_type == "DS18S20" or self.sensor_type == "DS18B20":
                self._sensor_ds18x20(sensor_slave, sensor_slave_dict_offset, verbose_level)
            else:
                print("unknown Type of sensor:", self.sensor_type)
                sys.exit(1)
                
        except IOError:
            print("PANIC read_sensor - Cannot find sensor >" + sensor_slave + "< on OW Server")
            print("No sensor attached")
            print("check with > owdir")
            sys.exit(1)

    def read_sensors(self, read_level, temp_all, sensor_slaves_dict_offset, dead_lo, dead_hi,
                     error_low, error_high, verbose_level):

        self.sensor_count = 0

        self.get_sensor_list(temp_all)
        # Open 1-wire slaves list for reading

        w1_slaves = self.sensor_list

        # Print header for results table
        if verbose_level > 0:
            print('Sensor ID       |   value')
            print('------------------------------')

        # Repeat following steps with each 1-wire slave
        for w1_slave in w1_slaves:
            time.sleep(0.2)
            self.read_sensor(w1_slave, sensor_slaves_dict_offset, temp_all,  verbose_level)

            # check for faulty data
            r = 1
            r_max = 3  # max retry for faulty data
            t = 0.5  # time delay between retry add per round
            while r <= r_max:
                if dead_lo <= self.value <= dead_hi:
                    break
                else:
                    if verbose_level > 1:
                        print("Panic", self.value)
                        print(r, ". retry")
                    time.sleep(t)
                    self.read_sensor(w1_slave, sensor_slaves_dict_offset, temp_all, verbose_level)
                    r += 1
                    t += 0.5

            if verbose_level > 0:
                if self.sensor_type == 'DS2438':
                    # DS2438
                    print(str(self.sensor_id) + ' | {:5.2f} {}'.format(self.value, '%rH'))  # Print value
                elif self.sensor_type == "DS18S20" or self.sensor_type == "DS18B20":
                    print(str(self.sensor_id) + ' | {:5.3f} {}'.format(self.value, '°C'))  # Print value
                else:
                    print("unknown Type of sensor:", self.sensor_type)

            if read_level:
                if error_low <= self.value <= error_high:
                    self.sensor_data.append((self.sensor_id, self.value))  # store value in database
                    self.sensor_count += 1

        if verbose_level > 2:
            print("sensors detected: ", self.sensor_count)
            print("sensor_data: ", self.sensor_data)
