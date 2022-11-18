import paho.mqtt.client as mqtt
import cv2
import logging

from von.singleton import Singleton
from von.terminal_font import TerminalFont


class MQTT_BrokerConfig:
    broker = 'voicevon.vicp.io'
    port = 1883
    uid = 'von'
    password = 'von1970'
    client_id = 'test_22111815'



class MqttAgent(metaclass=Singleton):

    def __init__(self):
        self.paho_mqtt_client = None

        self.__YELLOW = TerminalFont.Color.Fore.yellow
        self.__GREEN = TerminalFont.Color.Fore.green
        self.__RED = TerminalFont.Color.Fore.red
        self.__RESET = TerminalFont.Color.Control.reset
        self.__on_message_callbacks = []
        self.__do_debug_print_out = True

    def _on_phao_mqtt_client_connected_callback(self, client, userdata, flags, rc):
        if rc == 0:
            print(self.__GREEN + "MQTT connected OK. Start subscribe.  Returned code=" + self.__RESET,rc)
            # self.auto_subscribe()
        else:
            print("Bad connection Returned code= ", rc)      

    def __on_received_mqtt_message(self, client, userdata, message):
        '''
        When mqtt client received a message, this agent will callback many functions those care about the message.
        '''
        if self.__do_debug_print_out:
            #print("MQTT message received ", str(message.payload.decode("utf-8")))
            print("MQTT message topic=", message.topic)
            print('MQTT message payload=', message.payload)
            print("MQTT message qos=", message.qos)
            print("MQTT message retain flag=", message.retain)
        payload = str(message.payload.decode("utf-8"))
        for invoking in self.__on_message_callbacks:
            invoking(message.topic, payload)

    def connect_to_broker(self, config: MQTT_BrokerConfig) -> mqtt.Client:
        self.paho_mqtt_client = mqtt.Client(config.client_id)  # create new instance
        self.paho_mqtt_client.on_connect = self._on_phao_mqtt_client_connected_callback     # binding call back function 
        self.paho_mqtt_client.on_message = self.__on_received_mqtt_message
        self.paho_mqtt_client.username_pw_set(username=config.uid, password=config.password)
        self.paho_mqtt_client.connect(config.broker, port=config.port)
        if self.paho_mqtt_client.is_connected():
            print(self.__GREEN + '[Info]: MQTT has connected to: %s' % config.broker + self.__RESET)
        else:
            print(self.__RED + '[Warn]: MQTT has NOT!  connected to: %s, Is trying auto connect backgroundly.' % config.broker + self.__RESET)

        #self.paho_mqtt_client.loop_forever()
        self.paho_mqtt_client.loop_start()
        # self.paho_mqtt_client.loop_stop()
        return self.paho_mqtt_client

    def append_on_received_message_callback(self, callback, do_debug_print_out=False):
        '''
        will call back on received any message.
        Says not invoved to topic. 
        '''
        self.__on_message_callbacks.append(callback)
        self.__do_debug_print_out = do_debug_print_out

    def subscribe(self, topic, qos=0):
        self.paho_mqtt_client.subscribe(topic, qos)

    def publish_cv_image(self, topic, cv_image, retain=True):
      # return image as mqtt message payload
        is_success, img_encode = cv2.imencode(".jpg", cv_image)
        if is_success:
            img_pub = img_encode.tobytes()
            self.paho_mqtt_client.publish(topic, img_pub, retain=retain)

    def publish_file_image(self, topic, file_name, retain=True):
        with open(file_name, 'rb') as f:
            byte_im = f.read()
        self.paho_mqtt_client.publish('sower/img/bin',byte_im )

    def publish(self, topic, value):
        self.paho_mqtt_client.publish(topic, value, qos=2, retain =True)
    

g_mqtt_broker_config = MQTT_BrokerConfig()
g_mqtt = MqttAgent()



