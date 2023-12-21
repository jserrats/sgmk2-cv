from paho.mqtt import client as mqtt_client

broker = "mqtt.jserrats.xyz"
port = 1883
client_id = "sgmk2-controller"


class SGMk2:
    _rof_values = [60, 200, 400]

    def __init__(self):
        self.client = self.connect_mqtt()
        self.laser = False
        self.rof = 0
        self.autoaim = False
        
    def alert(self):
        self.client.publish("sgmk2/alert", "1")
        self.client.loop()
        
    def get_rof_value(self):
        return self._rof_values[self.rof]

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def flywheel(self, value):
        if value:
            self.client.publish("sgmk2/flywheel", "on")
        else:
            self.client.publish("sgmk2/flywheel", "off")

        self.client.loop()

    def shooting(self, value):
        if value:
            self.client.publish("sgmk2/shoot", "on")
        else:
            self.client.publish("sgmk2/shoot", "off")
        self.client.loop()

    def pan_rel(self, value):
        self.client.publish("sgmk2/pan/relative", value)
        self.client.loop()

    def tilt_rel(self, value):
        self.client.publish("sgmk2/tilt/relative", value)
        self.client.loop()

    def _set_rof(self, value):
        self.client.publish("sgmk2/rof", value)
        self.client.loop()

    def switch_rof(self):
        self.rof = (self.rof + 1) % 3
        self._set_rof(self._rof_values[self.rof])

    def toggle_laser(self):
        if self.laser:
            self.client.publish("sgmk2/laser", "on")
        else:
            self.client.publish("sgmk2/laser", "off")
        self.client.loop()
        self.laser = not self.laser
