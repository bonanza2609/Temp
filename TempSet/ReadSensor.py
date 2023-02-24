from .SensorGateway import SensorGateway
import sys
import time

version = 2.1


class ReadSensor(SensorGateway):

    @staticmethod
    def version():
        print(str("version_read_sensor: " + str(version)))

    def __init__(self, dead_lo, dead_hi, error_low, error_high):
        super().__init__()
        self.sensor_data = []
        self.sensor_id = None
        self.sensor_count = 0
        self.dead_lo = dead_lo
        self.dead_hi = dead_hi
        self.error_low = error_low
        self.error_high = error_high

    def read_sensor(self, sensor_slave, sensor_slave_dict_offset, verbose_level=1):

        self.sensor_id = sensor_slave  # id of 1-wire sensor
        self._sensor_type(sensor_slave)

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

    def read_sensors(self, read_level, temp_all, sensor_slaves_dict_offset, verbose_level=1):

        self.sensor_count = 0

        # Open 1-wire slaves list for reading
        self.get_sensor_list(temp_all)
        w1_slaves = self.sensor_list

        # Print header for results table
        if verbose_level > 0:
            print('Sensor ID       |   value')
            print('------------------------------')

        # Repeat following steps with each 1-wire slave
        for w1_slave in w1_slaves:
            time.sleep(0.2)
            self.read_sensor(w1_slave, sensor_slaves_dict_offset, verbose_level)

            # check for faulty data
            r = 1
            r_max = 3  # max retry for faulty data
            t = 0.5  # time delay between retry add per round
            while r <= r_max:
                if self.dead_lo <= self.value <= self.dead_hi:
                    break
                else:
                    if verbose_level > 1:
                        print("Panic", self.value)
                        print(r, ". retry")
                    time.sleep(t)
                    self.read_sensor(w1_slave, sensor_slaves_dict_offset, verbose_level)
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
                if self.error_low <= self.value <= self.error_high:
                    self.sensor_data.append((self.sensor_id, self.value))  # store value in database
                    self.sensor_count += 1

        if verbose_level > 2:
            print("sensors detected: ", self.sensor_count)
            print("sensor_data: ", self.sensor_data)
