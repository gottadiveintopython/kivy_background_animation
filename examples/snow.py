from kivy.app import App
from kivy.lang import Builder

from kivy_background_animation import snow

KV_CODE = '''
#:import random random.random
#:import T kivy.animation.AnimationTransition

FloatLayout:
    BASnow:
    Label:
        text: 'BASnow'
        font_size: 100
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
