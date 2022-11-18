import paho.mqtt.client as mqtt
import cv2
import logging

from von.singleton import Singleton
from von.terminal_font import TerminalFont


class MQTT_ConnectionConfig:
    broker = 'voicevon.vicp.io'
    port = 1883
    uid = ''
    password = ''
    client_id = ''

class MqttAutoSyncVar():
    def __init__(self, mqtt_topic: str, default_value: any , var_data_type='string'):
        self.mqtt_topic = mqtt_topic
        self.var_data_type = var_data_type
        self.default_value = default_value
        self.remote_value = None
        self.local_value = default_value


class MqttHelper(metaclass=Singleton):

    def __init__(self):
        # super(MqttHelper, self).__init__()
        self.paho_mqtt_client = None
        # self.paho_mqtt_client = mqtt
        # self.paho_mqtt_client = mqtt.Client(client_id)  # create new instance

        self.__YELLOW = TerminalFont.Color.Fore.yellow
        self.__GREEN = TerminalFont.Color.Fore.green
        self.__RED = TerminalFont.Color.Fore.red
        self.__RESET = TerminalFont.Color.Control.reset
        # self.mqtt_system_turn_on = True
        self.__on_message_callbacks = []
        self.__configable_vars = []
        self.__counter = 0

    def _on_connect(self, client, userdata, flags, rc):
        '''
        this is a callback from paho.matt.client, when it connected to the broker.
        '''
        if rc == 0:
            print(self.__GREEN + "MQTT connected OK. Start subscribe.  Returned code=" + self.__RESET,rc)
            self.auto_subscribe()
        else:
            print("Bad connection Returned code= ", rc)      

    def connect_to_broker(self, config:MQTT_ConnectionConfig) -> mqtt.Client:
        self.paho_mqtt_client = mqtt.Client(config.client_id)  # create new instance
        self.paho_mqtt_client.on_connect = self._on_connect     # binding call back function 
        self.paho_mqtt_client.username_pw_set(username=config.uid, password=config.password)
        self.paho_mqtt_client.connect(config.broker, port=config.port)
        if self.paho_mqtt_client.is_connected():
            print(self.__GREEN + '[Info]: MQTT has connected to: %s' % config.broker + self.__RESET)
        else:
            print(self.__RED + '[Warn]: MQTT has NOT!  connected to: %s, Is trying auto connect backgroundly.' % config.broker + self.__RESET)

        self.paho_mqtt_client.on_message = self.__on_message
        self.__do_debug_print_out = False
        #self.paho_mqtt_client.loop_forever()
        self.paho_mqtt_client.loop_start()
        # self.paho_mqtt_client.loop_stop()
        return self.paho_mqtt_client

    def append_on_message_callback(self, callback, do_debug_print_out=False):
        '''
        will call back on received any message.
        Says not invoved to topic. 
        '''
        self.__on_message_callbacks.append(callback)
        self.__do_debug_print_out = do_debug_print_out

    def append_configable_var(self, var):
        self.__configable_vars.append(var)

    def subscribe(self, topic, qos=0):
        self.paho_mqtt_client.subscribe(topic, qos)

    def subscribe_with_var(self, var, qos=1, space_len=0):
        '''
        Search all members of var and childrens
        if the member(or child, grand child)'s type is 'mqtt_configableItem'
        subscribe it by the 'topic' of that member. 
        '''
        # TODO: remove build in methods
        if space_len / 8 >= 3:
            return
        #self.__counter += 1
        #print('oooo', self.__counter,var)

        target_type_name = 'MqttAutoSyncVar'
        for this_item in dir(var):
            if this_item[:1] != '_':
                attr = getattr(var,this_item)
                type_name =type(attr).__name__
                # space = ' ' * space_len
                if type_name == target_type_name:
                    # For better understanding, we rename attr.
                    configable_item = attr  
                    # print ('aaaa', space + configable_item, type_name)
                    for type_value_topic in dir(configable_item):
                        # print('bbbb',type_value_topic)
                        if type_value_topic == 'topic':
                            topic_string = getattr(configable_item,type_value_topic)
                            # print('cccc', type_value_topic,topic_string)
                            self.paho_mqtt_client.subscribe(topic_string,qos)
                            print('MQTT subscribed: Topic= ', topic_string)
                else:
                    self.subscribe_with_var(attr, qos, space_len + 4)

    def auto_subscribe(self, qos=1, space_len=0):
        '''
        call append_configable_var() in advance.
        '''
        # target_type_name = 'MqttAutoSyncVar'

        for var in self.__configable_vars:
            self.subscribe_with_var(var)

    def update_leaf_by_topic(self, root_var, topic, payload, space_len=0):
        '''
        Search all members of var and childrens
        if the member(or child, grand child)'s type is 'mqtt_configableItem', 
            and the topic_string is wanted,
        update the value of that member  to  payload. 
        '''
        if space_len / 8 >= 3:
            return
        #self.__counter += 1
        #print(self.__counter, root_var)
        target_type_name = 'MqttAutoSyncVar'
        for this_item in dir(root_var):
                if this_item[:1] != '_':
                    attr = getattr(root_var,this_item)
                    type_name =type(attr).__name__
                    # space = ' ' * space_len

                    if type_name == target_type_name:
                        # For better understanding, we rename attr.
                        configable_item = attr  
                        # print ('aaaa', space + configable_item, type_name)
                        for type_value_topic in dir(configable_item):
                            # print('bbbb',type_value_topic)
                            if type_value_topic == 'topic':
                                topic_string = getattr(configable_item,type_value_topic)
                                # print('cccc', type_value_topic,topic_string)
                                if topic_string == topic:
                                    # print('ffff',type_value_topic,topic_string)
                                    if topic_string == topic:
                                        # print('RRRRRRRRRRRR', configable_item, type_value_topic, value)
                                        #TODO: type checking here.
                                        setattr(configable_item,'value',payload)
                                        print('Configable item is updated from MQTT-server, topic=%s, value=', topic, payload)
                    else:
                        self.update_leaf_by_topic(attr, topic, payload, space_len + 8)

    def update_from_topic(self, topic, payload, space_len=3):
        '''
        call append_configable_var() in advance.
        '''
        self.__counter =0
        for var in self.__configable_vars:
           self.update_leaf_by_topic(var, topic, payload)
        print('======================================== update_from_topic() is Done!')
    
    def __on_message(self, client, userdata, message):
        #self.__do_debug_print_out = True
        if self.__do_debug_print_out:
            #print("MQTT message received ", str(message.payload.decode("utf-8")))
            print("MQTT message topic=", message.topic)
            print('MQTT message payload=', message.payload)
            print("MQTT message qos=", message.qos)
            print("MQTT message retain flag=", message.retain)
        payload = str(message.payload.decode("utf-8"))
        #print('ppppppppppppppppppppppppp',topic, payload)
        #Solution A:
        for invoking in self.__on_message_callbacks:
            invoking(message.topic, payload)
        #Solution B:
        #logging.info('payload %s'oad)
        self.update_from_topic(message.topic, payload)
    
    def publish_init(self):
        #  traverse Json file, publish all elements to broker with default values
        pass
    
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
    

g_mqtt = MqttHelper()

if __name__ == "__main__":
    # class mqtt_config_test:
    #     right = MqttAutoSyncVar(mqtt_topic='gobot/test/right', default_value=1, var_data_type='string')
    #     left = MqttAutoSyncVar('gobot/test/left',2)
    #     hello = MqttAutoSyncVar('gobot/test/hello','Hello World')



    # put this line to your system_setup()
    config = MQTT_ConnectionConfig()
    config.broker = 'voicevon.vicp.io'
    config.port = 1883
    config.uid = 'von'
    config.password = 'von1970'
    config.client_id ='win_2211180921'
    g_mqtt.connect_to_broker(config)
    while not g_mqtt.paho_mqtt_client.is_connected():
        pass
    print("connected to mqtt broker.......")


    test_id = 2
    if test_id == 1:
        # put this line to anywhere.
        g_mqtt.publish('test/auto_sync/age', 6)
        print("check publishing result with  MQTT.fx Ver1.7.1 ,  Quit this with Ctrl+C")
        while True:
            pass
    
    if test_id == 2:
        var_hello =  MqttAutoSyncVar(mqtt_topic='test/auto_sync/hello', default_value='hello', var_data_type='str')
        g_mqtt.append_configable_var(var_hello)
        print (var_hello.default_value)
        print (var_hello.remote_value)

