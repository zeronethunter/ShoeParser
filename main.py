from kivymd.app import MDApp
from kivymd.uix.toolbar import MDToolbar
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivymd.uix.textfield import MDTextField
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivy.properties import StringProperty, NumericProperty
from kivy.factory import Factory
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.recycleview import RecycleView
import ssl
import urllib.request
import json
import os

__version__ = '1.0'

import refresh


class WindowManager(ScreenManager):
    pass


class ShoeScreen(MDScreen):
    pass


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        data = []
        if os.path.isdir('Cache'):
            for file in os.listdir('Cache'):
                name, price, link = file[:-4].split(';')
                if not name or name.isnumeric():
                    pass
                else:
                    data.append({'shoe_name': name,
                                 'price': price,
                                 'link': link.replace('_', '/').replace('!', '.'),
                                 'image_source': 'Cache/' + file})
        self.data = data

    def on_close(self):
        self.data.clear()


class AllShoesScreen(MDScreen):
    pass


class MyToolbar(MDToolbar):
    pass


class MyDialog(MDTextField):
    pass


class SearchMenu(MDDialog):
    title = 'Search'
    type = 'custom'
    text = StringProperty()

    def __init__(self, **kwargs):
        self.content_cls = MyDialog(font_size=self.height * .5)
        self.buttons = [
            MDFlatButton(text='FIND',
                         font_size=self.height * .3,
                         on_press=self.callback)
        ]
        super(SearchMenu, self).__init__(**kwargs)

    def callback(self, *args):
        self.text = self.content_cls.text
        self.dismiss()
        app = MDApp.get_running_app()
        app.refresh_with(self.text)


class CustomLabel(MDLabel):
    label_font_size = NumericProperty(32)

    def __init__(self, **kwargs):
        self.label_font_size = self.height
        super(CustomLabel, self).__init__(**kwargs)

    def build(self):
        self.canvas.before.clear()


class ImageCanvas(ButtonBehavior, Image):
    def __del__(self):
        self.remove_from_cache()


class ShoeButton(BoxLayout):
    shoe_name = StringProperty()
    price = StringProperty()
    link = StringProperty()
    image_source = StringProperty()
    new_line = StringProperty('\n')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BasketShoesApp(MDApp):
    title = 'Basketball Shoes'
    search_menu = None
    screen_manager = None

    def build(self):
        self.screen_manager = Factory.BasketShoesApp()
        self.screen_manager.current = 'all_shoes_screen'
        self.search_menu = SearchMenu(size_hint=(None, None),
                                      size=(Window.width * .5, Window.height * .7))
        return self.screen_manager

    def refresh_shoes(self):
        data = []
        if os.path.isdir('Cache'):
            for file in os.listdir('Cache'):
                name, price, link = file[:-4].split(';')
                if not name or name.isnumeric():
                    pass
                else:
                    data.append({'shoe_name': name,
                                 'price': price,
                                 'link': link.replace('_', '/').replace('!', '.'),
                                 'image_source': 'Cache/' + file})
        self.screen_manager.current_screen.ids.rv_id.data = data
        self.screen_manager.current_screen.ids.rv_id.refresh_from_data()

    def refresh_with(self, name_template):
        data = []
        if os.path.isdir('Cache'):
            count = 0
            for file in os.listdir('Cache'):
                name, price, link = file[:-4].split(';')
                if name.lower().find(name_template.lower()) != -1 and name:
                    data.append({'shoe_name': name,
                                 'price': price,
                                 'link': link.replace('_', '/').replace('!', '.'),
                                 'image_source': 'Cache/' + file})
                    count += 1
            if count == 0:
                data.append({'shoe_name': '',
                             'price': '',
                             'link': '',
                             'image_source': 'ERROR.png'})
        self.screen_manager.current_screen.ids.rv_id.data = data
        self.screen_manager.current_screen.ids.rv_id.refresh_from_data()

    def sort_ascending(self):
        toolbar = self.screen_manager.current_screen.ids.my_toolbar_id
        sorting = toolbar.left_action_items[0][0]
        data = self.screen_manager.current_screen.ids.rv_id.data
        if sorting == 'sort-ascending':
            self.screen_manager.current_screen.ids.rv_id.data = sorted(data, key=lambda i: int(i['price'][:-5]))
            toolbar.left_action_items[0][0] = 'sort-descending'
        else:
            self.screen_manager.current_screen.ids.rv_id.data = sorted(data, key=lambda i: int(i['price'][:-5]),
                                                                       reverse=True)
            toolbar.left_action_items[0][0] = 'sort-ascending'
        self.screen_manager.current_screen.ids.rv_id.refresh_from_data()


def make_db():
    if not os.path.isdir('Cache'):
        os.mkdir('Cache')

    if os.path.isfile('items.jl'):
        items = open('items.jl', 'r')
        for line in items:
            if line == '':
                break
            item = json.loads(line)
            jpg_path_name = 'Cache/' + item['name'] + ';' + item['price'] + ';' + item['link'].replace('.',
                                                                                                       '!').replace('/',
                                                                                                                    '_') + '.jpg'
            if not os.path.isfile(jpg_path_name):
                urllib.request.urlretrieve(item['img'].replace(' ', '%20'), jpg_path_name)


if __name__ == '__main__':
    builder = Builder.load_file('main.kv')
    ssl._create_default_https_context = ssl._create_unverified_context
    refresh.start()
    make_db()
    BasketShoesApp().run()
