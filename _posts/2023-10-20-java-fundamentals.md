---
layout: post
title: "Java Fundamentals Cheatsheet"
description: >-
  Personal cheatsheet for Java fundamentals. Covers OOP, classes, strings, exceptions, generics, collections, streams, concurrency, and modern Java features.
author: ryo
date: 2023-10-20 00:00:00 +0800
categories: [Software Engineering]
tags: [java, cheatsheet]
toc: true
comments: true
pin: false
published: true
---

## 1. OOP Principles

### 1.1. Encapsulation

Bundles data and behaviour together, hiding internal state. External access via getters/setters.

```java
public class BankAccount {
    private double balance; // hidden

    public double getBalance() { return balance; }

    public void deposit(double amount) {
        if (amount > 0) balance += amount;
    }
}
```

### 1.2. Inheritance

A subclass inherits fields and methods from a superclass. Java only supports **single class inheritance** but multiple interface implementation.

```java
public class Animal {
    public void eat() { System.out.println("eating"); }
}

public class Dog extends Animal {
    @Override
    public void eat() { System.out.println("eating kibble"); }

    public void bark() { System.out.println("woof"); }
}
```

- `super.method()` - call the parent's version
- `super(args)` - call parent constructor (must be first line)
- A subclass constructor always calls the parent constructor (implicitly `super()` if not specified)

### 1.3. Polymorphism

**Compile-time (overloading):** Same method name, different parameters.

```java
public int add(int a, int b) { return a + b; }
public double add(double a, double b) { return a + b; }
```

**Runtime (overriding):** Subclass overrides parent method. Resolved at runtime based on the actual object type, not the reference type.

```java
Animal a = new Dog(); // reference type: Animal, object type: Dog
a.eat();              // calls Dog.eat() - resolved at runtime
```

### 1.4. Abstraction

Hides implementation details, exposes only what's necessary. Achieved via **abstract classes** or **interfaces**.

```java
public abstract class Shape {
    public abstract double area(); // must implement

    public void describe() {       // shared implementation
        System.out.println("Area: " + area());
    }
}

public class Circle extends Shape {
    private double radius;
    public Circle(double r) { this.radius = r; }

    @Override
    public double area() { return Math.PI * radius * radius; }
}
```

---

## 2. Classes & Objects

### 2.1. Constructors

The default no-arg constructor is not generated once any constructor is explicitly defined. Use `this()` to delegate to another constructor in the same class.

```java
public class Person {
    private String name;
    private int age;

    public Person() { this("Unknown", 0); }          // delegates to other constructor

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

- If you define **any** constructor, the default no-arg constructor is **not** auto-generated
- `this(args)` - constructor chaining, must be first line

### 2.2. Access Modifiers

| Modifier | Same Class | Same Package | Subclass | Everywhere |
|---|---|---|---|---|
| `private` | yes | no | no | no |
| (default) | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

### 2.3. `static` Members

- **Static fields** - shared across all instances; belongs to the class, not any object
- **Static methods** - can be called without an instance; cannot access `this` or instance fields
- **Static blocks** - run once when the class is first loaded

```java
public class Counter {
    private static int count = 0; // shared

    public Counter() { count++; }

    public static int getCount() { return count; } // no instance needed
}

Counter.getCount(); // called on the class
```

### 2.4. `final`

| Usage | Meaning |
|---|---|
| `final` variable | Value cannot be reassigned after assignment |
| `final` method | Cannot be overridden in subclasses |
| `final` class | Cannot be subclassed (`String` is `final`) |
| `final` reference | Reference cannot point to a new object, but the object itself can be mutated |

```java
final List<String> list = new ArrayList<>();
list.add("ok");        // fine - mutating the object
list = new ArrayList<>(); // COMPILE ERROR - reassigning the reference
```

---

## 3. `equals()` and `hashCode()`

**The Contract:**
1. If `a.equals(b)` is `true`, then `a.hashCode() == b.hashCode()` **must** be true
2. The reverse is NOT required (hash collisions are allowed)
3. Always override both together

**Why it matters for Collections:** `HashMap`/`HashSet` use `hashCode()` to find the bucket, then `equals()` to confirm the match. If you override only `equals`, two "equal" objects can land in different buckets and never be found.

```java
public class Point {
    private int x, y;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Point p)) return false; // pattern matching
        return x == p.x && y == p.y;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }
}

// Default Object.equals() checks reference equality (==), not value equality
new Point(1,2).equals(new Point(1,2)); // false without override, true with override
```

---

## 4. Enums

Enums define a fixed set of named constants. Unlike plain constants, they are type-safe and can carry fields, methods, and implement interfaces.

```java
public enum Direction {
    NORTH, SOUTH, EAST, WEST;
}

// Enum with fields and methods
public enum Planet {
    MERCURY(3.303e+23, 2.4397e6),
    EARTH(5.976e+24, 6.37814e6);

    private final double mass;
    private final double radius;

    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }

    public double surfaceGravity() {
        final double G = 6.67300E-11;
        return G * mass / (radius * radius);
    }
}
```

| Method | Description |
|---|---|
| `Direction.values()` | Returns array of all enum constants |
| `Direction.valueOf("NORTH")` | Returns enum constant by name |
| `direction.name()` | Returns the name as a String |
| `direction.ordinal()` | Returns the zero-based position |

- Enums are implicitly `public static final` and extend `java.lang.Enum`
- Enums can implement interfaces
- Enums are safe for `switch` statements and can be used in `EnumMap`/`EnumSet` (highly efficient)

```java
switch (direction) {
    case NORTH -> System.out.println("Going north");
    case SOUTH -> System.out.println("Going south");
}
```

---

## 5. Interfaces & Abstract Classes

| | Interface | Abstract Class |
|---|---|---|
| Instantiation | no | no |
| Multiple inheritance | yes (multiple) | no (single) |
| Fields | `public static final` only | Any type |
| Methods | `abstract`, `default`, `static` | Any type |
| Constructor | no | yes |
| When to use | Define a **capability/contract** | Share **common state/behaviour** with a base |

```java
public interface Flyable {
    void fly(); // abstract by default

    default void land() {               // default - optional to override
        System.out.println("landing");
    }

    static Flyable noOp() {             // static factory
        return () -> {};
    }
}

public interface Swimmable {
    void swim();
}

// A class can implement multiple interfaces
public class Duck extends Bird implements Flyable, Swimmable {
    @Override public void fly() { ... }
    @Override public void swim() { ... }
}
```

**Diamond problem with default methods:** If two interfaces have the same `default` method, the implementing class **must** override it to resolve the conflict.

---

## 6. Pass by Value vs Pass by Reference

Java is **always pass by value**. For objects, the *value* passed is the **reference** (memory address). The reference itself is copied.

```java
void mutate(List<String> list) {
    list.add("added");     // affects original - same object via copied reference
}

void reassign(List<String> list) {
    list = new ArrayList<>(); // does NOT affect original - only local copy changes
}

List<String> names = new ArrayList<>();
mutate(names);    // names now has "added"
reassign(names);  // names unchanged
```

---

## 7. Strings

### 7.1. Immutability & String Pool

`String` is **immutable** - every "modification" creates a new object.

```java
String a = "hello";       // goes into the String pool
String b = "hello";       // same object from pool
String c = new String("hello"); // new heap object - avoid this

a == b       // true  (same pool reference)
a == c       // false (different objects)
a.equals(c)  // true  (same value)
```

### 7.2. `String` vs `StringBuilder` vs `StringBuffer`

| | `String` | `StringBuilder` | `StringBuffer` |
|---|---|---|---|
| Mutability | Immutable | Mutable | Mutable |
| Thread-safe | yes (immutable) | no | yes (synchronized) |
| Performance | Slow for concatenation in loops | Fast | Slower than `StringBuilder` |

```java
// Bad - creates many intermediate String objects
String result = "";
for (int i = 0; i < 1000; i++) result += i;

// Good
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) sb.append(i);
String result = sb.toString();
```

### 7.3. Common String Methods

```java
String s = "  Hello, World!  ";

s.trim()                        // "Hello, World!"
s.strip()                       // "Hello, World!" (Unicode-aware, prefer this)
s.toLowerCase()                 // "  hello, world!  "
s.toUpperCase()
s.contains("World")             // true
s.startsWith("Hello")           // false (leading spaces)
s.replace("World", "Java")      // "  Hello, Java!  "
s.split(", ")                   // ["  Hello", "World!  "]
s.substring(2, 7)               // "Hello"
s.charAt(2)                     // 'H'
s.indexOf("World")              // 9
s.isEmpty()                     // false
s.isBlank()                     // false (Java 11+)
s.length()                      // 17
String.format("Hi %s, you are %d", "Ryo", 25) // "Hi Ryo, you are 25"
String.join(", ", "a", "b", "c")               // "a, b, c"
"hello".repeat(3)               // "hellohellohello" (Java 11+)
```

---

## 8. Autoboxing, Unboxing & Gotchas

Autoboxing = automatic conversion from primitive (`int`) to wrapper (`Integer`). Unboxing is the reverse.

```java
Integer a = 5;   // autoboxing
int b = a;       // unboxing
```

**Integer Cache Gotcha:** Java caches `Integer` values from -128 to 127. Outside this range, `==` will fail even for equal values.

```java
Integer x = 127;
Integer y = 127;
x == y   // true  (cached)

Integer p = 128;
Integer q = 128;
p == q   // false (not cached - different heap objects)
p.equals(q) // true - always use .equals() for wrappers
```

**NPE from unboxing:**

```java
Integer val = null;
int x = val; // NullPointerException at runtime - unboxing null
```

**Performance:** Autoboxing in tight loops creates many unnecessary heap objects. Prefer primitives where possible.

---

## 9. Exceptions

### 9.1. Hierarchy

```
Throwable
├── Error          (JVM-level, don't catch: OutOfMemoryError, StackOverflowError)
└── Exception
    ├── Checked    (must declare or handle: IOException, SQLException)
    └── RuntimeException (unchecked: NullPointerException, IllegalArgumentException)
```

- **Checked** - compiler forces you to handle (try-catch) or declare (`throws`)
- **Unchecked (RuntimeException)** - programming bugs; not required to handle

### 9.2. try-catch-finally & try-with-resources

```java
// Basic
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("Error: " + e.getMessage());
} catch (Exception e) {
    e.printStackTrace(); // catches anything else
} finally {
    System.out.println("always runs, even if exception or return");
}

// Multi-catch
catch (IOException | SQLException e) { ... }

// try-with-resources - auto-closes anything implementing AutoCloseable
try (FileReader fr = new FileReader("file.txt");
     BufferedReader br = new BufferedReader(fr)) {
    String line = br.readLine();
} // fr and br are closed automatically, even on exception
```

### 9.3. Custom Exceptions

Extend `Exception` for checked exceptions, `RuntimeException` for unchecked. Call `super(message)` and add fields for any extra context.

```java
// Checked custom exception
public class InsufficientFundsException extends Exception {
    private final double amount;

    public InsufficientFundsException(double amount) {
        super("Insufficient funds. Shortfall: " + amount);
        this.amount = amount;
    }

    public double getAmount() { return amount; }
}

// Usage
public void withdraw(double amount) throws InsufficientFundsException {
    if (amount > balance) throw new InsufficientFundsException(amount - balance);
    balance -= amount;
}
```

### 9.4. `throw` vs `throws`

| | `throw` | `throws` |
|---|---|---|
| Purpose | Actually throws an exception instance | Declares that a method may throw |
| Location | Inside method body | Method signature |
| Example | `throw new RuntimeException("msg")` | `void read() throws IOException` |

---

## 10. Generics

### 10.1. Generic Classes & Methods

Type parameters are declared in angle brackets and resolved at the call site. Bounds like `<T extends Comparable<T>>` restrict which types are accepted.

```java
// Generic class
public class Box<T> {
    private T value;
    public Box(T value) { this.value = value; }
    public T get() { return value; }
}

Box<String> strBox = new Box<>("hello");
Box<Integer> intBox = new Box<>(42);

// Generic method
public static <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) > 0 ? a : b;
}
```

### 10.2. Bounded Wildcards

| Wildcard | Meaning | Use case |
|---|---|---|
| `<?>` | Unknown type | Read-only, most general |
| `<? extends T>` | T or any subclass (upper bound) | **Producer** - you read from it |
| `<? super T>` | T or any superclass (lower bound) | **Consumer** - you write into it |

**PECS - Producer Extends, Consumer Super:**

```java
// You can READ from an upper-bounded wildcard
public double sumList(List<? extends Number> list) {
    return list.stream().mapToDouble(Number::doubleValue).sum();
}

// You can WRITE to a lower-bounded wildcard
public void addNumbers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
}
```

### 10.3. Type Erasure

Generics are a compile-time feature. At runtime, type parameters are **erased** to `Object` (or their bound). You cannot do `new T()`, `new T[]`, or `instanceof T` at runtime.

---

## 11. Collections & Data Structures

### 11.1. Overview

| Interface | Implementation | Ordered | Sorted | Duplicates | Null | Thread-safe |
|---|---|---|---|---|---|---|
| `List` | `ArrayList` | yes (insertion) | no | yes | yes | no |
| `List` | `LinkedList` | yes (insertion) | no | yes | yes | no |
| `Set` | `HashSet` | no | no | no | 1 null | no |
| `Set` | `LinkedHashSet` | yes (insertion) | no | no | 1 null | no |
| `Set` | `TreeSet` | yes (sorted) | yes | no | no | no |
| `Map` | `HashMap` | no | no | Keys: no | Key/val: yes | no |
| `Map` | `LinkedHashMap` | yes (insertion) | no | Keys: no | yes | no |
| `Map` | `TreeMap` | yes (sorted) | yes | Keys: no | Key: no | no |
| `Queue` | `ArrayDeque` | yes (FIFO) | no | yes | no | no |
| `Queue` | `PriorityQueue` | yes (priority) | yes | yes | no | no |

**Thread-safe alternatives:** `ConcurrentHashMap`, `CopyOnWriteArrayList`, `Collections.synchronizedList(...)`

### 11.2. Common Operations

Reference for the most-used `List`, `Map`, and `Set` operations.

```java
// List
List<String> list = new ArrayList<>(List.of("a", "b", "c")); // mutable copy
list.add("d");
list.remove("b");
list.get(0);
list.size();
list.contains("a");
Collections.sort(list);
Collections.reverse(list);

// Map
Map<String, Integer> map = new HashMap<>();
map.put("a", 1);
map.getOrDefault("z", 0);         // 0 if missing
map.putIfAbsent("a", 99);         // ignored - already present
map.computeIfAbsent("b", k -> k.length()); // compute if missing
map.merge("a", 1, Integer::sum);  // get+update in one shot
for (Map.Entry<String, Integer> e : map.entrySet()) {
    System.out.println(e.getKey() + "=" + e.getValue());
}

// Set
Set<String> set = new HashSet<>(List.of("a", "b"));
set.add("c");
set.contains("a"); // O(1) for HashSet
```

### 11.3. `Comparable` vs `Comparator`

| | `Comparable` | `Comparator` |
|---|---|---|
| Method | `compareTo(T o)` | `compare(T o1, T o2)` |
| Defined in | The class itself | External / lambda |
| Purpose | Natural ordering | Custom/alternate ordering |

```java
// Comparable - natural order
public class Student implements Comparable<Student> {
    private int gpa;
    @Override
    public int compareTo(Student other) {
        return Integer.compare(this.gpa, other.gpa);
    }
}

// Comparator - flexible, can chain
List<Student> students = ...;
students.sort(Comparator.comparing(Student::getName)
                        .thenComparingInt(Student::getGpa)
                        .reversed());
```

---

## 12. Anonymous Classes, Inner Classes & Nested Classes

### 12.1. Types of Nested Classes

| Type | `static`? | Access outer instance? | Use case |
|---|---|---|---|
| Static nested class | yes | no | Logically grouped helper class |
| Inner class (non-static) | no | yes | Needs access to outer instance |
| Local class | no | yes (effectively final vars) | Method-scoped helper |
| Anonymous class | no | yes (effectively final vars) | One-off implementation |

### 12.2. Anonymous Classes

Implement an interface or extend an abstract class inline, without naming the class. Can only capture effectively final local variables from the enclosing scope.

```java
// Implemented inline without naming the class
Runnable r = new Runnable() {
    @Override
    public void run() {
        System.out.println("running");
    }
};

// With an abstract class
Shape shape = new Shape() {
    @Override
    public double area() { return 0; }
};
```

---

## 13. Lambdas, Functional Interfaces & Method References

### 13.1. Lambdas

A lambda can only be assigned where a **functional interface** is expected (an interface with exactly one abstract method).

```java
// (params) -> expression  OR  (params) -> { statements; }
Runnable r = () -> System.out.println("hi");
Comparator<String> c = (a, b) -> a.compareTo(b);
```

### 13.2. Common Functional Interfaces

| Interface | Signature | Use |
|---|---|---|
| `Runnable` | `() -> void` | Task with no input/output |
| `Supplier<T>` | `() -> T` | Produce a value |
| `Consumer<T>` | `T -> void` | Consume a value |
| `BiConsumer<T,U>` | `(T, U) -> void` | Consume two values |
| `Function<T,R>` | `T -> R` | Transform a value |
| `BiFunction<T,U,R>` | `(T, U) -> R` | Transform two values to one |
| `Predicate<T>` | `T -> boolean` | Test a condition |
| `BiPredicate<T,U>` | `(T, U) -> boolean` | Test two values |
| `UnaryOperator<T>` | `T -> T` | Transform same type |
| `BinaryOperator<T>` | `(T, T) -> T` | Combine two of same type |

```java
Predicate<String> isBlank = String::isBlank;
Function<String, Integer> len = String::length;
Consumer<String> print = System.out::println;
Supplier<List<String>> listMaker = ArrayList::new;

// Composing
Predicate<String> notBlank = isBlank.negate();
Function<String, String> trimThenUpper = ((Function<String, String>) String::trim).andThen(String::toUpperCase);
```

### 13.3. Method References

| Kind | Syntax | Lambda equivalent |
|---|---|---|
| Static method | `ClassName::staticMethod` | `x -> ClassName.staticMethod(x)` |
| Instance method (arbitrary instance) | `ClassName::instanceMethod` | `x -> x.instanceMethod()` |
| Instance method (specific instance) | `instance::instanceMethod` | `x -> instance.instanceMethod(x)` |
| Constructor | `ClassName::new` | `x -> new ClassName(x)` |

```java
List<String> words = List.of("hello", "world");

words.stream().map(String::toUpperCase).forEach(System.out::println);
//                  ^--- instance method ref        ^--- specific instance ref

List<String> list = words.stream().collect(Collectors.toCollection(ArrayList::new));
//                                                                  ^--- constructor ref
```

---

## 14. Streams API

### 14.1. Overview

Lazy pipeline of operations on a data source. Doesn't store data. **Intermediate** ops return a new stream (lazy). **Terminal** ops trigger evaluation and produce a result.

```java
List<String> names = List.of("alice", "bob", "charlie", "anna");

List<String> result = names.stream()                  // source
    .filter(n -> n.startsWith("a"))                   // intermediate
    .map(String::toUpperCase)                         // intermediate
    .sorted()                                         // intermediate
    .collect(Collectors.toList());                    // terminal
// ["ALICE", "ANNA"]
```

### 14.2. Intermediate Operations

| Operation | Description |
|---|---|
| `filter(Predicate)` | Keep elements matching predicate |
| `map(Function)` | Transform each element |
| `flatMap(Function)` | Map then flatten (for nested collections) |
| `distinct()` | Remove duplicates (uses `equals`) |
| `sorted()` / `sorted(Comparator)` | Sort elements |
| `limit(n)` | Take first n elements |
| `skip(n)` | Skip first n elements |
| `peek(Consumer)` | Debug/inspect without consuming |

### 14.3. Terminal Operations

| Operation | Description |
|---|---|
| `collect(Collector)` | Accumulate into collection, map, string, etc. |
| `forEach(Consumer)` | Consume each element |
| `count()` | Count elements |
| `findFirst()` / `findAny()` | Return Optional of first/any element |
| `anyMatch` / `allMatch` / `noneMatch` | Short-circuit boolean checks |
| `min(Comparator)` / `max(Comparator)` | Return Optional of min/max |
| `reduce(identity, BinaryOperator)` | Fold elements into one value |
| `toArray()` | Return array |

### 14.4. Common Collectors

Built-in collectors for grouping, joining, partitioning, and accumulating into collections. Import `java.util.stream.Collectors.*` statically.

```java
import static java.util.stream.Collectors.*;

// To collections
stream.collect(toList())
stream.collect(toSet())
stream.collect(toUnmodifiableList())

// Joining
stream.collect(joining(", ", "[", "]"))  // "[a, b, c]"

// Grouping
Map<Integer, List<String>> byLength = names.stream()
    .collect(groupingBy(String::length));

// Counting per group
Map<Integer, Long> countByLength = names.stream()
    .collect(groupingBy(String::length, counting()));

// Partitioning (splits into true/false)
Map<Boolean, List<String>> partition = names.stream()
    .collect(partitioningBy(n -> n.length() > 3));

// To map
Map<String, Integer> nameLengths = names.stream()
    .collect(toMap(n -> n, String::length));
```

### 14.5. `flatMap`

`flatMap` maps each element to a stream and flattens all resulting streams into one. Use it to process nested collections or split strings into words.

```java
List<List<Integer>> nested = List.of(List.of(1, 2), List.of(3, 4));

List<Integer> flat = nested.stream()
    .flatMap(Collection::stream)
    .collect(toList()); // [1, 2, 3, 4]

// Common use: split strings into words
List<String> sentences = List.of("hello world", "foo bar");
List<String> words = sentences.stream()
    .flatMap(s -> Arrays.stream(s.split(" ")))
    .collect(toList()); // ["hello", "world", "foo", "bar"]
```

### 14.6. `reduce`

`reduce` folds all elements into a single result using an accumulator. Without an identity value, the result is an `Optional` because the stream may be empty.

```java
// reduce(identity, accumulator)
int sum = IntStream.rangeClosed(1, 10).reduce(0, Integer::sum); // 55

// Without identity - returns Optional (stream could be empty)
Optional<String> longest = names.stream()
    .reduce((a, b) -> a.length() >= b.length() ? a : b);
```

### 14.7. Primitive Streams

Avoid boxing overhead for numeric work:

```java
IntStream.range(0, 5)              // 0, 1, 2, 3, 4
IntStream.rangeClosed(1, 5)        // 1, 2, 3, 4, 5
IntStream.of(1, 2, 3).sum()        // 6
IntStream.of(1, 2, 3).average()    // OptionalDouble
DoubleStream.of(1.0, 2.0).max()    // OptionalDouble

// Box to stream of wrappers
IntStream.of(1,2,3).boxed()        // Stream<Integer>

// To primitive stream from object stream
names.stream().mapToInt(String::length)
```

### 14.8. Parallel Streams

Switch from `.stream()` to `.parallelStream()` to process using the common `ForkJoinPool`. Only beneficial for CPU-intensive, stateless, order-independent operations on large datasets.

```java
long count = names.parallelStream()
    .filter(n -> n.length() > 3)
    .count();
```

- Uses the `ForkJoinPool.commonPool()`
- Good for CPU-intensive, stateless, order-independent operations
- Bad for I/O, stateful operations, or small data sets (overhead > gain)
- Avoid shared mutable state

---

## 15. Optionals

`Optional` wraps a potentially-null value to make the absence case explicit. Prefer `orElse`/`orElseGet` over calling `get()` directly.

```java
Optional<String> opt = Optional.of("hello");        // throws NPE if null
Optional<String> safe = Optional.ofNullable(null);  // empty Optional
Optional<String> empty = Optional.empty();

opt.isPresent()          // true
opt.isEmpty()            // false (Java 11+)
opt.get()                // "hello" - throws NoSuchElementException if empty

opt.orElse("default")           // "default" if empty
opt.orElseGet(() -> compute())  // lazy - only calls supplier if empty
opt.orElseThrow(() -> new RuntimeException("missing"))

opt.ifPresent(System.out::println)          // run if present
opt.ifPresentOrElse(s -> use(s), () -> handleEmpty()); // Java 9+

// Transforming
opt.map(String::toUpperCase)         // Optional<String>
opt.filter(s -> s.length() > 3)      // Optional<String> - empty if predicate fails
opt.flatMap(s -> findByName(s))      // when the mapping function itself returns Optional
```

**Rule:** Never use `Optional.get()` without checking `isPresent()`. Prefer `orElse`/`orElseGet`.

---

## 16. Concurrency

### 16.1. `Thread` and `Runnable`

The low-level API for creating threads. Prefer `ExecutorService` for managing thread pools in production code.

```java
// Extend Thread
Thread t = new Thread(() -> System.out.println("in thread"));
t.start();   // start - don't call run() directly

t.join();    // current thread waits for t to finish
Thread.sleep(1000); // current thread sleeps 1s (throws InterruptedException)
```

### 16.2. `ExecutorService`

Prefer over raw `Thread` for managing thread pools.

```java
ExecutorService exec = Executors.newFixedThreadPool(4);
ExecutorService single = Executors.newSingleThreadExecutor();
ExecutorService cached = Executors.newCachedThreadPool(); // grows as needed

// Submit Runnable (no return value)
exec.submit(() -> System.out.println("task"));

// Submit Callable (returns Future)
Future<Integer> future = exec.submit(() -> {
    Thread.sleep(100);
    return 42;
});

int result = future.get();          // blocks until done
future.get(1, TimeUnit.SECONDS);    // timeout variant

// Shutdown - always shut down
exec.shutdown();                    // graceful - waits for tasks to finish
exec.shutdownNow();                 // forceful - interrupts running tasks
```

### 16.3. `synchronized` and `volatile`

Three mechanisms for thread safety: `synchronized` blocks for atomic operations, `volatile` for memory visibility across threads, and atomic classes for lock-free single-variable updates.

```java
// synchronized method - lock on `this`
public synchronized void increment() { count++; }

// synchronized block - more granular
public void increment() {
    synchronized(this) { count++; }
}

// volatile - guarantees visibility across threads, NOT atomicity
private volatile boolean running = true;
// Good for flags. Bad for count++ (read-modify-write is not atomic)

// Atomic classes - thread-safe, lock-free
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();
counter.compareAndSet(expected, newValue);
```

### 16.4. `CompletableFuture`

`CompletableFuture` enables non-blocking async computation with composable chaining, error handling, and combination operators.

```java
// Async task (runs in ForkJoinPool by default)
CompletableFuture<String> cf = CompletableFuture.supplyAsync(() -> {
    return fetchData(); // runs in background
});

// Chaining - non-blocking
cf.thenApply(data -> data.toUpperCase())      // transform result (same thread)
  .thenApplyAsync(data -> process(data))      // transform result (async thread)
  .thenAccept(System.out::println)            // consume result, return void
  .thenRun(() -> System.out.println("done")); // run after, no access to result

// thenCompose - flat-map for CompletableFuture (avoids nesting)
CompletableFuture<String> result = cf
    .thenCompose(data -> anotherAsyncTask(data)); // anotherAsyncTask returns CF<String>

// Error handling
cf.exceptionally(ex -> {
    System.err.println("Error: " + ex.getMessage());
    return "fallback";
});

cf.handle((result, ex) -> {           // always runs - like finally
    if (ex != null) return "error";
    return result;
});

// Combining
CompletableFuture<String> a = CompletableFuture.supplyAsync(() -> "hello");
CompletableFuture<String> b = CompletableFuture.supplyAsync(() -> "world");

CompletableFuture.allOf(a, b).join(); // wait for all
CompletableFuture.anyOf(a, b).join(); // wait for first to complete

a.thenCombine(b, (ra, rb) -> ra + " " + rb); // combine two results
```

### 16.5. Common Concurrency Problems

| Problem | Description | Fix |
|---|---|---|
| Race condition | Two threads read-modify-write shared state | `synchronized`, `AtomicInteger` |
| Deadlock | Two threads each hold a lock the other needs | Consistent lock ordering, `tryLock` |
| Starvation | Thread never gets CPU time | Fair locks (`ReentrantLock(true)`) |
| Visibility problem | Thread reads stale cached value | `volatile`, `synchronized` |

---

## 17. Modern Java Features (Java 8–17)

### 17.1. Java 8

- Lambdas and Streams (covered above)
- `Optional` (covered above)
- Default/static interface methods (covered above)
- `java.time` API (`LocalDate`, `LocalDateTime`, `ZonedDateTime`, `Duration`, `Period`)

```java
LocalDate today = LocalDate.now();
LocalDate nextWeek = today.plusDays(7);
DateTimeFormatter fmt = DateTimeFormatter.ofPattern("dd/MM/yyyy");
String formatted = today.format(fmt);
```

### 17.2. Java 10 - `var`

```java
var list = new ArrayList<String>();  // inferred as ArrayList<String>
var name = "hello";                  // String

// Only for local variables - cannot use in fields, params, or return types
```

### 17.3. Java 14 - Switch Expressions

```java
// Old switch statement (fall-through prone)
int result;
switch (day) {
    case MONDAY: result = 1; break;
    default:     result = 0;
}

// New switch expression (exhaustive, no fall-through)
int result = switch (day) {
    case MONDAY -> 1;
    case TUESDAY -> 2;
    default -> 0;
};

// With yield for blocks
int result = switch (day) {
    case MONDAY -> 1;
    default -> {
        System.out.println("other");
        yield 0;
    }
};
```

### 17.4. Java 15 - Text Blocks

```java
String json = """
        {
            "name": "Ryo",
            "age": 25
        }
        """;
```

### 17.5. Java 16 - Records

Immutable data classes. Auto-generates constructor, accessors, `equals`, `hashCode`, `toString`.

```java
public record Point(int x, int y) {}

Point p = new Point(1, 2);
p.x()  // 1 - accessor (not getX)
p.y()  // 2

// Can add custom methods, validate in compact constructor
public record Range(int min, int max) {
    public Range {  // compact constructor
        if (min > max) throw new IllegalArgumentException();
    }
    public int size() { return max - min; }
}
```

### 17.6. Java 16 - Pattern Matching for `instanceof`

```java
// Old
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.length());
}

// New
if (obj instanceof String s) {
    System.out.println(s.length()); // s is already cast and scoped
}
```

### 17.7. Java 17 - Sealed Classes

Restrict which classes can extend/implement a type. All permitted subclasses must be in the same package (or module).

```java
public sealed class Shape permits Circle, Rectangle, Triangle {}

public final class Circle extends Shape { ... }
public non-sealed class Rectangle extends Shape { ... } // open for further extension
public sealed class Triangle extends Shape permits EquilateralTriangle { ... }
```

Combines well with pattern matching in `switch` (preview in Java 17, standard in Java 21):

```java
double area = switch (shape) {
    case Circle c    -> Math.PI * c.radius() * c.radius();
    case Rectangle r -> r.width() * r.height();
    case Triangle t  -> t.base() * t.height() / 2;
};
```
