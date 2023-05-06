from von.remote_var_mqtt import RemoteVar_mqtt
from von.logger import Logger

import cv2
import numpy
import pytesseract
from PIL import Image #pip install pillow




class OcrWindow:

    def __init__(self, config,  mqtt_topic_of_image) -> None:
        '''
        Image source is mqtt-message
        '''
        # self.__config = RemoteVar_mqtt(mqtt_topic_of_config, {})
        self.__image = RemoteVar_mqtt(mqtt_topic_of_image, None)
        self.__config = config
        # self.__is_loaded = False  # Load image and config, backgroundly

        self.__all_units = []
        self.__frame = numpy.zeros((1080,768,3), numpy.uint8)

    def show_config(self):
        # print(self.__config["areas"][1]['postions'])
        for i in range(10):
            x1,y1,x2,y2 = self.__config["areas"][i]['postions']
            cv2.rectangle(self.__frame, (x1,y1),(x2,y2), (0,255,0), thickness=2)
        cv2.imshow("debug", self.__frame)

    def match_template(self, origin):
        method = cv2.TM_SQDIFF_NORMED

        result = cv2.matchTemplate(self.__config["template_image"], origin, method)
        # We want the minimum squared difference
        mn,_,mnLoc,_ = cv2.minMaxLoc(result)
        # Draw the rectangle:
        # Extract the coordinates of our best match
        MPx, MPy = mnLoc

        imshow = False
        if imshow:
            # Step 2: Get the size of the template. This is the same size as the match.
            trows, tcols = self.__config.template_image.shape[:2]
            # Step 3: Draw the rectangle on origin
            cv2.rectangle(origin, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)
            cv2.imshow('match template',origin)
            cv2.waitKey(1)
        return MPx, MPy
            
    def SpinOnce(self):
        if not self.__image.rx_buffer_has_been_updated():
            cv2.waitKey(1)
            return

        np_array = numpy.frombuffer(self.__image.get(), dtype=numpy.uint8) 
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



