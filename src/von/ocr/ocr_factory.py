from von.ocr.ocr_unit import OcrUnit
from von.ocr.ocr_window import OcrWindow

from von.logger import Logger
from von.remote_var_mqtt import RemoteVar_mqtt

import cv2
import json


class OcrFactory:
    
    @classmethod
    def CreateKvmNodeConfig(cls, node_name:str):
        config = {}
        config['node_name'] = node_name
        config['my_topic'] = 'ocr/' + node_name + '/config'
        config['topic_of_screen_image'] = 'ocr/' + node_name + '/screen_image'
        config['resolution'] = (1024,768)
        config['fps'] = 1
        config['mode'] = 0  # 0=idle,  1=publish screen image 2=publish area image  3=publish ocr result
        return config


    @classmethod
    def CreateOcrWindow(cls, window_name:str) -> OcrWindow:
        '''
        Create ocr_window and config it.
        Load config from mqtt
        '''
        if window_name == 'ubuntu_performance':
            mqtt_topic_of_position_config = "ocr/" + window_name + "/config"
            mqtt_topic_of_screen_image = "ocr/" + window_name + "/screen_image"
            template_path_filename = "template_images/" + window_name + ".png"

            positions_config = RemoteVar_mqtt(mqtt_topic_of_position_config, None)
            # Logger.Print("OcrFactory::CreateOcrWindow()  point 31", '')
            while not positions_config.rx_buffer_has_been_updated():
                # wait mqtt syncing in the other thread.
                pass
            # Logger.Print("OcrFactory::CreateOcrWindow()  point 32", '')

            window_config = json.loads( positions_config.get())
            # Logger.Print("window_config", window_config)
            window_config["template_image"] = cv2.imread(template_path_filename)
            new_windows = OcrWindow(config = window_config, 
                                    mqtt_topic_of_image = mqtt_topic_of_screen_image)
            # Logger.Debug("OcrFactory::CreateOcrWindow() point 99")
            # Logger.Print("window_name", window_name)
            return new_windows
        
        else:
            Logger.Error("OcrFactory::CreateOcrWindow()")
            Logger.Print('requested window_name', window_name)
            return None # type: ignore

    

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