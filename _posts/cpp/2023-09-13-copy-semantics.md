---
authors: [gaurav]
layout: post
title: Copy Semantics
categories: [cpp]
tags: [c++, c++98, c++03, copy, copy constructor, copy semantics]
---

Copy semantics are the rules and mechanisms governing how objects are duplicated or cloned when
they're assigned to another object or passed as function arguments. These rules ensure that the
objects are `equal` and `independent`.

1. `Equality`: The original object (referred to as the "source") and the new object (the
   "destination") have identical content, `source == destination`. In other words, they are equal
   in terms of their values or state.
2. `Independent`: Modifications made to one object do not affect the other. They remain separate and
   independent instances, even though they might contain the same initial data.

## Implicit Copy

Implicit copying is a process where a copy of an object is created automatically by the programming
language or compiler without explicit instructions from the programmer. This behavior is common for
the objects which follow `value semantics`.

{: file="implicit_copy.cpp" }

```c++
#include <cassert>

struct Rectangle {                // plain old datatypes (POD)
    int length;
    int breadth;
};

int area(Rectangle r) {
    return r.length * r.breadth;
}

int main() {
    int x = 10;
    int y = x;                   // 1. implicit copy of the value
    assert(x == y);

    Rectangle rect {10, 20};
    assert(area(rect) == 200);   // 2. implicit copy, pass by value
}
```

1. In this example value of `x` is implicitly copied to `y`. If you later modify `y`, it does not
   affect the value of `x`.
2. Similarly while calling a function `area(rect)`, `rect` is implicitly copied to `r`.

To facilitate implicit copying, the compiler internally generates default copy constructors and
copy assignment operators, as needed. These generated functions perform a "member-wise copy",
meaning they copy each member from the source object to the destination object.

Implicit copying behaves as expected for basic data types like int and plain old data types.
However, it's crucial to be mindful of potential side effects when dealing with pointers.

## Shallow Copy

{: file="shallow_copy.cpp" }

```c++
#include <cassert>

int main() {
    int* srcPtr = new int(10);   // 1. memory allocation and initialization
    int* destPtr = srcPtr;       // 2. copy value from srcPtr to destPtr

    assert(srcPtr == destPtr);
    assert(*srcPtr == *destPtr);

    *destPtr = 20;
    assert(*srcPtr == 20);       // 3. changes reflected in other object

    delete srcPtr;
    delete destPtr;              // 4. dangling pointer, double free
}
```

{: file="output" }
{: .nolineno }

```bash
g++ -std=c++11 -fsanitize=address shallow_copy.cpp && ./a.out

=================================================================
==18713==ERROR: AddressSanitizer: attempting double-free on 0x602000000010 in thread T0:
    #0 0x7fb4d741c650 in operator delete(void*)
```

In this example, we show the potential issues with implicit copying using pointers:

1. `srcPtr` allocates memory on the heap and initializes it with the value 10.
2. `destPtr` is assigned the memory address from srcPtr, so both pointers point to the same memory.
3. `No independent modifications`: Modifying one pointer (e.g., *destPtr = 20) affects the other
   (*srcPtr), as they point to the same memory location..
4. `Double free`: Deleting `srcPtr` frees the associated memory. However, `destPtr` is left as a
   dangling pointer because it still points to the now-deleted memory. Attempting to delete
   `destPtr` would lead to a double-free issue, causing undefined behavior.
5. `Undefined behavior`: Any operations on `destPtr` after the memory is freed can result in
   undefined behavior because the memory is no longer valid.

Similar example with user defined structure.

{: file="shallow_copy_struct.cpp" }

```c++
#include <cstddef>

struct DynamicArray {
    DynamicArray(size_t size)
    : m_size {size}
    , m_ptr {new int[m_size]}
    {}

    ~DynamicArray() {
        delete[] m_ptr;
    }

    size_t m_size;
    int* m_ptr;
};

int main() {
    DynamicArray arr(10);
    {
        DynamicArray arr_copy(arr); // Copies arr into arr_copy. member by member
    }
}
```

{: file="output" }
{: .nolineno }

```bash
g++ -std=c++11 -fsanitize=address shallow_copy_struct.cpp && ./a.out

=================================================================
==11528==ERROR: AddressSanitizer: attempting double-free on 0x604000000010 in thread T0:
    #0 0x7ff4a3010780 in operator delete[](void*)
```

To avoid the issues of implicit copying with pointers, especially when dealing with dynamic memory
allocation, it's often necessary to implement deep copy mechanisms that duplicate not only the
pointers but also the data they point to, ensuring independent and safe handling of objects.

## Deep Copy

Deep copy involves recreating both the object and the data it holds, guaranteeing that
modifications in one instance don't impact others.

Deep copy is implemented explicitly by the programmer by providing user defined `copy constructor`
and `copy assignment operator`.

![Copy Semantics](/assets/img/cpp/copy.svg){: width="800" }

As can be seen in the image after copy operation members of `destination` and `source` both point to
different address but have same contents (shapes).

### Copy Constructor

{: file="copy_constructor.cpp" }

```c++
#include <iostream>
#include <algorithm>

DynamicArray(const DynamicArray& o)
    : m_size {o.m_size}
    , m_ptr {new int[m_size]}    // 1. memory allocation
    {
        std::copy(o.m_ptr, o.m_ptr + o.m_size, m_ptr);  // 2. copy values from source to dest
    }

void printArray(DynamicArray arr) {
    for (size_t i = 0; i < arr.m_size; ++i) {
        std::cout << i << std::endl;
    }
}

int main() {
    DynamicArray arr(10);
    {
        DynamicArray arr_copy(arr);  // Invokes copy constructor
    }
    printArray(arr);                 // creates a copy of arr and passes to printArray
}
```

1. `m_ptr {new int[m_size]}`: Separate memory is allocated to `arr_copy.m_ptr`
2. `std::copy(o.m_ptr, o.m_ptr + o.m_size, m_ptr);`: copies values stored at memory address pointed
    by `arr.m_ptr` to newly allocated memory address `arr_copy.m_ptr`

### Why Copy Constructor Takes Argument By Reference

Canonical signature of copy constructor is `DynamicArray(const DynamicArray& o)`.

If it will receive the argument by pass by value, then when copy constructor is invoked it will need
a copy of the argument which will in turn invoke the copy constructor, which would again call the
copy constructor and this will continue recursively until stack is full.

So it takes a parameter by reference.

### Why Copy Constructor Takes Const Argument

To avoid accidental modifications to the source object. Also const reference `const &` allows copy
constructor to receive `temporary objects`.

### Copy Assignment

Copy constructor solves only the half problems, we can get into same issues if copy assignment
operator is not provided.

```c++
int main() {
    DynamicArray arr(10);
    DynamicArray other(5);
    other = arr;                 // Invokes compiler provided copy assignment
}
```

Since both the objects already exist, `other = arr` invokes compiler provided assignment operator,
which performs member by member copy and will result in the same issue of two pointers pointing to
the same memory.

{: file="copy_assignment.cpp" }

```c++
DynamicArray& operator=(const DynamicArray& o) {
    if (this == &o) {            // 1. prevents self assignment, arr = arr
        return *this;
    }
    delete[] m_ptr;              // 2. delete any existing memory if any
    m_size = o.m_size;
    m_ptr = new int[m_size];
    std::copy(o.m_ptr, o.m_ptr + o.m_size, m_ptr);
    return *this;
}

int main() {
    DynamicArray arr(10);
    DynamicArray other(1);
    arr = other;                 // Since arr already exists, invokes copy assignment
}
```

Implementation of copy constructor and copy assignment operator is almost same with three small but
important differences.

1. Self assignment check `if (this == &o)`: Statement such as `arr = arr` is a self assignment, if
   the program does not check for self assignment then it will result in deletion of `m_ptr` first
   and on next line try to allocate new memory and will loose its original content.
2. Delete pre-allocated memory `delete[] m_ptr;`: In assignment both the object already exist and
   `m_ptr` might be pointing to valid memory. Allocating new memory without delete will result in
   memory leak.
3. `return *this;`: Returning reference to self is not mandatory but then you cannot perform
   assignment chaining `(a = b = c)`.

## Note

> If you find the need to provide a custom implementation for either the `copy constructor`,
  `copy assignment operator`, or `destructor`, it's a strong indication that you should consider
  providing custom implementations for all three of them. This principle is commonly referred to as
  the `Rule of Three`.
{: .prompt-info }

## Conclusion

Understanding copy semantics is crucial for managing the behavior of your C++ programs and
controlling how user defined structures are copied especially when pointer member variables are
involved.

Copy semantics is an important concept but it has its own downsides. For smaller size objects,
it is tolerable, but for larger ones, it leads to noticeable performance degradation due to the
creation of numerous temporary copies.

To address this inefficiency, c++11 introduced the concept of `move semantics`. If you're
looking to optimize your code and understand the inner workings of move
semantics, dive into our next blog on the topic.
