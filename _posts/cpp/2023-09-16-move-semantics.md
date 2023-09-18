---
authors: [gaurav]
layout: post
title: Move Semantics
categories: [cpp]
tags: [c++, c++11, move, move constructor, move semantics]
---

C++11 introduced numerous new features, with one of the most significant additions being the concept
of move semantics. Move semantics enable developers to enhance the performance of their code by
minimizing unnecessary object copying, particularly in scenarios where copying is
resource-intensive.

## What Is Move Semantics

Move semantics are the principles and mechanisms that govern how objects are transferred or moved
from one location to another, typically with a focus on resource management and efficiency.

1. `Ownership Transfer`: Enable the transfer of ownership of resource such as memory or file
   handles from source to destination
2. `Valid Source Object`: After move operation the source object is left in a valid state, typically
   unspecified but valid state so that it can be reassigned or destroyed properly.
3. `Efficient Transfer`: Move semantics optimize the process of transferring data by avoiding
   unnecessary duplication

Let's try to understand it with the help of a diagram.

![Move Semantics](/assets/img/cpp/move.svg){: width="800" }

In this context, `source` represents a container containing various shapes, with each element
initially pointing to a distinct shape object. When a move operation is performed from `source` to
`destination`, the individual shape elements are effectively relocated, meaning that ownership of
each shape element is transferred to its corresponding element in the `destination` container.
This fundamental concept is formally knowns as `move semantics`.

Upon close observation, it becomes apparent that the memory addresses where these shapes are stored
remain unaltered; what has undergone transformation is the ownership structure.

## Example

{: file="move_semantics.cpp"}

```c++
#include <cassert>
#include <iostream>
#include <memory>

int main() {
    auto source = std::unique_ptr<int>(new int); // 1. allocates memory
    *source = 10;

    std::cout << "source points to     : " << source.get() << std::endl;
    std::cout << "value: " << *source << std::endl;

    auto destination = std::move(source);        // 2. move source to destination
    std::cout << "destination points to: " << destination.get() << std::endl;
    std::cout << "value: " << *destination << std::endl;

    assert(source == nullptr);                   // 3. source is null
}
```

{: file="output"}
{: .nolineno }

```bash
source points to     : 0x602000000010, value: 10
destination points to: 0x602000000010, value: 10
```

Above code illustrates the principle of `move semantics`.

1. `auto source = std::unique_ptr<int>(new int)`: allocates memory to store an `int`
2. `auto destination = std::move(source)`: here we move the ownership of the memory from source to
   destination. See the output `destination` now points to same memory address which was earlier
   pointed by `source`.
3. `assert(source == nullptr)`: After move operation ownership is transferred from `source` to
   `destination` and `source` no longer points to previously allocated memory address, instead, it
   now points to `nullptr`

## Move Constructor And Move Assignment

In c++, [copy semantics][01] rely on the use of [copy constructors][02] and [copy assignment
operators][03] to duplicate objects or data. Similarly, c++11 introduced `move semantics`, which
leverage `rvalue reference`, `move constructors` and `move assignment operators` to efficiently
transfer ownership of resources or data.

{: file="move.cpp"}

```c++
#include <cassert>
#include <memory>
#include <utility>

struct DynamicArray {
    DynamicArray(int size)
    : m_size {size}
    , m_ptr {new int[size]}
    {
    }

    ~DynamicArray() {
        delete[] m_ptr;
    }

    DynamicArray(DynamicArray&& src) noexcept {            // 1,2. r-value reference, Move ctor
        m_size = std::exchange(src.m_size, -1);
        m_ptr  = std::exchange(src.m_ptr, nullptr);        // 4. efficient moving
    }

    DynamicArray& operator=(DynamicArray&& src) noexcept { // 3. Move assignment
        if (this == &src) {                                // 3. self assignment check
            return *this;
        }

        delete[] m_ptr;                                    // 3. delete any already assigned memory
        m_size = std::exchange(src.m_size, -1);            // 6. transfer value
        m_ptr  = std::exchange(src.m_ptr, nullptr);        // 5. transfer value
        return *this;
    }

    int m_size;
    int* m_ptr;
};

int main() {
    DynamicArray arr(10);
    DynamicArray arrMoved = std::move(arr);
    assert(arr.m_size == -1);
    assert(arr.m_ptr == nullptr);

    arr = std::move(arrMoved);
    assert(arr.m_size == 10);
    assert(arr.m_ptr != nullptr);
}
```

Key differences compared to copy semantics:

1. `Rvalue References (&&)`: Move semantics employ rvalue references `&&` to capture temporary
   values, such as literals or temporary objects.
2. `Move Constructor`: The move constructor `DynamicArray(DynamicArray&& other)` is responsible
   for transferring the contents and ownership of one object (the source, `other`) to a newly
   created object (the destination, `this`). It efficiently moves data members, like `m_size` and
   `m_ptr`, while invalidating the source's state to avoid `double-free` issues.
3. `Move Assignment Operator`: The move assignment operator
   (`DynamicArray& operator=(DynamicArray&& src)`) is used to transfer ownership and data from one
   object to another, similar to the move constructor. It also includes safeguards, such as
   self-assignment checks and proper resource cleanup.
4. `Efficiency and Memory`: Unlike traditional copying, move semantics do not involve allocating
   new memory or deep-copying data. Instead, they efficiently reassign ownership of existing
   resources, resulting in improved performance, especially when handling large or complex objects.
5. `Nullifying Pointers`: A crucial step in move semantics is nullifying pointers in the source
   object after transferring ownership to the destination. This prevents `double-free` issues and
   ensures that the source object is in a valid but unspecified state.
6. `std::exchange(src.m_size, -1)`: It is an utility to simplify the logic of transfer and
   nullifying the source object. It can be simplified as below.

   ```c++
   m_size = src.m_size;
   src.m_size = -1;
   ```

## Benefits of Move Semantics

1. `Improved Performance`: Move semantics reduces unnecessary overhead by transferring ownership of
   resources (e.g., memory) rather than copying them. This is particularly advantageous for objects
   that are costly to copy, such as large containers or objects with complex data structures.
2. `Resource Management`: Move semantics is essential for efficient resource management. Classes
   responsible for managing resources like memory (e.g., std::unique_ptr), file handles, or
   network connections can utilize move semantics to safely transfer ownership of these resources.
   This prevents resource leaks and ensures proper cleanup.
3. `Enhanced API Design`: Move semantics empowers better API design by enabling the creation of
   functions that take ownership of their arguments. For instance, you can define functions that
   accept `rvalue` references to indicate that they will assume ownership of the passed object.

## When to Use Move Semantics

> With great power comes great responsibility. - Uncle Ben
{: .prompt-warning }

While move semantics is a potent tool, it should be applied judiciously. Not all objects benefit
from move semantics.

For instance, in the code above, moving an `int` is equivalent to copying it, so there is no point
in using `x = std::move(y)` for simple data types like `int`.

Use move semantics in the following scenarios:

1. For Expensive-to-Copy Objects
2. When Your Object Manages a Resource: If your object handles resources such as memory, locks,
   file handles, or network connections.

---

[01]: {% link _posts/cpp/2023-09-13-copy-semantics.md %}
[02]: {% link _posts/cpp/2023-09-13-copy-semantics.md %}
[03]: {% link _posts/cpp/2023-09-13-copy-semantics.md %}
