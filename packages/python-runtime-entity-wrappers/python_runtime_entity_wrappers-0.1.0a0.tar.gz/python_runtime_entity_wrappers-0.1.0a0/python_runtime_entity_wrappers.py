# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import sys
from types import BuiltinFunctionType, FunctionType, ModuleType

from typing import Text, Union

if sys.version_info < (3,):
    from types import ClassType

    CLASS_TYPES = (ClassType, type)
    CLASS_TYPES_TYPE_ANNOTATION = Union[ClassType, type]
else:
    CLASS_TYPES = (type,)
    CLASS_TYPES_TYPE_ANNOTATION = type


class PythonRuntimeEntityWrapper(object): pass


class Module(PythonRuntimeEntityWrapper):
    """
    Represents a Python module.
    Two Module objects are equal if they wrap the same module instance.
    Comparison and hashing utilize the wrapped module instance.
    """
    __slots__ = ('module_instance',)

    def __new__(
            cls,
            module_instance,  # type: ModuleType
    ):
        if not isinstance(module_instance, ModuleType):
            raise TypeError

        self = super(Module, cls).__new__(cls)
        self.module_instance = module_instance
        return self

    def __reduce__(self):
        return self.__class__, (self.module_instance,)

    def __hash__(self):
        return hash(self.__reduce__())

    def __eq__(self, other):
        return isinstance(other, Module) and self.module_instance == other.module_instance

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.module_instance)


class Class(PythonRuntimeEntityWrapper):
    """
    Represents a Python class.
    Two Class objects are equal if they wrap the same class instance.
    Comparison and hashing utilize the wrapped class instance.
    """
    __slots__ = ('class_instance',)

    def __new__(
            cls,
            class_instance,  # type: CLASS_TYPES_TYPE_ANNOTATION
    ):
        if not isinstance(class_instance, CLASS_TYPES):
            raise TypeError

        self = super(Class, cls).__new__(cls)
        self.class_instance = class_instance
        return self

    def __reduce__(self):
        return self.__class__, (self.class_instance,)

    def __hash__(self):
        return hash(self.__reduce__())

    def __eq__(self, other):
        return isinstance(other, Class) and self.class_instance == other.class_instance

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.class_instance)


class Function(PythonRuntimeEntityWrapper):
    """
    Represents a Python function.
    Two Function objects are equal if they wrap the same function instance.
    Comparison and hashing utilize the wrapped function instance.
    """
    __slots__ = ('function_instance',)

    def __new__(
            cls,
            function_instance,  # type: Union[BuiltinFunctionType, FunctionType]
    ):
        if not isinstance(function_instance, (BuiltinFunctionType, FunctionType)):
            raise TypeError

        self = super(Function, cls).__new__(cls)
        self.function_instance = function_instance
        return self

    def __reduce__(self):
        return self.__class__, (self.function_instance,)

    def __hash__(self):
        return hash(self.__reduce__())

    def __eq__(self, other):
        return isinstance(other, Function) and self.function_instance == other.function_instance

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.function_instance)


class Constant(PythonRuntimeEntityWrapper):
    """
    Represents a constant value (int, float, complex, Text, bytes, None, Ellipsis).
    Two Constant objects are equal if their wrapped values are equal.
    Comparison and hashing utilize the wrapped value.
    """
    __slots__ = ('value',)

    def __new__(
            cls,
            value,  # type: Union[int, float, complex, Text, bytes, type(None), type(Ellipsis)]
    ):
        if not isinstance(value, (int, float, complex, Text, bytes, type(None), type(Ellipsis))):
            raise TypeError

        self = super(Constant, cls).__new__(cls)
        self.value = value
        return self

    def __reduce__(self):
        return self.__class__, (self.value,)

    def __hash__(self):
        return hash(self.__reduce__())

    def __eq__(self, other):
        return isinstance(other, Constant) and self.value == other.value

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.value)


class AbstractInstance(PythonRuntimeEntityWrapper):
    """
    Represents an abstract instance of a Python class.
    This does not wrap a concrete instance. Instead, AbstractInstance(MyClass) denotes an abstract, unnamed 'object of MyClass'.
    Each AbstractInstance(MyClass) is distinct from every other AbstractInstance(MyClass) (identity equality).
    """
    __slots__ = ('class_instance',)

    def __new__(
            cls,
            class_instance,  # type: CLASS_TYPES_TYPE_ANNOTATION
    ):
        if not isinstance(class_instance, CLASS_TYPES):
            raise TypeError

        self = super(AbstractInstance, cls).__new__(cls)
        self.class_instance = class_instance
        return self

    def __repr__(self):
        return '<%s(%r) at 0x%x>' % (self.__class__.__name__, self.class_instance, id(self))
