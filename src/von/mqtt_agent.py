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

class MqttAgent_ReceivedMessage():
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload
        self.updated = True
    
class MqttAgent_ReceivedDiction():
    def __init__(self) -> None:
        self.__newest_message = [MqttAgent_ReceivedMessage('','')]

    def FindItem(self, topic) -> MqttAgent_ReceivedMessage:
        for message in self.__newest_message:
            if message.topic == topic:
                return message
        return None

    def OnReceivedMessage(self, topic, payload):
        item = self.FindItem(topic)
        if item is None:
            new_message = MqttAgent_ReceivedMessage(topic, payload)
            self.__newest_message.append(new_message)
        else:
            item.payload = payload
            item.updated = True

    def has_updated_payload(self, topic) -> bool:
        item = self.FindItem(topic)
        return item.updated

    def FetchPayload(self, topic):
        item = self.FindItem(topic)
        if item is None:
            return None
        else:
            item.updated = False
            return item.payload


class MqttAgent(metaclass=Singleton):
    '''
    When received a message, There are two ways to get it:
    1.  set a __on_message_callbacks().   Note:  Not in main thread.
    2.  MqttAgent().RxBuffer.FetchPayload() 
    '''
    def __init__(self):
        self.paho_mqtt_client = None

        self.__YELLOW = TerminalFont.Color.Fore.yellow
        self.__GREEN = TerminalFont.Color.Fore.green
        self.__RED = TerminalFont.Color.Fore.red
        self.__RESET = TerminalFont.Color.Control.reset
        self.__on_message_callbacks = []
        self.__do_debug_print_out = False
        self.RxBuffer = MqttAgent_ReceivedDiction()

        

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
        is_utf_8 = False
        try:
            payload = str(message.payload.decode("utf-8"))
            is_utf_8 = True
        except:
            pass
        
        for invoking in self.__on_message_callbacks:
            if is_utf_8:
                invoking(message.topic, payload)
            else:
                invoking(message.topic, message.payload)
        self.RxBuffer.OnReceivedMessage(message.topic, message.payload)

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
        self.RxBuffer.OnReceivedMessage(topic, "")


    def publish_cv_image(self, topic, cv_image, retain=True):
        # https://blog.51cto.com/u_15088375/5845886
        # return image as mqtt message payload
        is_success, img_encode = cv2.imencode(".jpg", cv_image)
        if is_success:
            img_pub = img_encode.tobytes()
            self.paho_mqtt_client.publish(topic, img_pub, retain=retain)

    def publish_file_image(self, topic, file_name, retain=True):
        with open(file_name, 'rb') as f:
            byte_im = f.read()
        self.paho_mqtt_client.publish('sower/img/bin',byte_im )

    def publish(self, topic, payload):
        self.paho_mqtt_client.publish(topic, payload, qos=2, retain =True)
    

g_mqtt_broker_config = MQTT_BrokerConfig()
g_mqtt = MqttAgent()

if __name__ == "__main__":
    test_topic = "twh/221109/gcode_feed"
    g_mqtt.connect_to_broker(g_mqtt_broker_config)
    g_mqtt.subscribe(test_topic)
    count = 0
    while True:
        rx = g_mqtt.RxBuffer
        if rx.has_updated_payload(test_topic):
            payload = rx.FetchPayload(test_topic)
            print(count, payload)
            count += 1
        



