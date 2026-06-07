---
layout: post
title: "Python Fundamentals Cheatsheet"
description: >-
  Personal cheatsheet for Python fundamentals. Covers data types, collections, functions, OOP, exceptions, type hints, dataclasses, concurrency, and the standard library.
author: ryo
date: 2023-11-03 18:40:23 +0800
categories: [Software Engineering]
tags: [python, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. Data Types & Variables

```python
x: int = 42
y: float = 3.14
z: complex = 1 + 2j
b: bool = True        # True/False (capitalised)
n = None

# Type casting
int("42")             # 42
float("3.14")         # 3.14
str(42)               # "42"
bool(0)               # False
bool("hello")         # True

# Falsy values: 0, 0.0, "", [], {}, set(), None, False

# Multiple assignment
a, b, c = 1, 2, 3
a, *rest = [1, 2, 3, 4]   # a=1, rest=[2, 3, 4]
```

Python is **dynamically typed** - types are checked at runtime. Every variable is a reference to an object.

---

## 2. Strings

### 2.1. Literals & f-strings

```python
s = "hello"
s = 'hello'
s = """
multi
line
"""

name = "Ryo"
age = 25
f"{name} is {age}"            # "Ryo is 25"
f"{3.14159:.2f}"               # "3.14"
f"{1000000:,}"                 # "1,000,000"
f"{'hello':>10}"               # "     hello"
```

### 2.2. Common Methods

```python
s = "  Hello, World!  "

s.strip()                       # "Hello, World!"
s.lstrip() / s.rstrip()
s.lower() / s.upper()
s.title()                       # "Hello, World!" (capitalises each word)
s.replace("World", "Python")    # "  Hello, Python!  "
s.split(", ")                   # ["  Hello", "World!  "]
", ".join(["a", "b", "c"])      # "a, b, c"
s.startswith("  H")             # True
s.find("World")                 # 9  (-1 if not found)
s.count("l")                    # 3
"  ".isspace()                  # True
"123".isdigit()                 # True
```

### 2.3. Slicing

```python
s = "hello"
s[0]       # 'h'
s[-1]      # 'o'
s[1:3]     # 'el'
s[::2]     # 'hlo'   (every 2nd char)
s[::-1]    # 'olleh' (reverse)
```

Strings are immutable - slicing returns a new string.

---

## 3. Collections

### 3.1. List

Ordered, mutable, allows duplicates.

```python
lst = [1, 2, 3]
lst.append(4)
lst.extend([5, 6])
lst.insert(0, 0)          # insert value at index
lst.remove(3)             # remove first occurrence of value
lst.pop()                 # remove and return last
lst.pop(0)                # remove and return at index
lst.sort()                # in-place
sorted(lst)               # returns new sorted list
lst.reverse()
lst.index(2)              # index of first occurrence
len(lst)
2 in lst                  # True
lst[1:3]                  # slice
```

### 3.2. Tuple

Ordered, immutable.

```python
t = (1, 2, 3)
t = 1, 2, 3       # parentheses optional
t = (1,)          # single-element - trailing comma required
a, b, c = t       # unpacking

# Tuples are hashable if all elements are hashable - can be used as dict keys
```

### 3.3. Set

Unordered, no duplicates.

```python
s = {1, 2, 3}
s = set()           # empty set ({} creates a dict)
s.add(4)
s.discard(99)       # no error if missing
s.remove(1)         # KeyError if missing
3 in s              # O(1)

a = {1, 2, 3}
b = {2, 3, 4}
a | b               # union:                {1, 2, 3, 4}
a & b               # intersection:         {2, 3}
a - b               # difference:           {1}
a ^ b               # symmetric difference: {1, 4}
```

### 3.4. Dictionary

Key-value pairs, insertion-ordered (Python 3.7+).

```python
d = {"a": 1, "b": 2}
d["a"]                   # 1 - KeyError if missing
d.get("z", 0)            # 0 if missing
d["c"] = 3
del d["a"]
d.pop("b")               # remove and return
"a" in d
d.keys() / d.values() / d.items()
d.update({"d": 4})

# defaultdict - auto-creates missing keys
from collections import defaultdict
dd = defaultdict(list)
dd["x"].append(1)        # no KeyError

# Counter
from collections import Counter
Counter("aabbcc")                  # Counter({'a': 2, 'b': 2, 'c': 2})
Counter([1,1,2,3]).most_common(2)  # [(1, 2), (2, 1)]
```

### 3.5. Comprehensions

```python
# List
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]

# Dict
lengths = {word: len(word) for word in ["hi", "hello"]}

# Set
unique_lens = {len(w) for w in ["hi", "hello", "hey"]}

# Generator - lazy, does not build list in memory
total = sum(x**2 for x in range(1_000_000))
```

---

## 4. Control Flow

Python control flow includes `if`/`elif`/`else`, `for`, `while`, and `match`/`case` (Python 3.10+). `for`/`while` loops support an `else` clause that runs when the loop exits without a `break`.

```python
# if / elif / else
if x > 0:
    print("positive")
elif x < 0:
    print("negative")
else:
    print("zero")

# Ternary
result = "pos" if x > 0 else "non-pos"

# for
for item in [1, 2, 3]:
    print(item)

for i, item in enumerate(["a", "b", "c"]):
    print(i, item)    # 0 a, 1 b, 2 c

for k, v in d.items():
    print(k, v)

for a, b in zip([1, 2], ["x", "y"]):
    print(a, b)       # 1 x, 2 y

for i in range(5):         # 0-4
    pass
for i in range(2, 10, 2):  # 2, 4, 6, 8
    pass

# while
while condition:
    if should_stop: break
    if should_skip: continue
else:
    # runs if loop completed without a break
    pass

# match (Python 3.10+)
match command:
    case "quit":
        quit()
    case "go" | "move":
        move()
    case {"action": action, "target": target}:   # dict pattern
        handle(action, target)
    case _:
        print("unknown")
```

---

## 5. Functions

### 5.1. Definition & Arguments

Python functions support positional, default, `*args` (variadic positional), `**kwargs` (variadic keyword), keyword-only (after `*`), and positional-only (before `/`) parameters.

```python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

# *args - variable positional args (tuple)
def add(*numbers: int) -> int:
    return sum(numbers)

# **kwargs - variable keyword args (dict)
def create(**fields):
    return fields

# Keyword-only (must be passed by name)
def func(a, b, *, must_be_keyword):
    pass

# Positional-only (before /)
def func(a, b, /, c):   # a and b cannot be passed as kwargs
    pass
```

### 5.2. Closures & `nonlocal`

A closure captures variables from the enclosing scope. Use `nonlocal` to rebind an enclosing variable rather than just read it.

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = make_counter()
counter()   # 1
counter()   # 2
```

### 5.3. Decorators

A decorator wraps a function to extend its behavior without modifying it. Use `@functools.wraps` to preserve the wrapped function's `__name__` and `__doc__`.

```python
import functools

def log(func):
    @functools.wraps(func)    # preserves __name__, __doc__
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print("done")
        return result
    return wrapper

@log
def say_hello(name):
    print(f"Hello {name}")

# Decorator with arguments
def repeat(n):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def hello():
    print("hi")
```

### 5.4. Lambda

```python
add = lambda x, y: x + y
sorted(users, key=lambda u: u.age)
```

---

## 6. Classes & OOP

### 6.1. Basics

Class variables are shared across all instances. Instance variables are set in `__init__` via `self`. Override `__repr__`, `__eq__`, and `__hash__` to control how objects behave in collections and comparisons.

```python
class Animal:
    species = "Unknown"   # class variable - shared across instances

    def __init__(self, name: str, age: int):
        self.name = name  # instance variable
        self.age = age

    def speak(self) -> str:
        return f"{self.name} makes a sound"

    def __repr__(self) -> str:
        return f"Animal(name={self.name!r}, age={self.age})"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, Animal) and self.name == other.name

    def __hash__(self):   # required if __eq__ is defined
        return hash(self.name)
```

### 6.2. Inheritance

Call `super().__init__()` to invoke the parent constructor. `isinstance` checks the full MRO, so `isinstance(Dog(...), Animal)` returns `True`.

```python
class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str):
        super().__init__(name, age)
        self.breed = breed

    def speak(self) -> str:
        return f"{self.name} barks"

isinstance(Dog("Rex", 3, "Lab"), Animal)   # True
issubclass(Dog, Animal)                    # True
```

### 6.3. `@classmethod`, `@staticmethod`, `@property`

`@classmethod` is used for alternative constructors. `@staticmethod` is a plain utility with no implicit argument. `@property` makes a method accessible as an attribute with optional setter logic.

```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius

    @classmethod
    def from_diameter(cls, diameter: float) -> "Circle":
        return cls(diameter / 2)   # alternative constructor

    @staticmethod
    def validate_radius(r: float) -> bool:
        return r > 0               # utility, no access to cls or self

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float):
        if value <= 0:
            raise ValueError("radius must be positive")
        self._radius = value

    @property
    def area(self) -> float:
        import math
        return math.pi * self._radius ** 2
```

### 6.4. Common Dunder Methods

| Method | Triggered by |
|---|---|
| `__init__` | `obj = Class()` |
| `__repr__` | `repr(obj)`, REPL display |
| `__str__` | `str(obj)`, `print(obj)` |
| `__eq__` | `obj == other` |
| `__hash__` | `hash(obj)`, set/dict membership |
| `__len__` | `len(obj)` |
| `__getitem__` | `obj[key]` |
| `__contains__` | `x in obj` |
| `__iter__` | `for x in obj` |
| `__enter__` / `__exit__` | `with obj:` |
| `__add__` / `__mul__` | `obj + other`, `obj * n` |
| `__lt__` / `__le__` etc. | `<`, `<=` etc. |

---

## 7. Exceptions

### 7.1. Hierarchy (partial)

```
BaseException
├── SystemExit
├── KeyboardInterrupt
└── Exception
    ├── ValueError
    ├── TypeError
    ├── AttributeError
    ├── KeyError
    ├── IndexError
    ├── FileNotFoundError
    ├── IOError
    └── RuntimeError
```

### 7.2. try / except / else / finally

```python
try:
    result = 10 / x
except ZeroDivisionError:
    print("division by zero")
except (TypeError, ValueError) as e:
    print(f"bad input: {e}")
except Exception as e:
    raise RuntimeError("unexpected") from e   # exception chaining
else:
    print("no exception")                     # only if no exception was raised
finally:
    print("always runs")
```

### 7.3. Custom Exceptions

Subclass `Exception` (or a shared base class) to define domain-specific exceptions that carry structured data alongside a message.

```python
class AppError(Exception):
    pass

class NotFoundError(AppError):
    def __init__(self, resource: str, id: int):
        super().__init__(f"{resource} with id {id} not found")
        self.resource = resource
        self.id = id

raise NotFoundError("User", 42)
```

### 7.4. Context Managers

A context manager ties setup and teardown logic to a `with` block, guaranteeing cleanup even if an exception is raised. Implement `__enter__`/`__exit__` on a class, or use `@contextmanager` on a generator function.

```python
# __enter__ and __exit__ are called automatically
with open("file.txt") as f:
    data = f.read()

# Custom context manager
from contextlib import contextmanager

@contextmanager
def db_transaction(conn):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
```

---

## 8. Modules, Packages & Virtual Environments

### 8.1. Imports

```python
import os
from os import path, getcwd
from os.path import join, exists
import numpy as np              # alias

# Relative (inside a package)
from . import sibling
from ..parent import something
```

### 8.2. Package Structure

```
my_package/
├── __init__.py        # makes the directory a package
├── module_a.py
└── sub/
    ├── __init__.py
    └── module_b.py
```

`__init__.py` can re-export symbols:

```python
# my_package/__init__.py
from .module_a import MyClass   # consumers can import directly from my_package
```

### 8.3. `__name__` Guard

```python
def main():
    print("running")

if __name__ == "__main__":
    main()   # only runs when executed directly, not when imported
```

### 8.4. Virtual Environments

```bash
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
.venv\Scripts\activate        # Windows
deactivate

pip install requests
pip freeze > requirements.txt
pip install -r requirements.txt

# Modern tooling
pip install uv
uv venv && uv pip install -r requirements.txt
```

---

## 9. File I/O

Use `with` blocks to ensure files are closed automatically. Always specify `encoding` explicitly to avoid platform-dependent behavior.

```python
# Read
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()          # whole file as string
    lines = f.readlines()       # list of lines
    for line in f:              # line-by-line (memory efficient)
        print(line.strip())

# Write / Append
with open("file.txt", "w", encoding="utf-8") as f:
    f.write("hello\n")

with open("file.txt", "a") as f:
    f.write("more\n")
```

| Mode | Meaning |
|---|---|
| `r` | Read (default) |
| `w` | Write (truncates if exists) |
| `a` | Append |
| `x` | Create (fails if exists) |
| `b` | Binary mode (`rb`, `wb`) |
| `+` | Read + write (`r+`, `w+`) |

### 9.1. `pathlib`

```python
from pathlib import Path

p = Path("data") / "input" / "file.csv"
p.exists()
p.is_file()
p.is_dir()
p.suffix         # ".csv"
p.stem           # "file"
p.parent         # Path("data/input")
p.name           # "file.csv"
p.read_text(encoding="utf-8")
p.write_text("content")
p.mkdir(parents=True, exist_ok=True)
list(p.parent.glob("*.csv"))
```

---

## 10. Type Hints

Type hints are not enforced at runtime. They are used by static analysis tools like `mypy` and IDEs for completions and error detection.

```python
from typing import Optional, Union, Any
from collections.abc import Callable, Sequence, Iterator

def greet(name: str) -> str: ...

# Optional - can be None
def find(id: int) -> str | None: ...     # Python 3.10+ union syntax
def find(id: int) -> Optional[str]: ...  # equivalent, older style

# Collections
def process(items: list[int]) -> dict[str, int]: ...

# Callable
def apply(fn: Callable[[int, str], bool], x: int) -> bool: ...

# TypeVar - generic functions
from typing import TypeVar
T = TypeVar("T")
def first(items: list[T]) -> T:
    return items[0]

# Protocol - structural typing (duck typing)
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

def render(item: Drawable) -> None:
    item.draw()   # any object with a draw() method works - no inheritance needed
```

```bash
mypy my_module.py    # static type checker
```

---

## 11. Dataclasses & NamedTuples

### 11.1. `@dataclass`

Auto-generates `__init__`, `__repr__`, `__eq__`.

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float
    label: str = "origin"
    tags: list[str] = field(default_factory=list)   # mutable defaults need field()

p = Point(1.0, 2.0)
# Point(x=1.0, y=2.0, label='origin', tags=[])

@dataclass(frozen=True)    # immutable (generates __hash__)
class Coords:
    lat: float
    lon: float

@dataclass(order=True)     # generates __lt__, __le__ etc. based on field order
class Version:
    major: int
    minor: int
```

### 11.2. `NamedTuple`

```python
from typing import NamedTuple

class Employee(NamedTuple):
    name: str
    dept: str
    salary: float = 0.0

e = Employee("Ryo", "Engineering", 80000)
e.name       # "Ryo"
e[0]         # "Ryo" (tuple access still works)
e._asdict()  # {"name": "Ryo", "dept": "Engineering", "salary": 80000}
```

---

## 12. Concurrency

### 12.1. Threading (I/O-bound)

```python
import threading

def fetch(url):
    print(f"fetching {url}")

threads = [threading.Thread(target=fetch, args=(url,)) for url in urls]
for t in threads: t.start()
for t in threads: t.join()

# Thread-safe shared state
lock = threading.Lock()
with lock:
    shared_counter += 1
```

The **GIL (Global Interpreter Lock)** prevents true parallel CPU execution in CPython threads. Threading is still effective for I/O-bound work.

### 12.2. Multiprocessing (CPU-bound)

```python
from multiprocessing import Pool

def square(x):
    return x * x

with Pool(processes=4) as pool:
    results = pool.map(square, range(10))   # [0, 1, 4, 9, ...]
```

Each process has its own interpreter and memory - no GIL restriction.

### 12.3. `asyncio`

```python
import asyncio

async def fetch_data(url: str) -> str:
    await asyncio.sleep(1)    # simulate async I/O
    return f"data from {url}"

async def main():
    # Sequential
    result = await fetch_data("https://api.example.com")

    # Concurrent - all three run simultaneously
    results = await asyncio.gather(
        fetch_data("https://api1.com"),
        fetch_data("https://api2.com"),
        fetch_data("https://api3.com"),
    )

    # With timeout
    result = await asyncio.wait_for(fetch_data("url"), timeout=5.0)

asyncio.run(main())
```

`asyncio` is **single-threaded** - cooperative multitasking. Use for I/O-bound async work (HTTP, DB, file). Use `multiprocessing` for CPU-bound.

---

## 13. Common Standard Library

```python
import os
os.getcwd()
os.listdir(".")
os.environ.get("HOME")
os.path.join("a", "b", "c.txt")
os.makedirs("dir/sub", exist_ok=True)

import sys
sys.argv           # command-line args list
sys.exit(0)
sys.path           # module search paths

import json
json.dumps({"a": 1}, indent=2)    # dict to JSON string
json.loads('{"a": 1}')            # JSON string to dict
json.dump(data, file)             # write JSON to file
json.load(file)                   # read JSON from file

import re
re.match(r"^\d+", "123abc")        # match at start
re.search(r"\d+", "abc123")        # match anywhere
re.findall(r"\d+", "a1 b2 c3")    # ["1", "2", "3"]
re.sub(r"\s+", " ", "a  b   c")   # "a b c"

from datetime import datetime, date, timedelta
now = datetime.now()
today = date.today()
dt = datetime(2024, 1, 15, 10, 30)
dt.strftime("%Y-%m-%d %H:%M:%S")
datetime.strptime("2024-01-15", "%Y-%m-%d")
later = now + timedelta(days=7, hours=3)

import copy
copy.copy(obj)       # shallow copy
copy.deepcopy(obj)   # deep copy

from collections import OrderedDict, deque
d = deque(maxlen=100)    # efficient append/pop from both ends
d.appendleft(x)
d.popleft()

import itertools
list(itertools.chain([1,2], [3,4]))              # [1, 2, 3, 4]
list(itertools.product([1,2], ["a","b"]))        # [(1,'a'),(1,'b'),(2,'a'),(2,'b')]
list(itertools.combinations([1,2,3], 2))         # [(1,2),(1,3),(2,3)]
list(itertools.permutations([1,2,3], 2))

import functools
functools.reduce(lambda a, b: a + b, [1,2,3,4])  # 10
functools.lru_cache(maxsize=128)                  # memoize decorator
functools.partial(pow, 2)                         # partial(pow,2)(10) = 1024
```
