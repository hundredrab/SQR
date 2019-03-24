import os
import time

from PIL import Image

import kivy
import pyqrcode
import zbar
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.tabbedpanel import TabbedPanel

kivy.require('1.10.0')
# import cv2
# import android

Builder.load_string('''
<cameraClick>:
    manager:manager
    do_default_tab: False
    ScreenManager:
        id: manager
        Screen:
            id: sc1
            name: 'Camera'
            orientation: 'horizontal'
            BoxLayout:
                Camera:
                    id: camera
                    resolution: (640, 480)
                    play: True

        Screen:
            id: sc2
            name: 'gallery'
            FileChooserIconView:
                id: file_chooser
                canvas.before:
                    Color:
                        rgb: 04,0.5,0.4
                    Rectangle:
                        pos: self.pos
                        size: self.size
                on_selection: root.decode(*args)
        Screen:
            id: sc3
            name: 'results'
            Label:
                id: result
                text: "Nothing"

        Screen:
            id: sc4
            name: 'Create New'
            BoxLayout:
                orientation: 'vertical'
                TextInput:
                    name: 'txt'
                    id: txt
                    text: 'SQRReader'
                Button:
                    text: 'Create'
                    on_press: root.say_my_name(txt.text)

    TabbedPanelHeader:
        text: sc1.name
        screen: sc1.name
    TabbedPanelHeader:
        text: sc2.name
        screen: sc2.name
    TabbedPanelHeader:
        id: sc3head
        text: sc3.name
        screen: sc3.name
    TabbedPanelHeader:
        id: sc4head
        text: sc4.name
        screen: sc4.name
''')


class CameraClick(TabbedPanel):
    manager = ObjectProperty(None)

    def switch_to(self, header):
        self.manager.current = header.screen
        self.current_tab.state = "normal"
        header.state = "down"
        self._current_tab = header
        print(self._current_tab.screen)
        if self._current_tab.screen == 'Camera':
            self.ids.camera.play = True
            Clock.schedule_once(self.scheduled_scan, 1)
        else:
            self.ids.camera.play = False
        self.ids.file_chooser.path = App.get_running_app().user_data_dir

    def decode(self, *args):
        try:
            pil = Image.open(args[1][0]).convert('L')
            width, height = pil.size
            try:
                raw = pil.tostring()
            except(AttributeError, NotImplementedError):
                raw = pil.tobytes()
            image = zbar.Image(width, height, 'Y800', raw)
            scanner = zbar.ImageScanner()
            scanner.parse_config('enable')
            scanner.scan(image)

            print("Captured!")
            for symbol in image:
                print 'decoded', symbol.type, symbol.data
                label = self.ids.result
                label.text = str(symbol.type) + '\n\n' + str(symbol.data)
                self.switch_to(self.ids.sc3head)
                break
            del(image)
        except Exception as ae:
            print(ae)

    def scheduled_scan(self, dt):
        camera = self.ids['camera']
        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')
        timestr = time.strftime("%Y%m%d_%H%M%S")
        # app_folder = os.path.dirname(os.path.abspath(__file__))
        # print(app_folder)
        tc = App.get_running_app()
        app_folder = tc.user_data_dir
        if not os.path.exists(app_folder):
            os.makedirs(app_folder)
        camera.export_to_png(app_folder+"/IMG_{}.jpg".format(timestr))
        pil = Image.open(app_folder+"/IMG_{}.jpg".format(timestr)).convert('L')
        width, height = pil.size
        try:
            raw = pil.tostring()
        except(AttributeError, NotImplementedError):
            raw = pil.tobytes()
        image = zbar.Image(width, height, 'Y800', raw)

        scanner.scan(image)

        for symbol in image:
            print 'decoded', symbol.type, symbol.data
            label = self.ids.result
            label.text = str(symbol.type) + '\n\n' + str(symbol.data)
            self.switch_to(self.ids.sc3head)
            # self.ids.camera.play = False
            break
        else:
            os.remove(app_folder+"/IMG_{}.jpg".format(timestr))
            print("Found nothing.")
            Clock.schedule_once(self.scheduled_scan, 1.0/2)
        del(image)

    def say_my_name(self, text):
        # print(self.ids.txt)
        # print(dir(self.ids.txt))
        print(text)
        qr_code_raw = pyqrcode.create(text)
        app_folder = App.get_running_app().user_data_dir
        qr_code_raw.svg('SQR'+text+'.svg', scale=8)
        print("saved!")


class SQRReader(App):
    def build(self):
        cam = CameraClick()
        Clock.schedule_once(cam.scheduled_scan, 1.0/60.0)
        return cam


SQRReader().run()
