import kivy
kivy.require('1.10.0')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
import time
import os
# import cv2
# import android
import zbar
from kivy.uix.label import Label
from PIL import Image

Builder.load_string('''
<cameraClick>:
    orientation: 'horizontal'
    Camera:
        id: camera
        resolution: (480, 640)
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
            canvas.before:
                PushMatrix
                Rotate: 
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            size_hint_x: None
            width:'48dp'
        Button:
            canvas.before:
                PushMatrix
                Rotate: 
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: 'Capture'
            size_hint_x: None
            width: '48dp'
            on_press: root.capture()
''')


class CameraClick(BoxLayout):
    def capture(self):
        print(self)
        camera = self.ids['camera']
        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')
        print(camera.texture)
        print(dir(camera.texture))
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
        print(pil)
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
            print(self, self.ids, self.ids.boxy)
            label = self.ids.toggle
            label.text = str(symbol.type) + ' ' + str(symbol.data)
            break
        else:
            print("What")
        print(image)
        print(list(image))
        del(image)

class TestCamera(App):
    def build(self):
        print(self.user_data_dir, '===================')
        return CameraClick()

# class MyApp(App):
#     def build(self):
#         return Label(text="hello world")

# MyApp().run()
TestCamera().run()
