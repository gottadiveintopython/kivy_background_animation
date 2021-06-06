from kivy.app import App
from kivy.lang import Builder

from kivy_background_animation import vertical

KV_CODE = '''
#:import random random.random
#:import T kivy.animation.AnimationTransition

FloatLayout:
    BAVertical:
        max_sprites: 400
        color: "#668811"
        func_x: lambda: T.out_expo(random())
        func_spawning_interval: lambda: 0
    Label:
        text: 'BAVertical'
        font_size: 100
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
