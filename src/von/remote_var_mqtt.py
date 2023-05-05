from von.mqtt_agent import g_mqtt, g_mqtt_broker_config


class RemoteVar_mqtt():
    def __init__(self, mqtt_topic: str, default_value):
        self.__mqtt_topic = mqtt_topic
        self.__value = default_value
        self.__rx_buffer_has_been_renewed_flag = False
        g_mqtt.publish(mqtt_topic, default_value)
        g_mqtt.append_on_received_message_callback(self.__on_mqtt_agent_received_message)
        g_mqtt.subscribe(mqtt_topic)

    def set(self, new_value):
        if new_value != self.__value:
            self.__value = new_value
            g_mqtt.publish(self.__mqtt_topic, new_value)
            self.__rx_buffer_has_been_renewed_flag = False

    def get(self):
        self.__rx_buffer_has_been_renewed_flag = False
        return self.__value
            
    def __on_mqtt_agent_received_message(self, mqtt_message_topic, mqtt_message_payload):
        if mqtt_message_topic == self.__mqtt_topic:
            self.__value = mqtt_message_payload
            self.__rx_buffer_has_been_renewed_flag = True

    def rx_buffer_has_been_renewed(self) -> bool:
        return self.__rx_buffer_has_been_renewed_flag


    # def set_callback_on_sync_to_local(self, callback):
    #     '''
    #     This is optional , if the app want to get local update informing immediately.
    #     '''
    #     self.__on_copy_to_local_callback = callback


    # def Copy_LocalToRemote(self):
    #     if self.local_value != self.remote_value:
    #         g_mqtt.publish(self.__mqtt_topic, self.local_value)

    # def Copy_RemoteToLocal(self):
    #     self.local_value = self.remote_value
    #     if self.__on_copy_to_local_callback != None:
    #         self.__on_copy_to_local_callback()
    


if __name__ == "__main__":

    g_mqtt.connect_to_broker(g_mqtt_broker_config)
    while not g_mqtt.paho_mqtt_client.is_connected():
        pass
    print("connected to mqtt broker.......")


    test_id = 3
    if test_id == 1:
        # put this line to anywhere.
        g_mqtt.publish('test/auto_sync/age', 6)
        print("check publishing result with  MQTT.fx Ver1.7.1 ,  Quit this with Ctrl+C")
        while True:
            pass
    
    if test_id == 2:
        var_hello =  RemoteVar_mqtt(mqtt_topic='test/auto_sync/hello', default_value='hello')
        
        # print ('default value=', var_hello.default_value)
        print ('remote value=', var_hello.remote_value)
        var_hello.Copy_LocalToRemote()
        var_hello.auto_copy_to_local=True
        print("Instruction 1/2: With any MQTT client, publish a message :  topic='test/auto_sync/hello', payload='aaabbb'")
        while var_hello.local_value == 'hello':
            pass
        print (var_hello.local_value)
        print("Instruction 2/2: Watch this topic,  Run this tester again, should see the payload becomes default value")

    if test_id == 3:
        ir_state = RemoteVar_mqtt(mqtt_topic="twh/" + str(221109) + "/ir_state",  default_value="unknown")
        while True:
            print (ir_state.remote_value)
        
