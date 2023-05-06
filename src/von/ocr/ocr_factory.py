from von.ocr.ocr_unit import OcrUnit
from von.ocr.ocr_window import OcrWindow

from von.logger import Logger
from von.mqtt.remote_var_mqtt import RemoteVar_mqtt

import cv2
import numpy
import json


class OcrFactory:
    
    @classmethod
    def ListKvmNodes(cls):
        all = ['kvm_230506',
               'hdmi_230507',
               
               ]
        return all
    
    @classmethod
    def ListAppWindows(cls):
        all = ['ubuntu_performance',

            ]
        return all



    @classmethod
    def CreateKvmNodeConfig(cls, kvm_node_name:str):
        config = {}
        config['node_name'] = kvm_node_name
        config['my_topic'] = 'ocr/kvm/' + kvm_node_name + '/config'
        config['topic_of_screen_image'] = 'ocr/kvm' + kvm_node_name + '/screen_image'
        config['resolution'] = (1024,768)
        config['fps'] = 1
        config['mode'] = 1  # 0=idle,  1=publish screen image 2=publish area image  3=publish ocr result
        return config

    # @classmethod
    # def CreateOcrWindow(cls, app_window_name:str) ->OcrWindow:
    #     ocr_window = OcrWindow("nothing", app_window_name=app_window_name,auto_init_config=True)
        


    # @classmethod
    # def LoadOcrWindow(cls, kvm_node_name:str, app_window_name:str) -> OcrWindow:
    #     '''
    #     1. Load configuration from mqtt.
    #     2. Create ocr_window with configuration.
    #     '''
    #     window_config = {}

    #     # screen image
    #     window_config['mqtt_topic_of_screen_image'] = "ocr/kvm/" + kvm_node_name + "/screen_image"

    #     # marker image
    #     mqtt_topic_of_appwindow_marker_image = "ocr/app_window/" + app_window_name + "/marker"
    #     marker_getter = RemoteVar_mqtt(mqtt_topic_of_appwindow_marker_image, None)
    #     while not marker_getter.rx_buffer_has_been_updated():
    #         pass
    #     np_array = numpy.frombuffer(marker_getter.get(), dtype=numpy.uint8) 
    #     window_config['marker_image'] = cv2.imdecode(np_array, flags=1)

    #     # areas and positions
    #     mqtt_topic_of_position_config = "ocr/app_window/" + app_window_name + "/areas"
    #     positions_getter = RemoteVar_mqtt(mqtt_topic_of_position_config, None)
    #     while not positions_getter.rx_buffer_has_been_updated():
    #         pass
    #     window_config['areas'] = json.loads( positions_getter.get())
        
    #     # ready to create ocr_window
    #     ocr_window = OcrWindow(config = window_config)
        
    #     Logger.Debug("OcrFactory::CreateOcrWindow() point 99")
    #     Logger.Print("window_name", app_window_name)
    #     return ocr_window
        
    

    @classmethod
    def CreateOcrUnit(cls, unit_name:str) -> OcrUnit:
        if unit_name == 'title':
            unit = OcrUnit()
            unit.name = unit_name
            unit.height = 660
            unit.width = 450
            unit.left_offset = -20
            unit.top_offset = 50
            return unit
        else:
            Logger.Error('CreateOcrUnit()')
            Logger.Print('request unit_name', unit_name)
            return None # type: ignore