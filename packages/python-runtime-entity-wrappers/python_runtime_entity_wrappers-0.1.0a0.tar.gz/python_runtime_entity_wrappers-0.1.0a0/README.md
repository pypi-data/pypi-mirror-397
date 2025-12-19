# `python-runtime-entity-wrappers`

A set of small classes to represent Python runtime objects - **modules, classes, functions, constants, and abstract
instances** - in a structured and consistent way. This is especially useful for symbolic interpreters, type systems, or
metaprogramming tasks where you need clear semantics of identity and equality for runtime terms.

## Classes

| Wrapper          | What it Represents                                 | Comparison Semantics                          |
|------------------|----------------------------------------------------|-----------------------------------------------|
| Module           | Python module objects                              | By module instance                            |
| Class            | Python class/type objects                          | By class instance                             |
| Function         | Python function or built-in function               | By function instance                          |
| Constant         | Immutable primitive values                         | By value                                      |
| AbstractInstance | *Abstract* instance of a class (not a real object) | By identity (each AbstractInstance is unique) |

---

## Usage

```python
from python_runtime_entity_wrappers import Module, Class, Function, Constant, AbstractInstance

import math

# Module: refers to the 'math' module object
m1 = Module(math)
m2 = Module(math)
assert m1 == m2


# Class: refers to a Python class
class MyClass: pass


c1 = Class(MyClass)
c2 = Class(MyClass)
assert c1 == c2


# Function: refers to a Python function
def foo(): return 42


f1 = Function(foo)
f2 = Function(foo)
assert f1 == f2

# Constant: refers to a literal/primitive value
k1 = Constant(123)
k2 = Constant(123)
assert k1 == k2

# AbstractInstance: refers to an *abstract* instance of a class (not a real Python object)
i1 = AbstractInstance(MyClass)
i2 = AbstractInstance(MyClass)
assert i1 != i2  # Each AbstractInstance(...) is unique (identity equality)
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).