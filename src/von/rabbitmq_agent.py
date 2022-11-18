import pika 
import cv2
import time

# def color_print(fore: Color, obj: any):
#     print( obj)

# def Warn(obj: any):
#     color_print()

class AMQ_BrokerConfig:
    host = 'voicevon.vicp.io'
    port = 5672  
    virtual_host = '/'
    uid = 'von'
    password = 'von1970'


class RabbitMqAgent():
    '''
    To learn:  What is channel indeed ?
    '''
    def __init__(self) -> None:
        self.declaed_queues=[]

    def connect_to_broker(self, broker_config: AMQ_BrokerConfig) -> None:
        self.serverConfig = broker_config
        self.reconnect_to_broker()
        # self.blocking_connection = None

    def SpinOnce(self):
        self.blocking_connection.process_data_events()

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
            print("Connected RabbitMQ broker!")
        except Exception as e:
            print(e)

    #TODO:  exchange name shall be configable.
    def Publish(self, queue_name:str, payload:str):
        # if not (queue_name in self.declaed_queues):
        #     self.channel.queue_declare(queue=queue_name)
        #     self.declaed_queues.append(queue_name)

        self.channel.basic_publish(exchange = 'twh',
                        routing_key = queue_name,
                        body = payload)

    def PublishBatch(self, queue_name:str, payloads:list):
        print("[Info] RabbitMqAgent.PublishBatch(), queue_name=, payload= ", queue_name, payloads)
        if not (queue_name in self.declaed_queues):
            self.channel.queue_declare(queue=queue_name)
            self.declaed_queues.append(queue_name)
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

    def callback_example(self, ch, method, properties, body):
        print('RabbitMqAgent::callback_example()  mq Received ' ,  method.routing_key, body)
        # self.channel.basic_ack(delivery_tag=method.delivery_tag)


    def Subscribe(self, queue_name:str, callback):
        '''
        call back examole def callback_main(self, ch, method, properties, body):
        '''
        if not (queue_name in self.declaed_queues):
            ret = self.channel.queue_declare(queue=queue_name, durable=True)
            self.declaed_queues.append(queue_name)

        var_callback = callback
        if callback is None:
            var_callback = self.callback_example
        self.channel.basic_consume(queue=queue_name, on_message_callback=var_callback, auto_ack=True)

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


def callback_example_app(self, ch, method, properties, body):
        print('RabbitMqAgent::callback_example_app()  mq Received ' ,  method.routing_key, body)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == '__main__':
    g_amq = RabbitMqAgent()
    amq_broke_config = AMQ_BrokerConfig()
    g_amq.connect_to_broker(amq_broke_config)

    img = cv2.imread("nocommand.jpg")
    g_amq.publish_cv_image("test" , img)

    g_amq.Subscribe(queue_name='twh_221109_request',callback=None )
    while True:
        g_amq.SpinOnce()
    