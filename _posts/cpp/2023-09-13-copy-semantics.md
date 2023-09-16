---
authors: [gaurav]
layout: post
title: Copy Semantics
categories: [cpp]
tags: [c++, c++98, c++03, copy, copy-constructor, copy-semantics]
---

Copy semantics refer to the rules and mechanisms by which objects are copied or cloned when they
are assigned to another object or passed as function arguments. It creates objects that are
`equivalent` and `independent` i.e

1. `source == destination`
2. modification to one object does not cause modification to other

{: file="copy.cpp" }

```c++
#include <cassert>

struct Rectangle {                // plain old datatypes (POD)
    int length;
    int breadth;
};

int area(Rectangle r) {           // pass by value, implicit copy
    return r.length * r.breadth;
}

int main() {
    int x = 10;
    int y = x;                   // 1. construct, implicit copy
    assert(x == y);

    Rectangle rect {10, 20};
    assert(area(rect) == 200);   // 2. call area,
}
```

1. `int y = x;` copies the value `10` from variable `x` to `y`.
2. call to a function `area(rect)` copies values stored in `rect.length` and `rect.breadth` to
parameter `r.length` and `r.breadth`

By default compiler generates a default copy constructor and a default copy assignment operator if
required, which performs `member wise copy` i.e it copies each member from source to destination.

In case of basic datatypes such as `int` it is just copying a single value `y = x` and in case of
plain old datatypes (POD) it copies each member variable from source to destination `r = rect`.

This is also known as `shallow copy`. For basic datatypes and POD this is not an issue. But for user
defined classes/structures which include pointer member variables, this can be problematic.

## Shallow Copy

{: file="shallow_copy.cpp" }

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
g++ -std=c++11 -fsanitize=address shallow_copy.cpp && ./a.out

=================================================================
==11528==ERROR: AddressSanitizer: attempting double-free on 0x604000000010 in thread T0:
    #0 0x7ff4a3010780 in operator delete[](void*)
```

As described earlier, compiler provided copy constructor performs member by member copy i.e
`arr_copy.m_ptr = arr.m_ptr`.

So now `m_ptr` of both the objects are pointing to the same address. And this is bad.

1. `No independent modifications`: Changes done through `arr.m_ptr` will be reflected in
   `arr_copy.m_ptr` and vice-versa
2. `Undefined behavior`: Due to limited scope `arr_copy` is destroyed first resulting in deletion of
   memory pointed by `arr_copy.m_ptr`. Now any operation done through `arr.m_ptr` will result in
   undefined behavior since the memory block to which `arr.m_ptr` is pointing is already deleted.
   Pointing to deleted memory is also known as `dangling pointer`.
3. `Double free`: At the end of the program both objects go out of scope and are destroyed. Since
   both the pointers are pointing to the same memory this results in deletion of the same memory
   twice and we can see this error in the output.

To deal with such issues we need `deep copy`.

## Deep Copy

Issue with shallow copy was it simply copies the values directly even in case of pointer variables.
To fix this deep copy first allocates a sepearate memory to pointer member variables and then
copies the contents stored from source memory address to the newly allocated memory address.
Now each copy contains its own unique set of data, even if that data includes references or
pointers to other objects.

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
    printArray(arr);             // creates a temporary copy of arr and passes to printArray
}
```

1. `m_ptr {new int[m_size]}`: Separate memory is allocated to `arr_copy.m_ptr`
2. `std::copy(o.m_ptr, o.m_ptr + o.m_size, m_ptr);`: copies values stored at memory address pointed
    by `arr.m_ptr` to newly allocated memory address `arr_copy.m_ptr`

### Why Copy Constructor Takes Argument By Reference

Canonical signature of copy constructor is `DynamicArray(const DynamicArray& o)`.

If it will recieve the argument by pass by value, then when copy constrcutor is invoked it will need
a copy of the argument which will in turn invoke the copy constructor, which would again call the
copy constructor and this will continue recursively until stack is full.

So it takes a parameter by reference.

### Why Copy Constructor Takes Const Argument

To avoid accidental modfications to the source object. Also const reference `const &` allows copy
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
DynamicArray& operator=(const DynamicArray& o)
{
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

Implentation of copy constructor and copy assignment operator is almost same with three small but
important differences.

1. Self assignment check `if (this == &o)`: Statement such as `arr = arr` is a self assignment, if
   the program does not check for self assignment then it will result in deletion of `m_ptr` first
   and on next line try to allocate new memory and will loose its original content.
2. Delete pre-allocated memory `delete[] m_ptr;`: In assignment both the object already exist and
   `m_ptr` might be pointing to valid memory. Allocating new memory without delete will result in
   memory leak.
3. `return *this;`:  Returning reference to self is not mandatory but then you cannot perform
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

To address this inefficiency, c++11 introduced the concept of `move semantics`. If you're a
technical enthusiast looking to optimize your code and understand the inner workings of move
semantics, dive into our next blog on the topic.
