from von.mqtt_agent import g_mqtt, g_mqtt_broker_config


class MqttAutoSyncVar():
    def __init__(self, mqtt_topic: str, default_value: any , var_data_type='string'):
        self.mqtt_topic = mqtt_topic
        self.var_data_type = var_data_type
        self.default_value = default_value
        self.remote_value = None
        self.local_value = default_value
        self.auto_sync_to_local = True
        self.auto_sync_to_remote = True
        self.__on_sync_to_local_callback = None
        g_mqtt.subscribe(self.mqtt_topic)
        g_mqtt.append_on_received_message_callback(self.__on_mqtt_agent_received_message)

    def set_callback_on_sync_to_local(self, callback):
        '''
        This is optional , if the app want to get local update informing immediately.
        '''
        self.__on_sync_to_local_callback = callback
    
    def __on_mqtt_agent_received_message(self, mqtt_message_topic, mqtt_message_payload):
        if mqtt_message_topic == self.mqtt_topic:
            self.remote_value = mqtt_message_payload
            if self.auto_sync_to_local:
                self.Sync_RemoteToLocal()



    def Sync_LocalToRemote(self):
        if self.local_value != self.remote_value:
            g_mqtt.publish(self.mqtt_topic, self.local_value)

    def Sync_RemoteToLocal(self):
        self.local_value = self.remote_value
        if self.__on_sync_to_local_callback != None:
            self.__on_sync_to_local_callback()
    


if __name__ == "__main__":

    g_mqtt.connect_to_broker(g_mqtt_broker_config)
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
        
        print (var_hello.default_value)
        print (var_hello.remote_value)
        var_hello.Sync_LocalToRemote()
        print("Test Instruction: With any MQTT client, publish a message :  topic='test/auto_sync/hello', payload='aaabbb'")
        while var_hello.local_value == 'hello':
            pass
        print (var_hello.local_value)

