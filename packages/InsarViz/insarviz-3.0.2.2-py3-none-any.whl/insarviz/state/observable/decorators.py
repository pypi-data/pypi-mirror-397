from typing import Any

from .__prelude__ import Qt
from .Lens import SELF
from .Dynamic import Dynamic, PureDynamic

class dynamic_property:
    def __init__(self, initial = None):
        self.__initial = initial
    def __set_name__(self, klass, name):
        self.__name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        sig = instance.dynamic_attribute(self.name)
        return sig.value
    def __set__(self, instance, value):
        sig = instance.dynamic_attribute(self.name)
        sig.value = value
    def register(self, instance):
        return PureDynamic(self.__initial)
    @property
    def name(self):
        return self.__name

# Useful decorators
class CachedProperty(dynamic_property):
    class __CachedDynamic(Dynamic):
        def __init__(self, depends, func, instance, destroy):
            super().__init__()
            self.__depends = depends
            self.__destroy = destroy
            self.__func = func
            self.__last_computed = None
            self.__instance = instance
            self.__last_depend_triggered = None
            for dep in self.__depends:
                dep.value_changed.connect(self.__on_depend_changed(dep))

        def __on_depend_changed(self, dep):
            def doit():
                self.__last_depend_triggered = dep
                self.invalidate()
            return doit

        def invalidate(self):
            if hasattr(self, "_current_value"):
                del self._current_value
            self.value_changed.emit(self.__last_computed)
        def clear(self):
            self.invalidate()
            self.__destroy(self.__last_computed)
            self.__last_computed = None

        @property
        def value(self):
            if not hasattr(self, "_current_value"):
                self.__destroy(self.__last_computed)
                self._current_value = self.__func(self.__instance, self.__last_depend_triggered)
                self.__last_computed = self._current_value
            return self._current_value

    def __init__(self, depends, func, destroy):
        self.__depends = depends
        self.__func = func
        self.__destroy = destroy

    def register(self, instance):
        return self.__CachedDynamic([dep[instance] for dep in self.__depends], self.__func, instance, self.__destroy)
def cached_property(*depends, destroy = lambda _: None):
    return lambda f: CachedProperty(depends, lambda _self, _: f(_self), destroy)
cached_property.tracing = lambda *depends: lambda f: CachedProperty(depends, f)

def dynamic_method(*depends):
    def wrap(f):
        def ret(_self):
            def doit(*args, **kwargs):
                return f(_self, *args, **kwargs)
            return doit
        ret.__name__ = f.__name__
        return cached_property(*depends)(ret)
    return wrap

class view_property(dynamic_property):
    class __PrivateProperty:
        def __init__(self, view_name):
            self.__view_name = view_name
        def __get__(self, instance, owner):
            if instance is None:
                return self
            return instance.dynamic_attribute(self.__view_name).value
        def __set__(self, instance, value):
            instance.dynamic_attribute(self.__view_name).set_value(value)
    class __ReadonlyDynamic(Dynamic):
        def __init__(self, name):
            super().__init__()
            self.__value = None
            self.__name = name
        def set_value(self, value):
            old = self.__value
            self.__value = value
            self.value_changed.emit(old)
        @property
        def value(self):
            return self.__value
        @value.setter
        def value(self, v):
            raise Exception(f"view property '{self.__name}' is readonly")

    def __set_name__(self, klass, name):
        super().__set_name__(klass, name)
        self.__hidden_name = "_"+name
        setattr(klass, self.__hidden_name, self.__PrivateProperty(self.name))
    def register(self, instance):
        return self.__ReadonlyDynamic(self.name)

class derived_property(dynamic_property):
    def register(self, instance):
        ret = getattr(instance, "_dynamic_"+self.name, PureDynamic(None))
        return ret

class filtered_property(dynamic_property):
    class __FilteredDynamic(Dynamic):
        def __init__(self, instance, filt):
            super().__init__(None)
            self.__filter = filt
            self.__instance = instance
            self.__value = None
        @property
        def value(self):
            return self.__value
        @value.setter
        def value(self, v):
            old = self.__value
            self.__value = self.__filter(self.__instance, v)
            self.value_changed.emit(old)

    def __init__(self, filt):
        self.__filter = filt
    def register(self, instance):
        return self.__FilteredDynamic(instance, self.__filter)

class dynamic:
    variable           = dynamic_property
    filtered_variable  = filtered_property
    readonly           = view_property
    external           = derived_property
    memo               = cached_property
    method             = dynamic_method
