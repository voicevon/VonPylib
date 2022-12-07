from von.amq_agent import  g_amq, g_amq_broke_config
from von.mqtt_agent import g_mqtt,g_mqtt_broker_config

class AmqMqtt_Bridge():
    def __init__(self, queue_name, mqtt_topic) -> None:
        g_amq.Subscribe(queue_name=queue_name)
        g_amq.process_data_events()
        self.amq_queue_name = queue_name
        self.amq_payload = g_amq.fetch_message_payload(self.amq_queue_name)

        self.mqtt_topic_feed = mqtt_topic
        g_mqtt.publish(self.mqtt_topic_feed, self.amq_payload)

        self.mqtt_topic_feedback = mqtt_topic + '/fb'
        g_mqtt.subscribe(self.mqtt_topic_feedback)
        # self.mqtt_feedback_message = None

    def spin_once(self):
        feedback_payload = g_mqtt.RxBuffer.FetchPayload(self.mqtt_topic_feedback)
        if feedback_payload == self.amq_payload:
            # feed a new message out, This message is come from amq
            new_payload = g_amq.fetch_message_payload(self.amq_queue_name)
            if new_payload is not None:
                print("new_payload=", new_payload)
                g_mqtt.publish(self.mqtt_topic_feed, new_payload)
                self.amq_payload = new_payload


class AmqMqtt_Bridges():
    def __init__(self) -> None:
        self.all_bridges = [AmqMqtt_Bridge('test','test')]


    def Append(self, amq_queue_name:str):
        '''
        amq_queue_name should not contain '_'
        '''
        mqtt_publish_topic = amq_queue_name.replace("_", "/")
        new_bridge = AmqMqtt_Bridge(amq_queue_name, mqtt_publish_topic)
        self.all_bridges.append(new_bridge)

    def spin_once(self):
        for bridge in self.all_bridges:
            bridge.spin_once()

if __name__ == '__main__':
    g_amq.connect_to_broker(g_amq_broke_config)
    g_mqtt.connect_to_broker(g_mqtt_broker_config)    
    while not g_mqtt.paho_mqtt_client.is_connected():
        pass
    print("connected to mqtt broker.......")

    a = AmqMqtt_Bridges()
    a.Append('twh_221109_gcode','twh/221109/gcode')
    while True:
        g_amq.process_data_events()
        a.spin_once()

    # s =  AmqMqtt_Bridge('twh_221109_gcode', 'twh/221109/gcode_feed')
    # while True:
    #     g_amq.process_data_events()
    #     s.spin_once()