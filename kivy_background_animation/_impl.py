__all__ = ('BASpace', 'BAInstance', )

from kivy.lang import Builder
from kivy.uix.widget import Widget
from .kv_compatible_eventdispatcher import (
    FakeParentBehavior, KvCompatibleEventDispatcher,
)


Builder.load_string(r'''
<BASpace>:
    canvas.before:
        PushMatrix
        Translate:
            xy: self.pos
    canvas.after:
        PopMatrix
''')


BAInstance = KvCompatibleEventDispatcher


class BASpace(FakeParentBehavior, Widget):
    pass
