from von.mqtt.remote_var_mqtt import RemoteVar_mqtt, g_mqtt
from von.logger import Logger
import json
import cv2
import numpy
import pytesseract
from PIL import Image #pip install pillow

# class OcrWindowConfig:
#     def __init__(self, kvm_node_name, app_window_name) -> None:
#         self.__config = {}
#         # screen image
#         self.__config['mqtt_topic_of_screen_image'] = "ocr/kvm/" + kvm_node_name + "/screen_image"

#         # marker image
#         mqtt_topic_of_appwindow_marker_image = "ocr/app_window/" + app_window_name + "/marker"
#         marker_getter = RemoteVar_mqtt(mqtt_topic_of_appwindow_marker_image, None)
#         while not marker_getter.rx_buffer_has_been_updated():
#             pass
#         np_array = numpy.frombuffer(marker_getter.get(), dtype=numpy.uint8) 
#         self.__config['marker_image'] = cv2.imdecode(np_array, flags=1)

#         # areas and positions
#         mqtt_topic_of_position_config = "ocr/app_window/" + app_window_name + "/areas"
#         positions_getter = RemoteVar_mqtt(mqtt_topic_of_position_config, None)
#         while not positions_getter.rx_buffer_has_been_updated():
#             pass
#         self.__config['areas'] = json.loads( positions_getter.get())

#     def load(self):

#     def save_to_mqtt(self)
#         node_config = OcrFactory.CreateKvmNodeConfig(node_name)
#         payload = json.dumps(node_config)

#         mqtt_config = RemoteVar_mqtt(node_config['my_topic'], payload)
#         while not  mqtt_config.rx_buffer_has_been_updated():
#             pass

class OcrWindow:
    def __init__(self, kvm_node_name:str, app_window_name:str, auto_init_config=False) -> None:
        '''
        '''
        self.__image_getter = RemoteVar_mqtt("ocr/kvm/" + kvm_node_name + "/screen_image", None)
        self.__config_getter = RemoteVar_mqtt("ocr/" + app_window_name + "/config", None)
        self.__mqtt_topic_of_marker_image = "ocr/" + app_window_name + "/marker_image"
        if auto_init_config:
            # create default config, and save it to mqtt
            self.__config = {}
            self.__config['areas'] = {}
            self.__marker_image = numpy.zeros((100, 100, 3), numpy.uint8)
            self.__save_config()
            g_mqtt.publish_cv_image(self.__mqtt_topic_of_marker_image, self.__marker_image)
            
        else:
            # load from history, here is mqtt
            while not self.__config_getter.rx_buffer_has_been_updated():
                pass
            self.__config = json.loads(self.__config_getter.get())
            # marker image
            
            marker_getter = RemoteVar_mqtt(self.__mqtt_topic_of_marker_image, None)
            while not marker_getter.rx_buffer_has_been_updated():
                pass
            np_array = numpy.frombuffer(marker_getter.get(), dtype=numpy.uint8) 
            self.__marker_image = cv2.imdecode(np_array, flags=1)

        width, height = 1024, 768
        self.__frame = numpy.zeros((width, height,3), numpy.uint8)

    def update_areas(self, areas_json):
        '''
        areas will be updated to config,  and config will be saved to mqtt-broker
        '''
        self.__config["areas"] = areas_json
        self.__save_config()

    def __save_config(self):
        payload = json.dumps(self.__config)
        # Logger.Print('ssssssssssssssss', payload)
        self.__config_getter.set(payload)
        # marker_getter = RemoteVar_mqtt(self.__config['mqtt_topic_of_marker_image'], None)


        
    def show_config(self):
        # print(self.__config["areas"][1]['postions'])
        for i in range(10):
            x1,y1,x2,y2 = self.__config["areas"][i]['postions']
            cv2.rectangle(self.__frame, (x1,y1),(x2,y2), (0,255,0), thickness=2)
        cv2.imshow("debug", self.__frame)

    def match_template(self, origin):
        method = cv2.TM_SQDIFF_NORMED

        result = cv2.matchTemplate(self.__config["marker_image"], origin, method)
        # We want the minimum squared difference
        mn,_,mnLoc,_ = cv2.minMaxLoc(result)
        # Draw the rectangle:
        # Extract the coordinates of our best match
        MPx, MPy = mnLoc

        imshow = False
        if imshow:
            # Step 2: Get the size of the template. This is the same size as the match.
            trows, tcols = self.__config["marker_image"].shape[:2]
            # Step 3: Draw the rectangle on origin
            cv2.rectangle(origin, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)
            cv2.imshow('match template',origin)
            cv2.waitKey(1)
        return MPx, MPy
            
    def SpinOnce(self):
        cv2.waitKey(1)
        if not self.__image_getter.rx_buffer_has_been_updated():
            return

        np_array = numpy.frombuffer(self.__image_getter.get(), dtype=numpy.uint8) 
        self.__frame = cv2.imdecode(np_array, flags=1)

        debug = True
        if debug:
            cv2.imshow("origin_from_mqtt",  self.__frame)
            self.show_config()
        # Now we got a frame, try to  find marker.  
        # left, top = self.match_template(self.__frame)
        left, top = 0, 0






        # crop frame to many ocr units, base location is the marker.
        x2,y2, x1,y1 = self.__config["areas"][1]['postions']
        # print(x1,y1, x2,y2)
        cropped_image = self.__frame[y1:y2, x1:x2]
        cv2.imshow("area-1", cropped_image)
        cv2.waitKey(1)
        tesseract_img = Image.fromarray(cropped_image)
        xx = pytesseract.image_to_string(tesseract_img)
        print(xx)
        # for unit in self.__all_units:
        #     image = unit.GetAreaImage(self.__frame, left, top)
        #     cv2.imshow(unit.name, image)
        #     cv2.waitKey(1)



