import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.clock import Clock
import time
import os
# import cv2
# import android
import zbar
from kivy.uix.label import Label
from PIL import Image

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
                
                BoxLayout:
                    id: boxy
                    size_hint_x: None
                    width:'48dp'
                    orientation: 'vertical'
                    ToggleButton:
                        orientation: 'vertical'
                        id: toggle
                        text: 'Play'
                        on_press: camera.play = not camera.play
                        size_hint_y: None
                        height:'48dp'
                    Button:
                        text: 'Capture'
                        size_hint_y: None
                        height: '48dp'
                        on_press: root.capture()
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
    def capture(self):
        camera = self.ids['camera']
        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')
        timestr = time.strftime("%Y%m%d_%H%M%S")
        # app_folder = os.path.dirname(os.path.abspath(__file__))
        # print(app_folder)
        tc=App.get_running_app()
        print(tc.user_data_dir, '---------------------------')
        app_folder = tc.user_data_dir
        if not os.path.exists(app_folder):
            os.makedirs(app_folder)
        camera.export_to_png(app_folder+"/IMG_{}.jpg".format(timestr))
        print(os.listdir(app_folder))
        pil = Image.open(app_folder+"/IMG_{}.jpg".format(timestr)).convert('L')
        width, height = pil.size
        try:
            raw = pil.tostring()
        except( AttributeError, NotImplementedError):
            raw = pil.tobytes()
        image = zbar.Image(width, height, 'Y800', raw)

        scanner.scan(image)

        print("Captured!")
        for symbol in image:
            print 'decoded', symbol.type, symbol.data
            label = self.ids.toggle
            label.text = str(symbol.type) + ' ' + str(symbol.data)
            label = self.ids.result
            label.text = str(symbol.type) + '\n\n' + str(symbol.data)
            break
        del(image)

    def decode(self, *args):
        try:
            pil = Image.open(args[1][0]).convert('L')
            width, height = pil.size
            try:
                raw = pil.tostring()
            except( AttributeError, NotImplementedError):
                raw = pil.tobytes()
            image = zbar.Image(width, height, 'Y800', raw)
            scanner = zbar.ImageScanner()
            scanner.parse_config('enable')
            scanner.scan(image)

            print("Captured!")
            for symbol in image:
                print 'decoded', symbol.type, symbol.data
                label = self.ids.toggle
                label.text = str(symbol.type) + ' ' + str(symbol.data)
                label = self.ids.result
                label.text = str(symbol.type) + '\n\n' + str(symbol.data)
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
        tc=App.get_running_app()
        print(tc.user_data_dir, '---------------------------')
        app_folder = tc.user_data_dir
        if not os.path.exists(app_folder):
            os.makedirs(app_folder)
        camera.export_to_png(app_folder+"/IMG_{}.jpg".format(timestr))
        print(os.listdir(app_folder))
        pil = Image.open(app_folder+"/IMG_{}.jpg".format(timestr)).convert('L')
        width, height = pil.size
        try:
            raw = pil.tostring()
        except( AttributeError, NotImplementedError):
            raw = pil.tobytes()
        image = zbar.Image(width, height, 'Y800', raw)

        scanner.scan(image)

        print("Captured!")
        for symbol in image:
            print 'decoded', symbol.type, symbol.data
            label = self.ids.toggle
            label.text = str(symbol.type) + ' ' + str(symbol.data)
            label = self.ids.result
            label.text = str(symbol.type) + '\n\n' + str(symbol.data)
            self.switch_to(self.ids.sc3head)
            # self.ids.camera.play = False
            break
        else:
            os.remove(app_folder+"/IMG_{}.jpg".format(timestr))
            print("Found nothing.")
            Clock.schedule_once(self.scheduled_scan, 1.0/60.0)
        del(image)


class SQRReader(App):
    def build(self):
        cam = CameraClick()
        Clock.schedule_once(cam.scheduled_scan, 1.0/60.0)
        return cam

# class MyApp(App):
#     def build(self):
#         return Label(text="hello world")

# MyApp().run()
SQRReader().run()
