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

class MqttConfigableItem():
    topic = ''
    type = ''
    value = ''

    def __init__(self,topic,value,type='string'):
        self.topic = topic
        self.type = type
        self.value = value


class MqttHelper(metaclass=Singleton):
# class MqttHelper(mqtt.Client, metaclass=Singleton):

    def __init__(self):
        # super(MqttHelper, self).__init__()
        self.__is_connected = False
        self.client = None
        # self.client = mqtt
        # self.client = mqtt.Client(client_id)  # create new instance

        self.__YELLOW = TerminalFont.Color.Fore.yellow
        self.__GREEN = TerminalFont.Color.Fore.green
        self.__RED = TerminalFont.Color.Fore.red
        self.__RESET = TerminalFont.Color.Control.reset
        # self.mqtt_system_turn_on = True
        self.__on_message_callbacks = []
        self.__configable_vars = []
        self.__counter = 0

    def on_connect(self, client, userdata, flags,rc):
        '''
        rc == return code.
        '''
        if rc==0:
            self.connected_flag=True #set flag
            logging.info(self.__GREEN + "MQTT connected OK. Start subscribe.  Returned code=" + self.__RESET,rc)
            #client.subscribe(topic)
            self.auto_subscribe()
        else:
            print("Bad connection Returned code= ",rc)      

    # def connect_to_broker(self, client_id, broker, port, uid, psw):
    def connect_to_broker(self, config:MQTT_ConnectionConfig):
        self.client = mqtt.Client(config.client_id)  # create new instance
        self.client.on_connect = self.on_connect  # binding call back function 
        self.client.username_pw_set(username=config.uid, password=config.password)
        self.client.connect(config.broker, port=config.port)
        if self.client.is_connected():
            print(self.__GREEN + '[Info]: MQTT has connected to: %s' % config.broker + self.__RESET)
        else:
            print(self.__RED + '[Warn]: MQTT has NOT!  connected to: %s, Is trying auto connect backgroundly.' % config.broker + self.__RESET)

        self.client.on_message = self.__on_message
        self.__do_debug_print_out = False
        #self.client.loop_forever()
        self.client.loop_start()
        # self.client.loop_stop()
        return self.client

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
        self.client.subscribe(topic, qos)
    


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

        target_type_name = 'MqttConfigableItem'
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
                            self.client.subscribe(topic_string,qos)
                            print('MQTT subscribed: Topic= ', topic_string)
                else:
                    self.subscribe_with_var(attr, qos, space_len + 4)

    def auto_subscribe(self, qos=1, space_len=0):
        '''
        call append_configable_var() in advance.
        '''
        # target_type_name = 'MqttConfigableItem'

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
        target_type_name = 'MqttConfigableItem'
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
            self.client.publish(topic, img_pub, retain=retain)

    def publish_file_image(self, topic, file_name, retain=True):
        with open(file_name, 'rb') as f:
            byte_im = f.read()
        self.client.publish('sower/img/bin',byte_im )

    def publish(self, topic, value):
        self.client.publish(topic, value, qos=2, retain =True)
    

g_mqtt = MqttHelper()

if __name__ == "__main__":
    class mqtt_config_test:
        right = MqttConfigableItem('gobot/test/right',1)
        left = MqttConfigableItem('gobot/test/right',2)
        hello = MqttConfigableItem('gobot/test/hello','Hello World')



    # put this line to your system_setup()
    config = MQTT_ConnectionConfig()
    config.uid = ''
    config.password = ''
    g_mqtt.connect_to_broker(config)
    test_id =2
    if test_id ==1:
        # put this line to anywhere.
        g_mqtt.publish('test/test1/test2', 1)
    
    if test_id ==2:
        g_mqtt.append_configable_var(mqtt_config_test)
        g_mqtt.update_from_topic(mqtt_config_test,'gobot/test/hello', 'aaaabbbb')
        print (mqtt_config_test.hello.value)

