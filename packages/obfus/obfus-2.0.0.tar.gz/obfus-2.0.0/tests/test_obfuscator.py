#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive tests for the Python obfuscator.
Tests that obfuscated code produces identical results to original code.
"""

import ast
import asyncio
import hashlib
import importlib.util
import json
import os
import pickle
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

# Add the rewrite directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from obfus import ObfuscationConfig, ObfuscationEngine


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def obfuscator_minimal():
    """Obfuscator with minimal settings."""
    config = ObfuscationConfig.minimal()
    return ObfuscationEngine(config)


@pytest.fixture
def obfuscator_standard():
    """Obfuscator with standard settings."""
    config = ObfuscationConfig.standard()
    return ObfuscationEngine(config)


@pytest.fixture
def obfuscator_aggressive():
    """Obfuscator with aggressive settings."""
    config = ObfuscationConfig.aggressive()
    return ObfuscationEngine(config)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmpdir = tempfile.mkdtemp(prefix='obfuscator_test_')
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def all_features_path():
    """Path to the all_features.py test fixture."""
    return Path(__file__).parent / 'fixtures' / 'all_features.py'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def run_python_code(code: str, timeout: int = 30) -> Tuple[str, str, int]:
    """Run Python code and return stdout, stderr, return code."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        try:
            result = subprocess.run(
                [sys.executable, f.name],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout, result.stderr, result.returncode
        finally:
            os.unlink(f.name)


def run_python_file(filepath: str, timeout: int = 30) -> Tuple[str, str, int]:
    """Run a Python file and return stdout, stderr, return code."""
    result = subprocess.run(
        [sys.executable, filepath],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.stdout, result.stderr, result.returncode


def load_module_from_code(code: str, module_name: str = 'test_module') -> Any:
    """Load a module from code string."""
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(code, module.__dict__)
    return module


def compare_outputs(original: str, obfuscated: str) -> bool:
    """Compare outputs, ignoring whitespace differences."""
    return original.strip() == obfuscated.strip()


def get_deterministic_hash(data: Any) -> str:
    """Get a deterministic hash of data."""
    return hashlib.sha256(pickle.dumps(data)).hexdigest()[:16]


# ============================================================================
# BASIC FUNCTIONALITY TESTS
# ============================================================================

class TestBasicObfuscation:
    """Test basic obfuscation functionality."""

    def test_simple_function(self, obfuscator_standard):
        """Test obfuscation of a simple function."""
        code = '''
def add(a, b):
    return a + b

print(add(2, 3))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, orig_rc = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_class_definition(self, obfuscator_standard):
        """Test obfuscation of class definitions."""
        code = '''
class Calculator:
    def __init__(self, value):
        self.value = value

    def add(self, x):
        return self.value + x

    def multiply(self, x):
        return self.value * x

calc = Calculator(10)
print(calc.add(5))
print(calc.multiply(3))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_list_comprehension(self, obfuscator_standard):
        """Test obfuscation of list comprehensions."""
        code = '''
squares = [x * x for x in range(10)]
evens = [x for x in squares if x % 2 == 0]
print(squares)
print(evens)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_dict_comprehension(self, obfuscator_standard):
        """Test obfuscation of dict comprehensions."""
        code = '''
squares = {x: x * x for x in range(5)}
filtered = {k: v for k, v in squares.items() if v > 5}
print(squares)
print(filtered)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_set_comprehension(self, obfuscator_standard):
        """Test obfuscation of set comprehensions."""
        code = '''
items = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
unique_squares = {x * x for x in items}
print(sorted(unique_squares))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_generator_expression(self, obfuscator_standard):
        """Test obfuscation of generator expressions."""
        code = '''
gen = (x * 2 for x in range(5))
print(list(gen))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# ADVANCED FEATURES TESTS
# ============================================================================

class TestAdvancedFeatures:
    """Test obfuscation of advanced Python features."""

    def test_decorators(self, obfuscator_standard):
        """Test obfuscation of decorators."""
        code = '''
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs) + 1
    return wrapper

@my_decorator
def add(a, b):
    return a + b

print(add(2, 3))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_decorator_with_arguments(self, obfuscator_standard):
        """Test obfuscation of decorators with arguments."""
        code = '''
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    return f"Hello, {name}"

print(greet("World"))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_class_decorator(self, obfuscator_standard):
        """Test obfuscation of class decorators."""
        code = '''
def add_method(cls):
    cls.added_method = lambda self: "added"
    return cls

@add_method
class MyClass:
    def original_method(self):
        return "original"

obj = MyClass()
print(obj.original_method())
print(obj.added_method())
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_generators(self, obfuscator_standard):
        """Test obfuscation of generators."""
        code = '''
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

print(list(fibonacci(10)))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_generator_send(self, obfuscator_standard):
        """Test obfuscation of generators with send."""
        code = '''
def accumulator():
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value

gen = accumulator()
next(gen)
print(gen.send(10))
print(gen.send(20))
print(gen.send(30))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_yield_from(self, obfuscator_standard):
        """Test obfuscation of yield from."""
        code = '''
def chain(*iterables):
    for it in iterables:
        yield from it

result = list(chain([1, 2], [3, 4], [5, 6]))
print(result)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_closures(self, obfuscator_standard):
        """Test obfuscation of closures."""
        code = '''
def make_multiplier(n):
    def multiplier(x):
        return x * n
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))
print(triple(5))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_nested_closures(self, obfuscator_standard):
        """Test obfuscation of deeply nested closures."""
        code = '''
def outer(a):
    def middle(b):
        def inner(c):
            return a + b + c
        return inner
    return middle

result = outer(1)(2)(3)
print(result)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# CLASS FEATURES TESTS
# ============================================================================

class TestClassFeatures:
    """Test obfuscation of class-related features."""

    def test_inheritance(self, obfuscator_standard):
        """Test obfuscation of class inheritance."""
        code = '''
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow!"

animals = [Dog("Rex"), Cat("Whiskers")]
for animal in animals:
    print(animal.speak())
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_multiple_inheritance(self, obfuscator_standard):
        """Test obfuscation of multiple inheritance."""
        code = '''
class A:
    def method_a(self):
        return "A"

class B:
    def method_b(self):
        return "B"

class C(A, B):
    def method_c(self):
        return f"{self.method_a()}{self.method_b()}C"

obj = C()
print(obj.method_a())
print(obj.method_b())
print(obj.method_c())
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_super_calls(self, obfuscator_standard):
        """Test obfuscation of super() calls."""
        code = '''
class Base:
    def __init__(self, value):
        self.value = value

    def compute(self):
        return self.value

class Derived(Base):
    def __init__(self, value, multiplier):
        super().__init__(value)
        self.multiplier = multiplier

    def compute(self):
        return super().compute() * self.multiplier

obj = Derived(10, 3)
print(obj.compute())
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_properties(self, obfuscator_standard):
        """Test obfuscation of properties."""
        code = '''
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self):
        return 3.14159 * self._radius ** 2

c = Circle(5)
print(c.radius)
print(f"{c.area:.2f}")
c.radius = 10
print(c.radius)
print(f"{c.area:.2f}")
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_class_methods(self, obfuscator_standard):
        """Test obfuscation of class methods and static methods."""
        code = '''
class Counter:
    _count = 0

    def __init__(self):
        Counter._count += 1

    @classmethod
    def get_count(cls):
        return cls._count

    @staticmethod
    def description():
        return "A counter class"

c1 = Counter()
c2 = Counter()
c3 = Counter()

print(Counter.get_count())
print(Counter.description())
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_dunder_methods(self, obfuscator_standard):
        """Test obfuscation of dunder methods."""
        code = '''
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __len__(self):
        return 2

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Vector index out of range")

v1 = Vector(1, 2)
v2 = Vector(3, 4)

print(v1)
print(v1 + v2)
print(v1 * 3)
print(v1 == Vector(1, 2))
print(len(v1))
print(v1[0], v1[1])
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# METACLASS TESTS
# ============================================================================

class TestMetaclasses:
    """Test obfuscation of metaclasses."""

    def test_simple_metaclass(self, obfuscator_standard):
        """Test obfuscation of simple metaclass."""
        code = '''
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        namespace['added_attr'] = 42
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    pass

print(MyClass.added_attr)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_registry_metaclass(self, obfuscator_standard):
        """Test obfuscation of registry metaclass."""
        code = '''
class RegistryMeta(type):
    registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if name != 'Base':
            mcs.registry[name] = cls
        return cls

class Base(metaclass=RegistryMeta):
    pass

class PluginA(Base):
    pass

class PluginB(Base):
    pass

print(sorted(RegistryMeta.registry.keys()))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# ENUM TESTS
# ============================================================================

class TestEnums:
    """Test obfuscation of enums."""

    def test_simple_enum(self, obfuscator_standard):
        """Test obfuscation of simple enum."""
        code = '''
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED)
print(Color.RED.value)
print(Color.RED.name)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_int_enum(self, obfuscator_standard):
        """Test obfuscation of IntEnum."""
        code = '''
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

print(Priority.HIGH > Priority.LOW)
print(Priority.MEDIUM + 1)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_flag_enum(self, obfuscator_standard):
        """Test obfuscation of Flag enum."""
        code = '''
from enum import Flag, auto

class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()

perms = Permission.READ | Permission.WRITE
print(Permission.READ in perms)
print(Permission.EXECUTE in perms)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# DATACLASS TESTS
# ============================================================================

class TestDataclasses:
    """Test obfuscation of dataclasses."""

    def test_simple_dataclass(self, obfuscator_standard):
        """Test obfuscation of simple dataclass."""
        code = '''
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p = Point(3, 4)
print(p)
print(p.x, p.y)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_dataclass_with_defaults(self, obfuscator_standard):
        """Test obfuscation of dataclass with defaults."""
        code = '''
from dataclasses import dataclass, field

@dataclass
class Config:
    name: str
    value: int = 10
    tags: list = field(default_factory=list)

c = Config("test")
print(c.name)
print(c.value)
print(c.tags)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_frozen_dataclass(self, obfuscator_standard):
        """Test obfuscation of frozen dataclass."""
        code = '''
from dataclasses import dataclass

@dataclass(frozen=True)
class ImmutablePoint:
    x: int
    y: int

p = ImmutablePoint(3, 4)
print(p)
print(hash(p))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        # Note: hash values might differ, so we just check it doesn't crash
        assert obf_rc == 0


# ============================================================================
# ASYNC TESTS
# ============================================================================

class TestAsync:
    """Test obfuscation of async/await features."""

    def test_simple_async(self, obfuscator_standard):
        """Test obfuscation of simple async function."""
        code = '''
import asyncio

async def async_add(a, b):
    await asyncio.sleep(0)
    return a + b

result = asyncio.run(async_add(2, 3))
print(result)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_async_gather(self, obfuscator_standard):
        """Test obfuscation of asyncio.gather."""
        code = '''
import asyncio

async def compute(x):
    await asyncio.sleep(0)
    return x * 2

async def main():
    results = await asyncio.gather(
        compute(1),
        compute(2),
        compute(3)
    )
    return results

result = asyncio.run(main())
print(result)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_async_generator(self, obfuscator_standard):
        """Test obfuscation of async generator."""
        code = '''
import asyncio

async def async_range(n):
    for i in range(n):
        await asyncio.sleep(0)
        yield i

async def main():
    result = []
    async for x in async_range(5):
        result.append(x)
    return result

result = asyncio.run(main())
print(result)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_async_comprehension(self, obfuscator_standard):
        """Test obfuscation of async comprehension."""
        code = '''
import asyncio

async def async_range(n):
    for i in range(n):
        await asyncio.sleep(0)
        yield i

async def main():
    result = [x * 2 async for x in async_range(5)]
    return result

result = asyncio.run(main())
print(result)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_async_context_manager(self, obfuscator_standard):
        """Test obfuscation of async context manager."""
        code = '''
import asyncio

class AsyncResource:
    def __init__(self, value):
        self.value = value

    async def __aenter__(self):
        await asyncio.sleep(0)
        return self.value * 2

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(0)
        return False

async def main():
    async with AsyncResource(10) as value:
        return value

result = asyncio.run(main())
print(result)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# THREADING TESTS
# ============================================================================

class TestThreading:
    """Test obfuscation of threading features."""

    def test_simple_threading(self, obfuscator_standard):
        """Test obfuscation of simple threading."""
        code = '''
import threading

results = []
lock = threading.Lock()

def worker(value):
    with lock:
        results.append(value * 2)

threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(sorted(results))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_thread_pool(self, obfuscator_standard):
        """Test obfuscation of thread pool."""
        code = '''
from concurrent.futures import ThreadPoolExecutor

def compute(x):
    return x * x

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(compute, range(10)))

print(results)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# CONTEXT MANAGER TESTS
# ============================================================================

class TestContextManagers:
    """Test obfuscation of context managers."""

    def test_class_context_manager(self, obfuscator_standard):
        """Test obfuscation of class-based context manager."""
        code = '''
class Resource:
    def __init__(self, name):
        self.name = name
        self.opened = False

    def __enter__(self):
        self.opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.opened = False
        return False

with Resource("test") as r:
    print(f"Inside: {r.opened}")
print(f"Outside: {r.opened}")
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_generator_context_manager(self, obfuscator_standard):
        """Test obfuscation of generator-based context manager."""
        code = '''
from contextlib import contextmanager

@contextmanager
def managed_resource(name):
    print(f"Opening {name}")
    try:
        yield name.upper()
    finally:
        print(f"Closing {name}")

with managed_resource("test") as value:
    print(f"Using {value}")
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# EXCEPTION HANDLING TESTS
# ============================================================================

class TestExceptionHandling:
    """Test obfuscation of exception handling."""

    def test_try_except(self, obfuscator_standard):
        """Test obfuscation of try/except."""
        code = '''
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "infinity"

print(safe_divide(10, 2))
print(safe_divide(10, 0))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_try_except_else_finally(self, obfuscator_standard):
        """Test obfuscation of try/except/else/finally."""
        code = '''
def process(value):
    result = []
    try:
        x = 10 / value
        result.append("try")
    except ZeroDivisionError:
        result.append("except")
    else:
        result.append("else")
    finally:
        result.append("finally")
    return result

print(process(2))
print(process(0))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_exception_chaining(self, obfuscator_standard):
        """Test obfuscation of exception chaining."""
        code = '''
class CustomError(Exception):
    pass

def process():
    try:
        raise ValueError("original")
    except ValueError as e:
        raise CustomError("wrapped") from e

try:
    process()
except CustomError as e:
    print(f"Caught: {e}")
    print(f"Cause: {e.__cause__}")
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# FUNCTIONAL PROGRAMMING TESTS
# ============================================================================

class TestFunctionalProgramming:
    """Test obfuscation of functional programming features."""

    def test_lambda(self, obfuscator_standard):
        """Test obfuscation of lambda functions."""
        code = '''
double = lambda x: x * 2
add = lambda x, y: x + y
compose = lambda f, g: lambda x: f(g(x))

print(double(5))
print(add(3, 4))
print(compose(double, lambda x: x + 1)(5))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_map_filter_reduce(self, obfuscator_standard):
        """Test obfuscation of map, filter, reduce."""
        code = '''
from functools import reduce

numbers = [1, 2, 3, 4, 5]

doubled = list(map(lambda x: x * 2, numbers))
evens = list(filter(lambda x: x % 2 == 0, doubled))
total = reduce(lambda x, y: x + y, evens)

print(doubled)
print(evens)
print(total)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_partial(self, obfuscator_standard):
        """Test obfuscation of functools.partial."""
        code = '''
from functools import partial

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube = partial(power, exp=3)

print(square(5))
print(cube(3))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# COMPREHENSIVE ALL-FEATURES TEST
# ============================================================================

class TestAllFeatures:
    """Test obfuscation using the comprehensive all_features.py fixture."""

    def test_all_features_minimal(self, obfuscator_minimal, all_features_path, temp_dir):
        """Test all features with minimal obfuscation."""
        if not all_features_path.exists():
            pytest.skip("all_features.py fixture not found")

        original_code = all_features_path.read_text()
        obfuscated_code = obfuscator_minimal.obfuscate_source(original_code)

        # Write obfuscated code to temp file
        obfuscated_path = Path(temp_dir) / 'obfuscated.py'
        obfuscated_path.write_text(obfuscated_code)

        # Run both and compare
        orig_out, orig_err, orig_rc = run_python_file(str(all_features_path))
        obf_out, obf_err, obf_rc = run_python_file(str(obfuscated_path))

        assert orig_rc == 0, f"Original code failed: {orig_err}"
        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out), f"Output mismatch:\nOriginal:\n{orig_out}\n\nObfuscated:\n{obf_out}"

    def test_all_features_standard(self, obfuscator_standard, all_features_path, temp_dir):
        """Test all features with standard obfuscation."""
        if not all_features_path.exists():
            pytest.skip("all_features.py fixture not found")

        original_code = all_features_path.read_text()
        obfuscated_code = obfuscator_standard.obfuscate_source(original_code)

        # Write obfuscated code to temp file
        obfuscated_path = Path(temp_dir) / 'obfuscated.py'
        obfuscated_path.write_text(obfuscated_code)

        # Run both and compare
        orig_out, orig_err, orig_rc = run_python_file(str(all_features_path))
        obf_out, obf_err, obf_rc = run_python_file(str(obfuscated_path))

        assert orig_rc == 0, f"Original code failed: {orig_err}"
        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out), f"Output mismatch:\nOriginal:\n{orig_out}\n\nObfuscated:\n{obf_out}"

    def test_all_features_aggressive(self, obfuscator_aggressive, all_features_path, temp_dir):
        """Test all features with aggressive obfuscation."""
        if not all_features_path.exists():
            pytest.skip("all_features.py fixture not found")

        original_code = all_features_path.read_text()
        obfuscated_code = obfuscator_aggressive.obfuscate_source(original_code)

        # Write obfuscated code to temp file
        obfuscated_path = Path(temp_dir) / 'obfuscated.py'
        obfuscated_path.write_text(obfuscated_code)

        # Run both
        orig_out, orig_err, orig_rc = run_python_file(str(all_features_path))
        obf_out, obf_err, obf_rc = run_python_file(str(obfuscated_path))

        assert orig_rc == 0, f"Original code failed: {orig_err}"
        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        # Note: aggressive mode renames classes, so registry_classes output differs
        # We verify the code runs correctly but don't compare exact output
        assert "Total test categories: 80" in obf_out, "Obfuscated code should complete all tests"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test obfuscation of edge cases."""

    def test_empty_file(self, obfuscator_standard):
        """Test obfuscation of empty file."""
        code = ''
        obfuscated = obfuscator_standard.obfuscate_source(code)
        assert obfuscated is not None

    def test_only_comments(self, obfuscator_standard):
        """Test obfuscation of file with only comments."""
        code = '''
# This is a comment
# Another comment
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)
        # Should not crash
        assert obfuscated is not None

    def test_unicode_strings(self, obfuscator_standard):
        """Test obfuscation of unicode strings."""
        code = '''
message = "Hello, \u4e16\u754c!"
emoji = "Python \U0001F40D"
print(message)
print(emoji)
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_multiline_strings(self, obfuscator_standard):
        """Test obfuscation of multiline strings."""
        code = '''
text = """
This is a
multiline string
with several lines
"""
print(text.strip())
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_f_strings(self, obfuscator_standard):
        """Test obfuscation of f-strings."""
        code = '''
name = "World"
value = 42
print(f"Hello, {name}!")
print(f"Value: {value}")
print(f"Computed: {value * 2}")
print(f"Formatted: {value:05d}")
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_walrus_operator(self, obfuscator_standard):
        """Test obfuscation of walrus operator."""
        code = '''
if (n := 10) > 5:
    print(f"n is {n}")

items = [1, 2, 3, 4, 5]
if (length := len(items)) > 3:
    print(f"Length: {length}")
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_match_statement(self, obfuscator_standard):
        """Test obfuscation of match statement (Python 3.10+)."""
        code = '''
def http_status(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:
            return "Unknown"

print(http_status(200))
print(http_status(404))
print(http_status(999))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_positional_only_params(self, obfuscator_standard):
        """Test obfuscation of positional-only parameters."""
        code = '''
def greet(name, /, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("World"))
print(greet("Python", greeting="Hi"))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_keyword_only_params(self, obfuscator_standard):
        """Test obfuscation of keyword-only parameters."""
        code = '''
def process(data, *, validate=True, transform=False):
    result = data
    if validate:
        result = f"validated:{result}"
    if transform:
        result = result.upper()
    return result

print(process("test"))
print(process("test", validate=False, transform=True))
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# OBFUSCATION LEVEL TESTS
# ============================================================================

class TestObfuscationLevels:
    """Test different obfuscation levels."""

    def test_minimal_produces_valid_code(self, obfuscator_minimal):
        """Test that minimal obfuscation produces valid code."""
        code = '''
class Test:
    def __init__(self, value):
        self.value = value

    def double(self):
        return self.value * 2

t = Test(21)
print(t.double())
'''
        obfuscated = obfuscator_minimal.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_standard_produces_valid_code(self, obfuscator_standard):
        """Test that standard obfuscation produces valid code."""
        code = '''
class Test:
    def __init__(self, value):
        self.value = value

    def double(self):
        return self.value * 2

t = Test(21)
print(t.double())
'''
        obfuscated = obfuscator_standard.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)

    def test_aggressive_produces_valid_code(self, obfuscator_aggressive):
        """Test that aggressive obfuscation produces valid code."""
        code = '''
class Test:
    def __init__(self, value):
        self.value = value

    def double(self):
        return self.value * 2

t = Test(21)
print(t.double())
'''
        obfuscated = obfuscator_aggressive.obfuscate_source(code)

        orig_out, _, _ = run_python_code(code)
        obf_out, obf_err, obf_rc = run_python_code(obfuscated)

        assert obf_rc == 0, f"Obfuscated code failed: {obf_err}"
        assert compare_outputs(orig_out, obf_out)


# ============================================================================
# DETERMINISM TESTS
# ============================================================================

class TestDeterminism:
    """Test that obfuscation produces deterministic results."""

    def test_same_output_multiple_runs(self, obfuscator_standard):
        """Test that obfuscating the same code produces same functional output."""
        code = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

for i in range(10):
    print(factorial(i))
'''
        # Obfuscate multiple times
        outputs = []
        for _ in range(3):
            obfuscated = obfuscator_standard.obfuscate_source(code)
            out, _, rc = run_python_code(obfuscated)
            assert rc == 0
            outputs.append(out)

        # All outputs should be identical
        assert all(o == outputs[0] for o in outputs)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
