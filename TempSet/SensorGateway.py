from pyownet import protocol
import sys


version = 1.0


class SensorGateway:

    @staticmethod
    def version():
        print(str("version_sensor_gateway:" + str(version)))

    def __init__(self):
        self.sensor_list = None
        self.ow_proxy = None

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
