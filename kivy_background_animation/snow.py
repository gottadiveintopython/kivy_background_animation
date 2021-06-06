__all__ = ('BASnow', )

from array import array
import random as random_module
from kivy.clock import Clock
from kivy.lang import Builder

from kivy.graphics import Point, Color
from kivy.core.image import Image as CoreImage
from kivy.properties import (
    ColorProperty, StringProperty, ObjectProperty, BoundedNumericProperty,
)
from kivy.uix.widget import Widget
import asynckivy



Builder.load_string(r'''
<BASnow>:
    canvas.before:
        PushMatrix
        Translate:
            xy: self.pos
    canvas.after:
        PopMatrix
''')


class BASnow(Widget):
    '''spriteが上端/下端から現れ下端/上端に向かって流れていくanimation
    '''

    random = ObjectProperty(None, allownone=True)
    '''animationの計算に使う乱数生成器を指定できる。random.Random型。'''

    texture = ObjectProperty(None, allownone=True)
    '''spriteに貼り付けるtexture。sourceと共に使うべからず。

    'texture' is preferable than 'source' if you are going to frequently
    change the properties of the class.
    '''

    source = StringProperty()
    '''spriteに貼り付けるtextureのfilepath。textureと共に使うべからず。'''

    color = ColorProperty("#FFFFFFFF")
    '''spriteの色。textureのpixelと乗算される'''

    sprite_size = BoundedNumericProperty(None, min=2, allownone=True)
    '''spriteの大きさ。Noneの場合はtextureの大きさをそのままspriteの大きさとして使う。'''

    max_sprites = BoundedNumericProperty(1000, min=1)
    '''一度に現れるspriteの最大数。
    When this property changes, the animation will re-start.
    '''

    func_velocity = ObjectProperty()
    '''一つspriteが作られる毎に呼ばれ、戻り値がspriteの速度(単位はpixel)となる。'''

    func_spawning_interval = ObjectProperty(None, allownone=True)
    '''一つspriteが作られる毎に呼ばれ、戻り値が次のspriteを作るまでの間隔(単位は秒)となる。'''

    func_x = ObjectProperty(None, allownone=True)
    '''一つspriteが作られる毎に呼ばれ、戻り値がspriteのx座標(0から1の範囲)となる。'''

    func_amplitude = ObjectProperty(None, allownone=True)
    '''一つspriteが作られる毎に呼ばれ、戻り値がspriteの揺れ幅(単位はpixel)となる。'''

    max_amplitude = BoundedNumericProperty(0, min=0)
    ''''func_amplitude()'が返しうる最大の値をここに指定する必要がある'''

    _main_task = asynckivy.sleep_forever()

    def __init__(self, **kwargs):
        self._needs_to_restart = True
        self._ctx = {}
        self._trigger_update = trigger_update = \
            Clock.create_trigger(self._update, .1)
        super().__init__(**kwargs)
        fbind = self.fbind
        trigger_restart = self.trigger_restart
        for name in ('parent', 'max_sprites', ):
            fbind(name, trigger_restart)
        for name in (
                'random', 'texture', 'source', 'color', 'sprite_size',
                'func_velocity', 'func_spawning_interval', 'func_x',
                'func_amplitude', 'max_amplitude', ):
            fbind(name, trigger_update)

    def trigger_restart(self, *args, **kwargs):
        self._needs_to_restart = True
        self._trigger_update()

    def _update(self, *args, **kwargs):
        self._main_task.close()
        if self.parent is None:
            return
        self._main_task = asynckivy.start(self._async_main())

    async def _async_main(self):
        needs_to_restart = self._needs_to_restart

        # setup texture
        texture = self.texture
        if texture and self.source:
            raise ValueError("You cannot specify both 'texture' and 'source'.")
        if self.source:
            texture = CoreImage(self.source).texture

        # calculate 'point_size'
        if self.sprite_size is None:
            point_size = 1 if texture is None else (max(texture.size) / 2)
        else:
            point_size = self.sprite_size / 2

        # setup graphics instructions
        ctx = self._ctx
        if needs_to_restart:
            with self.canvas:
                color_inst = Color()
                point_inst = Point()
        else:
            color_inst = ctx['color_inst']
            point_inst = ctx['point_inst']
        color_inst.rgba = self.color
        point_inst.pointsize = point_size
        point_inst.texture = texture

        # create arrays
        if needs_to_restart:
            max_sprites = self.max_sprites
            ctx.update(
                visible_arr=array('B', [0, ] * max_sprites),
                base_x_arr=array('f', [0., ] * max_sprites),
                x_arr=array('f', [0., ] * max_sprites),
                y_arr=array('f', [0., ] * max_sprites),
                velocity_y_arr=array('f', [0., ] * max_sprites),
                amplitude_arr=array('f', [0., ] * max_sprites),
                radian_arr=array('f', [0., ] * max_sprites),
            )

        # setup the amplitude
        random = self.random or random_module
        if self.func_amplitude is None:
            func_amplitude = lambda: random.uniform(100, 600, )
            max_amplitude = 600
        else:
            func_amplitude = self.func_amplitude
            max_amplitude = self.max_amplitude

        # build 'ctx'
        ctx.update(
            random=random,
            widget=self,
            point_size=point_size,
            color_inst=color_inst,
            point_inst=point_inst,
            func_x=self.func_x or random.random,
            func_spawning_interval=self.func_spawning_interval \
                or (lambda: random.random() * .2),
            func_velocity=self.func_velocity \
                or (lambda: float(random.randint(-60, -1))),
            func_amplitude=func_amplitude,
            max_amplitude=max_amplitude,
        )

        # start animation
        try:
            self._needs_to_restart = False
            await asynckivy.and_(
                _spawn_sprite(ctx),
                _remove_sprite_if_its_outside_of_the_space(ctx),
                _move_sprites(ctx),
            )
        finally:
            if self._needs_to_restart:
                ctx.clear()
                self.canvas.remove(point_inst)
                self.canvas.remove(color_inst)


async def _spawn_sprite(ctx:dict):
    from asynckivy import sleep
    import math

    # unpack 'ctx' to improve performance
    random = ctx['random']
    func_spawning_interval = ctx['func_spawning_interval']
    func_velocity = ctx['func_velocity']
    func_x = ctx['func_x']
    func_amplitude = ctx['func_amplitude']
    widget = ctx['widget']
    visible_arr = ctx['visible_arr']
    velocity_y_arr = ctx['velocity_y_arr']
    base_x_arr = ctx['base_x_arr']
    y_arr = ctx['y_arr']
    amplitude_arr = ctx['amplitude_arr']
    radian_arr = ctx['radian_arr']

    grace_x = ctx['point_size'] + ctx['max_amplitude']
    grace_y = ctx['point_size']
    min_x = -grace_x
    min_y = -grace_y
    uniform = random.uniform
    pi_x_2x = math.pi * 2
    while True:
        await sleep(func_spawning_interval())
        try:
            # 空いているslotのindexを求める
            i = visible_arr.index(0)
        except ValueError:
            continue
        max_x = widget.width + grace_x
        max_y = widget.height + grace_y
        velocity_y = func_velocity()
        velocity_y_arr[i] = velocity_y
        base_x_arr[i] = min_x + func_x() * (max_x - min_x)
        y_arr[i] = min_y if velocity_y >= 0. else max_y
        amplitude_arr[i] = func_amplitude()
        radian_arr[i] = uniform(0., pi_x_2x)
        visible_arr[i] = 1


async def _remove_sprite_if_its_outside_of_the_space(ctx:dict):
    from asynckivy import create_sleep
    from itertools import compress, count

    # unpack 'ctx' to improve performance
    widget = ctx['widget']
    visible_arr = ctx['visible_arr']
    x_arr = ctx['x_arr']
    y_arr = ctx['y_arr']

    grace_x = ctx['point_size'] + ctx['max_amplitude']
    grace_y = ctx['point_size']
    min_x = -grace_x
    min_y = -grace_y
    sleep = await create_sleep(2)
    while True:
        await sleep()
        max_x = widget.width + grace_x
        max_y = widget.height + grace_y
        for i in compress(count(), visible_arr):
            if (min_y <= y_arr[i] <= max_y) and (min_x <= x_arr[i] <= max_x):
                pass
            else:
                visible_arr[i] = 0


async def _move_sprites(ctx:dict):
    from math import cos
    from time import perf_counter as get_current_time
    from itertools import compress, count, chain
    from asynckivy import create_sleep

    # unpack 'ctx' to improve performance
    point_inst = ctx['point_inst']
    visible_arr = ctx['visible_arr']
    velocity_y_arr = ctx['velocity_y_arr']
    base_x_arr = ctx['base_x_arr']
    x_arr = ctx['x_arr']
    y_arr = ctx['y_arr']
    amplitude_arr = ctx['amplitude_arr']
    radian_arr = ctx['radian_arr']

    chain_from_iterable = chain.from_iterable
    sleep = await create_sleep(0)
    last = get_current_time()
    while True:
        await sleep()
        current = get_current_time()
        delta = current - last
        last = current
        for i in compress(count(), visible_arr):
            y_arr[i] += velocity_y_arr[i] * delta
            radian = radian_arr[i] + delta * 0.2
            radian_arr[i] = radian
            x_arr[i] = base_x_arr[i] + amplitude_arr[i] * cos(radian)
        # 描画命令を更新
        point_inst.points = tuple(chain_from_iterable(
            compress(zip(x_arr, y_arr), visible_arr)))
