from kivy.app import App
from kivy.lang import Builder

from kivy_background_animation.predefined import vertical

KV_CODE = '''
#:import random random.random
#:import uniform random.uniform
#:import Window kivy.core.window.Window
#:import T kivy.animation.AnimationTransition
#:import CoreImage kivy.core.image.Image
#:set texture CoreImage("data/logo/kivy-icon-128.png").texture

<Separator@Widget>:
    size: 2, 2
    canvas:
        Color:
            rgb: 1, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
<HSeparator@Separator>:
    size_hint_y: None
<VSeparator@Separator>:
    size_hint_x: None

<MainLabel@Label>:
    font_size: max(sp(15), 20)
    color: .7, .9, .2, 1
    outline_width: 2
    outline_color: 0, 0, 0, 1
    size_hint_y: None
    height: self.texture_size[1] + 4
<SubLabel@Label>:
    font_size: max(sp(14), 15)
    color: .7, .9, .2, 1
    outline_width: 1
    outline_color: 0, 0, 0, 1

FloatLayout:
    BASpace:
        BAVertical:
            id: anim
            sprite_size: sprite_size.value
            max_sprites: max_sprites.value
            texture: texture if use_texture.active else None
            color: (*color.color[:3], opacity.value, )
            func_spawning_interval: lambda: uniform(spwn_min.value, spwn_max.value)
            func_velocity: lambda: uniform(velocity_min.value, velocity_max.value)
    BoxLayout:
        BoxLayout:
            orientation: 'vertical'
            MainLabel:
                text: 'max_sprites: {}\\n(changing this restarts the animation)'.format(max_sprites.value)
                halign: 'center'
            Slider:
                id: max_sprites
                min: 1
                max: 1000
                step: 1
                value: 100
            HSeparator:
            MainLabel:
                text: 'sprite_size: {}'.format(sprite_size.value)
            Slider:
                id: sprite_size
                min: 2
                max: 400
                step: 1
                value: 2
            HSeparator:
            MainLabel:
                text: 'color'
            ColorWheel:
                id: color
                color: 1, 1, 1, 1
            HSeparator:
            MainLabel:
                text: 'opacity'
            Slider:
                id: opacity
                min: 0
                max: 1
                step: 0.1
                value: 0.4
            HSeparator:
            MainLabel:
                text: 'use texture?'
            CheckBox:
                id: use_texture
                active: False
        VSeparator:
        BoxLayout:
            orientation: 'vertical'
            MainLabel:
                text: 'distribution'
            BoxLayout:
                CheckBox:
                    group: 'distribution'
                    on_active: if args[1]: anim.func_x = random
                SubLabel:
                    text: 'linear'
            BoxLayout:
                CheckBox:
                    group: 'distribution'
                    on_active: if args[1]: anim.func_x = (lambda: T.out_expo(random()))
                SubLabel:
                    text: 'out_expo'
            BoxLayout:
                CheckBox:
                    group: 'distribution'
                    on_active: if args[1]: anim.func_x = (lambda: T.in_cubic(random()))
                SubLabel:
                    text: 'in_cubic'
            HSeparator:
            MainLabel:
                text: 'spawning interval'
            BoxLayout:
                SubLabel:
                    text: 'min: {:.01f}sec'.format(spwn_min.value)
                    size_hint_x: .6
                Slider:
                    id: spwn_min
                    min: 0
                    max: 2
                    step: 0.1
                    value: 0
            BoxLayout:
                SubLabel:
                    text: 'max: {:.01f}sec'.format(spwn_max.value)
                    size_hint_x: .6
                Slider:
                    id: spwn_max
                    min: 0
                    max: 2
                    step: 0.1
                    value: 1
            HSeparator:
            MainLabel:
                text: 'velocity'
            BoxLayout:
                SubLabel:
                    text: 'min: {}pixels/sec'.format(velocity_min.value)
                    size_hint_x: .6
                Slider:
                    id: velocity_min
                    min: -400
                    max: 400
                    step: 1
                    value: 1
            BoxLayout:
                SubLabel:
                    text: 'max: {}pixels/sec'.format(velocity_max.value)
                    size_hint_x: .6
                Slider:
                    id: velocity_max
                    min: -400
                    max: 400
                    step: 1
                    value: 50
'''


class SampleApp(App):
    def build(self):
        return Builder.load_string(KV_CODE)


if __name__ == '__main__':
    SampleApp().run()
