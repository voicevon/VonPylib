import pika 
import cv2
import time

class AMQ_BrokerConfig:
    host = 'voicevon.vicp.io'
    port = 5672  
    virtual_host = '/'
    uid = 'von'
    password = 'von1970'


class Amq_Message():

    def __init__(self, method, body) -> None:
        self.method = method
        self.body = body

class Amq_Subscriber():
    def __init__(self, queue_name: str, channel ) -> None:
        self.queue_name = queue_name
        self.unacked_messages = [Amq_Message(None,None)]
        self.unacked_messages.clear()

        self.channel = channel
        var_callback = self.CopyToUnackedMessage
        self.channel.basic_consume(queue=queue_name, on_message_callback=var_callback, auto_ack=False)

    def CopyToUnackedMessage(self, ch, method, properties, body):
        unacked = Amq_Message(method, body)
        self.unacked_messages.append(unacked)

    def FetchMessage(self) -> str:
        if len(self.unacked_messages) > 0:
            result = self.unacked_messages[0].body
            tag = self.unacked_messages[0].method.delivery_tag
            self.channel.basic_ack(tag)
            self.unacked_messages.pop(0)
        else:
            result = None
        return result

class AmqAgent():
    '''
    To learn:  What is channel indeed ?
    '''
    def __init__(self) -> None:
        self.subscribers=[]

    def connect_to_broker(self, broker_config: AMQ_BrokerConfig) -> None:
        self.serverConfig = broker_config
        self.reconnect_to_broker()
        self.prefeched_message = None
        self.delivery_tag = None

    def process_data_events(self, time_limit=0):
        if self.channel.connection.is_closed:
            print("AmqAgent::process_data_events()  Connection is closed. Trying to reconnect ")
            input("press any key to reconnect")
            self.reconnect_to_broker()
        self.blocking_connection.process_data_events(time_limit)

    def reconnect_to_broker(self):
        broker_config = self.serverConfig
        credentials = pika.PlainCredentials(broker_config.uid, broker_config.password)
        parameters = pika.ConnectionParameters(host=broker_config.host,
                                    port=broker_config.port,
                                    virtual_host=broker_config.virtual_host,
                                    credentials=credentials)
        try:
            print("Start to connect to RabbitMQ broker.")
            self.blocking_connection = pika.BlockingConnection(parameters)
            self.channel = self.blocking_connection.channel()
            self.channel.basic_qos(prefetch_count=10)
            print("Connected RabbitMQ broker!")
        except Exception as e:
            print(e)

    def Publish(self, exchange_name: str, queue_name: str, payload: str):
        # if not (queue_name in self.declaed_queues):
        #     self.channel.queue_declare(queue=queue_name)
        #     self.declaed_queues.append(queue_name)

        self.channel.basic_publish(exchange = exchange_name,
                        routing_key = queue_name,
                        body = payload)

    def PublishBatch(self, queue_name:str, payloads:list):
        print("[Info] RabbitMqAgent.PublishBatch(), queue_name=, payload= ", queue_name, payloads)
        # if not (queue_name in self.declaed_queues):
        #     self.channel.queue_declare(queue=queue_name)
        #     self.declaed_queues.append(queue_name)
        for pp in payloads:
            self.channel.basic_publish(exchange = '',
                            routing_key = queue_name,
                            body = pp)

    def publish_cv_image(self, queue_name:str, cv_image):
        # Convert received message into Numpy array
        # jpg = np.frombuffer(RECEIVEDMESSAGE, dtype=np.uint8)

        # # JPEG-decode back into original frame - which is actually a Numpy array
        # im = cv2.imdecode(jpg, cv2.IMREAD_UNCHANGED)
        if not (queue_name in self.declaed_queues):
            self.channel.queue_declare(queue=queue_name)
            self.declaed_queues.append(queue_name)

        is_success, img_encode = cv2.imencode(".jpg", cv_image)
        if is_success:
            img_pub = img_encode.tobytes()
            # self.client.publish(topic, img_pub, retain=retain)
            self.channel.basic_publish(exchange = '',
                        routing_key = queue_name,
                        body = img_pub)

    def __FindSubscriber(self, queue_name:str) -> Amq_Subscriber:
        for subscriber in self.subscribers:
            if subscriber.queue_name == queue_name:
                return subscriber
        return None

    def fetch_message_payload(self, queue_name:str) -> str:
        subscriber = self.__FindSubscriber(queue_name)
        if subscriber is None:
            print("no subscriber is found")
            return None
        else:
            return subscriber.FetchMessage()

    def Subscribe(self, queue_name:str):
        '''
        use fetch_message_payload() to check out message.body
        '''
        new_subscriber = Amq_Subscriber(queue_name, self.channel)
        self.subscribers.append(new_subscriber)

        # new_subscriber.channel = self.channel
        # var_callback = callback
        # if callback is None:
        #     var_callback = new_subscriber.CopyToUnackedMessage
        # new_subscriber.channel.basic_consume(queue=queue_name, on_message_callback=var_callback, auto_ack=False)

    def RabbitMQ_publish_tester(self):
        i = 0
        while True:
            self.channel.basic_publish(exchange='',
                            routing_key='gobot_x2134_house',
                            body = str(i))
            self.channel.basic_publish(exchange='',
                            routing_key='gobot_x2134_arm',
                            body = str(i))
            print(" [x] Sent ",i)
            i += 1  
            time.sleep(2)

g_amq = AmqAgent()
g_amq_broker_config = AMQ_BrokerConfig()


if __name__ == '__main__':
    g_amq.connect_to_broker(g_amq_broker_config)

    # img = cv2.imread("nocommand.jpg")
    # g_amq.publish_cv_image("test" , img)
    # g_amq_broker_config.host = 'localhost'

    g_amq.Subscribe(queue_name='twh_deposit')
    g_amq.Subscribe(queue_name='twh_withdraw')
    count = 0
    g_amq.process_data_events()
    while True:
        g_amq.process_data_events()
        # g_amq.process_data_events()
        time.sleep(0.9)
        xx = g_amq.fetch_message_payload('twh_deposit')
        # xx = ss.FetchMessage()
        if xx is not None:
            print(xx)
            time.sleep(1)

        xx = g_amq.fetch_message_payload('twh_withdraw')
        if xx is not None:
            # g_amq.process_data_events()
            if count>1:
                print("withdraw is empty................................", count)
            count =0
            # print('final fetchd.', xx)
        else:
            # print("fetched   None", count)
            count += 1
        # time.sleep(1)


    