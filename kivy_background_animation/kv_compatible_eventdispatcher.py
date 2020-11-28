'''
Kv Compatible EventDispatcher
=============================

widget以外のEventDispatcherをKv言語上で使えるようにするためのmodule。
'''


__all__ = ('FakeParentBehavior', 'KvCompatibleEventDispatcher', )

from kivy.properties import ListProperty, DictProperty, ObjectProperty
from kivy.factory import Factory
from kivy.uix.widget import Widget, WidgetBase


class FakeParentBehavior:
    fake_children = ListProperty()

    def add_widget(self, widget, *args, **kwargs):
        widget = widget.__self__
        if widget in self.fake_children:
            raise ValueError(f"{widget!r} already belongs to me.")
        self.fake_children.append(widget)
        widget.fake_parent = self

    def remove_widget(self, widget, *args, **kwargs):
        widget = widget.__self__
        if widget in self.fake_children:
            self.fake_children.remove(widget)
            widget.fake_parent = None

    def clear_widgets(self, *args, **kwargs):
        for w in self.fake_children[:]:
            self.remove_widget(w)


class KvCompatibleEventDispatcher(WidgetBase):
    """:class:`EventDispatcher` that can be used in kv-language."""
    __events__ = ('on_kv_post', )
    _proxy_ref = None

    proxy_ref = Widget.proxy_ref
    '''Same as :class:`Widget`'s'''

    __hash__ = Widget.__hash__
    '''Same as :class:`Widget`'s'''

    apply_class_lang_rules = Widget.apply_class_lang_rules
    '''Same as :class:`Widget`'s'''

    on_kv_post = Widget.on_kv_post
    '''Same as :class:`Widget`'s'''

    cls = ListProperty([])
    '''Same as :class:`Widget`'s'''

    ids = DictProperty({})
    '''Same as :class:`Widget`'s'''

    fake_parent = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        # prevent from direct instantiation
        if type(self) is KvCompatibleEventDispatcher:
            raise TypeError(
                "KvCompatibleEventDispatcher may not be instantiated")

        no_builder = '__no_builder' in kwargs
        if no_builder:
            del kwargs['__no_builder']
        on_args = {k: v for k, v in kwargs.items() if k[:3] == 'on_'}
        for key in on_args:
            del kwargs[key]

        super().__init__(**kwargs)

        # Apply all the styles.
        if not no_builder:
            rule_children = []
            self.apply_class_lang_rules(
                ignored_consts=self._kwargs_applied_init,
                rule_children=rule_children)

            for widget in rule_children:
                widget.dispatch('on_kv_post', self)
            self.dispatch('on_kv_post', self)

        # Bind all the events.
        if on_args:
            self.bind(**on_args)


r = Factory.register
r('FakeParentBehavior', cls=FakeParentBehavior)
r('KvCompatibleEventDispatcher', cls=KvCompatibleEventDispatcher)
del r
