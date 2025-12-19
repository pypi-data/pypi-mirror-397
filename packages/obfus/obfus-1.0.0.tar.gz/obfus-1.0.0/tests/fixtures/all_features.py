#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Python feature test fixture.
This module tests ALL Python features to ensure obfuscation doesn't break functionality.
The output is deterministic and can be compared before/after obfuscation.
"""

import abc
import asyncio
import contextlib
import functools
import itertools
import operator
import sys
import threading
import weakref
from collections import OrderedDict, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum, Flag, IntEnum, auto
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generator,
    Generic,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)

# ============================================================================
# SECTION 1: Basic Functions and Closures
# ============================================================================

def simple_function(x: int, y: int) -> int:
    """Simple function with type hints."""
    return x + y


def function_with_defaults(a: int, b: int = 10, c: int = 20) -> int:
    """Function with default arguments."""
    return a + b + c


def function_with_args_kwargs(*args: int, **kwargs: int) -> Tuple[int, int]:
    """Function with *args and **kwargs."""
    return (sum(args), sum(kwargs.values()))


def closure_factory(multiplier: int) -> Callable[[int], int]:
    """Factory function that creates closures."""
    def inner(x: int) -> int:
        return x * multiplier
    return inner


def nested_closures(a: int) -> Callable[[], Callable[[], int]]:
    """Deeply nested closures."""
    def level1() -> Callable[[], int]:
        b = a + 1
        def level2() -> int:
            c = b + 1
            return a + b + c
        return level2
    return level1


# ============================================================================
# SECTION 2: Generators and Iterators
# ============================================================================

def simple_generator(n: int) -> Generator[int, None, None]:
    """Simple generator function."""
    for i in range(n):
        yield i * 2


def generator_with_send() -> Generator[int, int, str]:
    """Generator that accepts sent values."""
    total = 0
    while True:
        received = yield total
        if received is None:
            break
        total += received
    return f"final:{total}"


def nested_generator(n: int) -> Generator[int, None, None]:
    """Generator using yield from."""
    yield from range(n)
    yield from (x * x for x in range(n))


class CustomIterator:
    """Custom iterator class."""

    def __init__(self, limit: int):
        self.limit = limit
        self.current = 0

    def __iter__(self) -> 'CustomIterator':
        return self

    def __next__(self) -> int:
        if self.current >= self.limit:
            raise StopIteration
        result = self.current * 3
        self.current += 1
        return result


class CustomIterable:
    """Custom iterable that returns an iterator."""

    def __init__(self, data: List[int]):
        self._data = data

    def __iter__(self) -> Iterator[int]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


# ============================================================================
# SECTION 3: Decorators
# ============================================================================

def simple_decorator(func: Callable) -> Callable:
    """Simple decorator that wraps a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs) + 1
    return wrapper


def decorator_with_args(multiplier: int) -> Callable:
    """Decorator factory with arguments."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs) * multiplier
        return wrapper
    return decorator


def class_decorator(cls: type) -> type:
    """Decorator for classes."""
    cls.decorated = True
    cls.decoration_value = 42
    return cls


class DecoratorClass:
    """Class that can be used as a decorator."""

    def __init__(self, prefix: str):
        self.prefix = prefix

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return f"{self.prefix}:{result}"
        return wrapper


@simple_decorator
def decorated_function(x: int) -> int:
    """Function with simple decorator."""
    return x * 2


@decorator_with_args(3)
def decorated_with_args(x: int) -> int:
    """Function with parameterized decorator."""
    return x + 1


@DecoratorClass("result")
def decorated_with_class(x: int) -> str:
    """Function decorated with class decorator."""
    return str(x * 10)


# ============================================================================
# SECTION 4: Classes and Inheritance
# ============================================================================

class BaseClass:
    """Base class with various features."""

    class_variable: ClassVar[int] = 100

    def __init__(self, value: int):
        self.value = value
        self._private = value * 2
        self.__mangled = value * 3

    def instance_method(self) -> int:
        return self.value + self._private

    @classmethod
    def class_method(cls) -> int:
        return cls.class_variable

    @staticmethod
    def static_method(x: int) -> int:
        return x * 4

    @property
    def computed_property(self) -> int:
        return self.value * 5

    @computed_property.setter
    def computed_property(self, value: int) -> None:
        self.value = value // 5

    def __repr__(self) -> str:
        return f"BaseClass({self.value})"

    def __add__(self, other: 'BaseClass') -> 'BaseClass':
        return BaseClass(self.value + other.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseClass):
            return NotImplemented
        return self.value == other.value


class DerivedClass(BaseClass):
    """Derived class with method overriding."""

    def __init__(self, value: int, extra: int):
        super().__init__(value)
        self.extra = extra

    def instance_method(self) -> int:
        return super().instance_method() + self.extra

    def derived_only_method(self) -> int:
        return self.extra * 2


class MixinA:
    """Mixin class A."""

    def mixin_a_method(self) -> str:
        return "mixin_a"


class MixinB:
    """Mixin class B."""

    def mixin_b_method(self) -> str:
        return "mixin_b"


class MultipleInheritance(DerivedClass, MixinA, MixinB):
    """Class with multiple inheritance."""

    def combined_method(self) -> str:
        return f"{self.mixin_a_method()}_{self.mixin_b_method()}_{self.value}"


# ============================================================================
# SECTION 5: Metaclasses
# ============================================================================

class SimpleMeta(type):
    """Simple metaclass."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> type:
        namespace['meta_added'] = 'added_by_meta'
        namespace['meta_value'] = 999
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name: str, bases: tuple, namespace: dict) -> None:
        super().__init__(name, bases, namespace)
        cls.init_by_meta = True


class RegistryMeta(type):
    """Metaclass that registers all classes."""

    registry: Dict[str, type] = {}

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> type:
        cls = super().__new__(mcs, name, bases, namespace)
        mcs.registry[name] = cls
        return cls


class MetaclassUser(metaclass=SimpleMeta):
    """Class using SimpleMeta metaclass."""

    def __init__(self, value: int):
        self.value = value

    def get_meta_info(self) -> Tuple[str, int, bool]:
        return (self.meta_added, self.meta_value, self.init_by_meta)


class RegisteredClassA(metaclass=RegistryMeta):
    """First registered class."""
    pass


class RegisteredClassB(metaclass=RegistryMeta):
    """Second registered class."""
    pass


# ============================================================================
# SECTION 6: Abstract Base Classes and Protocols
# ============================================================================

class AbstractBase(abc.ABC):
    """Abstract base class."""

    @abc.abstractmethod
    def abstract_method(self) -> int:
        """Must be implemented by subclasses."""
        pass

    @abc.abstractproperty
    def abstract_property(self) -> str:
        """Abstract property."""
        pass

    def concrete_method(self) -> str:
        return "concrete"


class ConcreteImplementation(AbstractBase):
    """Concrete implementation of abstract class."""

    def __init__(self, value: int):
        self._value = value

    def abstract_method(self) -> int:
        return self._value * 2

    @property
    def abstract_property(self) -> str:
        return f"property:{self._value}"


class SupportsAdd(Protocol):
    """Protocol for objects that support addition."""

    def __add__(self, other: Any) -> Any:
        ...


def add_objects(a: SupportsAdd, b: SupportsAdd) -> Any:
    """Function using Protocol type hint."""
    return a + b


# ============================================================================
# SECTION 7: Enums
# ============================================================================

class Color(Enum):
    """Simple enum."""
    RED = 1
    GREEN = 2
    BLUE = 3


class Priority(IntEnum):
    """Integer enum."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Permission(Flag):
    """Flag enum for bitwise operations."""
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()
    ALL = READ | WRITE | EXECUTE


class StatusWithMethod(Enum):
    """Enum with custom methods."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

    def is_terminal(self) -> bool:
        return self == StatusWithMethod.COMPLETED

    @classmethod
    def from_string(cls, s: str) -> 'StatusWithMethod':
        return cls(s.lower())


# ============================================================================
# SECTION 8: Dataclasses
# ============================================================================

@dataclass
class SimpleDataclass:
    """Simple dataclass."""
    name: str
    value: int
    active: bool = True


@dataclass(frozen=True)
class FrozenDataclass:
    """Immutable dataclass."""
    id: int
    data: str


@dataclass
class DataclassWithFactory:
    """Dataclass with field factories."""
    name: str
    items: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.computed = len(self.name) + len(self.items)


@dataclass
class NestedDataclass:
    """Dataclass containing other dataclasses."""
    simple: SimpleDataclass
    frozen: FrozenDataclass
    extra: int = 0


# ============================================================================
# SECTION 9: Context Managers
# ============================================================================

class SimpleContextManager:
    """Simple context manager class."""

    def __init__(self, name: str):
        self.name = name
        self.entered = False
        self.exited = False

    def __enter__(self) -> 'SimpleContextManager':
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.exited = True
        return False


@contextlib.contextmanager
def generator_context_manager(value: int) -> Generator[int, None, None]:
    """Context manager using generator."""
    setup_value = value * 2
    try:
        yield setup_value
    finally:
        pass  # Cleanup would go here


class AsyncContextManager:
    """Async context manager."""

    def __init__(self, value: int):
        self.value = value
        self.entered = False

    async def __aenter__(self) -> int:
        self.entered = True
        await asyncio.sleep(0)
        return self.value * 3

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False


# ============================================================================
# SECTION 10: Async/Await
# ============================================================================

async def simple_async_function(x: int) -> int:
    """Simple async function."""
    await asyncio.sleep(0)
    return x * 2


async def async_with_multiple_awaits(values: List[int]) -> List[int]:
    """Async function with multiple awaits."""
    results = []
    for v in values:
        await asyncio.sleep(0)
        results.append(v * 3)
    return results


async def async_generator(n: int):
    """Async generator."""
    for i in range(n):
        await asyncio.sleep(0)
        yield i * 4


async def async_comprehension(n: int) -> List[int]:
    """Async comprehension."""
    return [x async for x in async_generator(n)]


async def gather_async_tasks(values: List[int]) -> List[int]:
    """Using asyncio.gather."""
    tasks = [simple_async_function(v) for v in values]
    results = await asyncio.gather(*tasks)
    return list(results)


async def async_context_usage(value: int) -> Tuple[bool, int]:
    """Using async context manager."""
    async with AsyncContextManager(value) as result:
        return (True, result)


# ============================================================================
# SECTION 11: Threading
# ============================================================================

class ThreadSafeCounter:
    """Thread-safe counter using locks."""

    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> None:
        with self._lock:
            self._value += 1

    def get_value(self) -> int:
        with self._lock:
            return self._value


def run_threaded_counter(num_threads: int, increments_per_thread: int) -> int:
    """Run counter increments in multiple threads."""
    counter = ThreadSafeCounter()

    def worker():
        for _ in range(increments_per_thread):
            counter.increment()

    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return counter.get_value()


def run_with_thread_pool(values: List[int]) -> List[int]:
    """Using ThreadPoolExecutor."""
    def process(x: int) -> int:
        return x * x

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process, values))
    return results


# ============================================================================
# SECTION 12: Descriptors
# ============================================================================

class TypedDescriptor:
    """Descriptor that enforces type checking."""

    def __init__(self, name: str, expected_type: type):
        self.name = name
        self.expected_type = expected_type
        self.private_name = f'_desc_{name}'

    def __get__(self, obj, objtype=None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}, got {type(value)}")
        setattr(obj, self.private_name, value)


class CachedProperty:
    """Descriptor implementing cached property."""

    def __init__(self, func: Callable):
        self.func = func
        self.attr_name = None

    def __set_name__(self, owner, name):
        self.attr_name = f'_cached_{name}'

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if not hasattr(obj, self.attr_name):
            setattr(obj, self.attr_name, self.func(obj))
        return getattr(obj, self.attr_name)


class DescriptorUser:
    """Class using custom descriptors."""

    typed_value = TypedDescriptor('typed_value', int)

    def __init__(self, value: int):
        self.typed_value = value
        self._compute_count = 0

    @CachedProperty
    def expensive_computation(self) -> int:
        self._compute_count += 1
        return self.typed_value * 100


# ============================================================================
# SECTION 13: Generic Types
# ============================================================================

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


class GenericContainer(Generic[T]):
    """Generic container class."""

    def __init__(self, value: T):
        self._value = value

    def get(self) -> T:
        return self._value

    def set(self, value: T) -> None:
        self._value = value

    def map(self, func: Callable[[T], T]) -> 'GenericContainer[T]':
        return GenericContainer(func(self._value))


class GenericPair(Generic[K, V]):
    """Generic pair with two type parameters."""

    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value

    def swap(self) -> 'GenericPair[V, K]':
        return GenericPair(self.value, self.key)

    def as_tuple(self) -> Tuple[K, V]:
        return (self.key, self.value)


class BoundedGeneric(Generic[T]):
    """Generic with bounded type operations."""

    def __init__(self, items: List[T]):
        self.items = items

    def first(self) -> Optional[T]:
        return self.items[0] if self.items else None

    def last(self) -> Optional[T]:
        return self.items[-1] if self.items else None


# ============================================================================
# SECTION 14: Special Methods (Dunder Methods)
# ============================================================================

class FullFeaturedClass:
    """Class implementing many special methods."""

    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"FullFeaturedClass({self.value})"

    def __str__(self) -> str:
        return f"Value: {self.value}"

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FullFeaturedClass):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other: 'FullFeaturedClass') -> bool:
        return self.value < other.value

    def __le__(self, other: 'FullFeaturedClass') -> bool:
        return self.value <= other.value

    def __add__(self, other: 'FullFeaturedClass') -> 'FullFeaturedClass':
        return FullFeaturedClass(self.value + other.value)

    def __sub__(self, other: 'FullFeaturedClass') -> 'FullFeaturedClass':
        return FullFeaturedClass(self.value - other.value)

    def __mul__(self, other: int) -> 'FullFeaturedClass':
        return FullFeaturedClass(self.value * other)

    def __truediv__(self, other: int) -> 'FullFeaturedClass':
        return FullFeaturedClass(self.value // other)

    def __neg__(self) -> 'FullFeaturedClass':
        return FullFeaturedClass(-self.value)

    def __abs__(self) -> 'FullFeaturedClass':
        return FullFeaturedClass(abs(self.value))

    def __bool__(self) -> bool:
        return self.value != 0

    def __int__(self) -> int:
        return self.value

    def __float__(self) -> float:
        return float(self.value)

    def __len__(self) -> int:
        return abs(self.value)

    def __getitem__(self, key: int) -> int:
        return self.value + key

    def __setitem__(self, key: int, value: int) -> None:
        self.value = value - key

    def __contains__(self, item: int) -> bool:
        return 0 <= item <= self.value

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.value))

    def __call__(self, x: int) -> int:
        return self.value + x


# ============================================================================
# SECTION 15: Collections and Data Structures
# ============================================================================

def test_builtin_collections() -> Dict[str, Any]:
    """Test built-in collection types."""
    results = {}

    # List operations
    lst = [3, 1, 4, 1, 5, 9, 2, 6]
    results['list_sorted'] = sorted(lst)
    results['list_reversed'] = list(reversed(lst))
    results['list_comprehension'] = [x * 2 for x in lst if x > 3]

    # Dict operations
    dct = {'a': 1, 'b': 2, 'c': 3}
    results['dict_keys'] = sorted(dct.keys())
    results['dict_values'] = sorted(dct.values())
    results['dict_comprehension'] = {k: v * 2 for k, v in dct.items()}

    # Set operations
    set1 = {1, 2, 3, 4, 5}
    set2 = {4, 5, 6, 7, 8}
    results['set_union'] = sorted(set1 | set2)
    results['set_intersection'] = sorted(set1 & set2)
    results['set_difference'] = sorted(set1 - set2)

    # Tuple operations
    tpl = (1, 2, 3, 4, 5)
    results['tuple_slice'] = tpl[1:4]
    results['tuple_concat'] = tpl + (6, 7)

    return results


def test_collections_module() -> Dict[str, Any]:
    """Test collections module types."""
    results = {}

    # defaultdict
    dd = defaultdict(list)
    for i, c in enumerate("abcabc"):
        dd[c].append(i)
    results['defaultdict'] = dict(dd)

    # OrderedDict
    od = OrderedDict()
    od['first'] = 1
    od['second'] = 2
    od['third'] = 3
    results['ordereddict_keys'] = list(od.keys())

    # deque
    dq = deque([1, 2, 3], maxlen=5)
    dq.append(4)
    dq.appendleft(0)
    results['deque'] = list(dq)

    return results


def test_itertools_operations() -> Dict[str, Any]:
    """Test itertools functions."""
    results = {}

    # chain
    results['chain'] = list(itertools.chain([1, 2], [3, 4], [5, 6]))

    # combinations
    results['combinations'] = list(itertools.combinations([1, 2, 3, 4], 2))

    # permutations
    results['permutations'] = list(itertools.permutations([1, 2, 3], 2))

    # groupby
    data = [('a', 1), ('a', 2), ('b', 3), ('b', 4)]
    grouped = {k: list(v) for k, v in itertools.groupby(data, key=lambda x: x[0])}
    results['groupby'] = grouped

    # accumulate
    results['accumulate'] = list(itertools.accumulate([1, 2, 3, 4, 5]))

    # product
    results['product'] = list(itertools.product([1, 2], ['a', 'b']))

    return results


# ============================================================================
# SECTION 16: Functional Programming
# ============================================================================

def test_functools_operations() -> Dict[str, Any]:
    """Test functools functions."""
    results = {}

    # reduce
    results['reduce_sum'] = functools.reduce(operator.add, [1, 2, 3, 4, 5])
    results['reduce_mul'] = functools.reduce(operator.mul, [1, 2, 3, 4, 5])

    # partial
    def power(base, exp):
        return base ** exp
    square = functools.partial(power, exp=2)
    cube = functools.partial(power, exp=3)
    results['partial_square'] = square(5)
    results['partial_cube'] = cube(3)

    # lru_cache effect
    @functools.lru_cache(maxsize=128)
    def fib(n):
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)

    results['fib_20'] = fib(20)

    return results


def test_lambda_and_map() -> Dict[str, Any]:
    """Test lambda functions and map/filter."""
    results = {}

    # Lambda
    double = lambda x: x * 2
    results['lambda_double'] = double(5)

    # map
    results['map_squares'] = list(map(lambda x: x ** 2, range(5)))

    # filter
    results['filter_even'] = list(filter(lambda x: x % 2 == 0, range(10)))

    # Nested lambdas
    compose = lambda f, g: lambda x: f(g(x))
    add_one = lambda x: x + 1
    multiply_two = lambda x: x * 2
    composed = compose(add_one, multiply_two)
    results['composed'] = composed(5)

    return results


# ============================================================================
# SECTION 17: Exception Handling
# ============================================================================

class CustomException(Exception):
    """Custom exception class."""

    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.code = code


class ChainedException(Exception):
    """Exception for chaining."""
    pass


def test_exception_handling() -> Dict[str, Any]:
    """Test exception handling features."""
    results = {}

    # Basic try/except
    try:
        x = 1 / 0
    except ZeroDivisionError:
        results['basic_except'] = "caught"

    # Multiple except clauses
    def multi_except(value):
        try:
            if value == 0:
                raise ValueError("zero")
            if value < 0:
                raise TypeError("negative")
            return value * 2
        except ValueError:
            return "value_error"
        except TypeError:
            return "type_error"

    results['multi_except_0'] = multi_except(0)
    results['multi_except_neg'] = multi_except(-1)
    results['multi_except_pos'] = multi_except(5)

    # try/except/else/finally
    def full_try_block(value):
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

    results['full_try_success'] = full_try_block(2)
    results['full_try_fail'] = full_try_block(0)

    # Exception chaining
    def chained_exception():
        try:
            try:
                raise ValueError("original")
            except ValueError as e:
                raise ChainedException("chained") from e
        except ChainedException as e:
            return (str(e), str(e.__cause__))

    results['chained'] = chained_exception()

    # Custom exception
    def custom_exception_test():
        try:
            raise CustomException("test error", 42)
        except CustomException as e:
            return (str(e), e.code)

    results['custom_exception'] = custom_exception_test()

    return results


# ============================================================================
# SECTION 18: String Operations
# ============================================================================

def test_string_operations() -> Dict[str, Any]:
    """Test string operations."""
    results = {}

    # Basic operations
    s = "Hello, World!"
    results['upper'] = s.upper()
    results['lower'] = s.lower()
    results['split'] = s.split(', ')
    results['replace'] = s.replace('World', 'Python')

    # f-strings
    name = "test"
    value = 42
    results['fstring'] = f"name={name}, value={value}"
    results['fstring_expr'] = f"computed={value * 2}"
    results['fstring_format'] = f"padded={value:05d}"

    # String methods
    results['strip'] = "  hello  ".strip()
    results['join'] = "-".join(['a', 'b', 'c'])
    results['startswith'] = s.startswith('Hello')
    results['endswith'] = s.endswith('!')

    # Unicode
    results['unicode'] = "Hello, \u4e16\u754c!"
    results['emoji'] = "Python \U0001F40D"

    return results


# ============================================================================
# SECTION 19: Slots and Memory Optimization
# ============================================================================

class SlottedClass:
    """Class using __slots__ for memory optimization."""

    __slots__ = ['x', 'y', 'z']

    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def sum(self) -> int:
        return self.x + self.y + self.z


class InheritedSlots(SlottedClass):
    """Class inheriting from slotted class."""

    __slots__ = ['w']

    def __init__(self, x: int, y: int, z: int, w: int):
        super().__init__(x, y, z)
        self.w = w

    def sum(self) -> int:
        return super().sum() + self.w


# ============================================================================
# SECTION 20: Weak References
# ============================================================================

class WeakRefTarget:
    """Class that can be weakly referenced."""

    def __init__(self, value: int):
        self.value = value

    def get_value(self) -> int:
        return self.value


def test_weak_references() -> Dict[str, Any]:
    """Test weak reference functionality."""
    results = {}

    obj = WeakRefTarget(42)
    ref = weakref.ref(obj)

    results['ref_alive'] = ref() is not None
    results['ref_value'] = ref().value if ref() else None

    return results


# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def run_all_tests() -> Dict[str, Any]:
    """Run all tests and return results."""
    results = OrderedDict()

    # Section 1: Basic Functions
    results['simple_function'] = simple_function(3, 4)
    results['function_defaults'] = function_with_defaults(5)
    results['function_args_kwargs'] = function_with_args_kwargs(1, 2, 3, x=10, y=20)
    results['closure'] = closure_factory(5)(10)
    results['nested_closure'] = nested_closures(1)()()

    # Section 2: Generators and Iterators
    results['simple_generator'] = list(simple_generator(5))
    results['nested_generator'] = list(nested_generator(3))
    results['custom_iterator'] = list(CustomIterator(5))
    results['custom_iterable'] = list(CustomIterable([1, 2, 3, 4]))

    # Generator with send
    gen = generator_with_send()
    next(gen)
    gen.send(10)
    gen.send(20)
    try:
        gen.send(None)
    except StopIteration as e:
        results['generator_send'] = e.value

    # Section 3: Decorators
    results['decorated_function'] = decorated_function(5)
    results['decorated_with_args'] = decorated_with_args(5)
    results['decorated_with_class'] = decorated_with_class(5)

    # Section 4: Classes
    base = BaseClass(10)
    results['base_instance_method'] = base.instance_method()
    results['base_class_method'] = BaseClass.class_method()
    results['base_static_method'] = BaseClass.static_method(5)
    results['base_property'] = base.computed_property
    results['base_add'] = (base + BaseClass(5)).value

    derived = DerivedClass(10, 5)
    results['derived_method'] = derived.instance_method()
    results['derived_only'] = derived.derived_only_method()

    multi = MultipleInheritance(10, 5)
    results['multiple_inheritance'] = multi.combined_method()

    # Section 5: Metaclasses
    meta_user = MetaclassUser(42)
    results['metaclass_info'] = meta_user.get_meta_info()
    results['registry_classes'] = sorted(RegistryMeta.registry.keys())

    # Section 6: Abstract classes
    concrete = ConcreteImplementation(25)
    results['abstract_method'] = concrete.abstract_method()
    results['abstract_property'] = concrete.abstract_property
    results['concrete_method'] = concrete.concrete_method()

    # Section 7: Enums
    results['enum_value'] = Color.RED.value
    results['int_enum'] = Priority.HIGH + Priority.LOW
    results['flag_enum'] = (Permission.READ | Permission.WRITE).value
    results['enum_method'] = StatusWithMethod.COMPLETED.is_terminal()

    # Section 8: Dataclasses
    simple_dc = SimpleDataclass("test", 42)
    results['dataclass_name'] = simple_dc.name
    results['dataclass_value'] = simple_dc.value

    frozen_dc = FrozenDataclass(1, "frozen")
    results['frozen_id'] = frozen_dc.id

    factory_dc = DataclassWithFactory("hello", [1, 2, 3])
    results['factory_computed'] = factory_dc.computed

    nested_dc = NestedDataclass(simple_dc, frozen_dc, 100)
    results['nested_extra'] = nested_dc.extra

    # Section 9: Context Managers
    with SimpleContextManager("test") as cm:
        results['context_entered'] = cm.entered
    results['context_exited'] = cm.exited

    with generator_context_manager(10) as value:
        results['generator_context'] = value

    # Section 10: Async
    results['async_simple'] = asyncio.run(simple_async_function(5))
    results['async_multiple'] = asyncio.run(async_with_multiple_awaits([1, 2, 3]))
    results['async_comprehension'] = asyncio.run(async_comprehension(4))
    results['async_gather'] = asyncio.run(gather_async_tasks([1, 2, 3]))
    results['async_context'] = asyncio.run(async_context_usage(10))

    # Section 11: Threading
    results['threaded_counter'] = run_threaded_counter(4, 100)
    results['thread_pool'] = run_with_thread_pool([1, 2, 3, 4, 5])

    # Section 12: Descriptors
    desc_user = DescriptorUser(10)
    results['typed_descriptor'] = desc_user.typed_value
    results['cached_property'] = desc_user.expensive_computation
    _ = desc_user.expensive_computation  # Access again
    results['cached_compute_count'] = desc_user._compute_count

    # Section 13: Generics
    container = GenericContainer(42)
    results['generic_get'] = container.get()
    results['generic_map'] = container.map(lambda x: x * 2).get()

    pair = GenericPair("key", 100)
    results['generic_pair'] = pair.as_tuple()
    results['generic_swap'] = pair.swap().as_tuple()

    bounded = BoundedGeneric([1, 2, 3, 4, 5])
    results['bounded_first'] = bounded.first()
    results['bounded_last'] = bounded.last()

    # Section 14: Special Methods
    ff = FullFeaturedClass(10)
    results['repr'] = repr(ff)
    results['str'] = str(ff)
    results['hash'] = hash(ff) == hash(FullFeaturedClass(10))
    results['eq'] = ff == FullFeaturedClass(10)
    results['lt'] = ff < FullFeaturedClass(20)
    results['add'] = (ff + FullFeaturedClass(5)).value
    results['mul'] = (ff * 3).value
    results['neg'] = (-ff).value
    results['abs'] = abs(FullFeaturedClass(-5)).value
    results['bool'] = bool(ff)
    results['int'] = int(ff)
    results['len'] = len(ff)
    results['getitem'] = ff[5]
    results['contains'] = 5 in ff
    results['iter'] = list(ff)
    results['call'] = ff(5)

    # Section 15: Collections
    results['builtin_collections'] = test_builtin_collections()
    results['collections_module'] = test_collections_module()
    results['itertools'] = test_itertools_operations()

    # Section 16: Functional
    results['functools'] = test_functools_operations()
    results['lambda_map'] = test_lambda_and_map()

    # Section 17: Exceptions
    results['exceptions'] = test_exception_handling()

    # Section 18: Strings
    results['strings'] = test_string_operations()

    # Section 19: Slots
    slotted = SlottedClass(1, 2, 3)
    results['slotted_sum'] = slotted.sum()

    inherited_slots = InheritedSlots(1, 2, 3, 4)
    results['inherited_slots_sum'] = inherited_slots.sum()

    # Section 20: Weak References
    results['weak_refs'] = test_weak_references()

    return results


def format_results(results: Dict[str, Any], indent: int = 0) -> str:
    """Format results for display."""
    lines = []
    prefix = "  " * indent
    for key, value in results.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(format_results(value, indent + 1))
        else:
            lines.append(f"{prefix}{key}: {value!r}")
    return "\n".join(lines)


if __name__ == "__main__":
    results = run_all_tests()
    print("=" * 70)
    print("ALL PYTHON FEATURES TEST RESULTS")
    print("=" * 70)
    print(format_results(results))
    print("=" * 70)
    print(f"Total test categories: {len(results)}")
