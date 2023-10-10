---
authors: [gaurav]
layout: post
title: Name Hiding
categories: [cpp]
tags: [c++, shadowing, name-hiding]
---

Before diving into the theory or concept of `name hiding`, let's first try to understand the
behavior of the following code snippet.


{: file="name_hiding.cpp"}

```c++
#include <cstdio>

struct Base {
    void foo() {
        puts("Base::foo()");
    }
};

struct Derived : Base {
    void foo(int i) {
        puts("Derived::foo(int)");
    }
};

int main() {
    Derived obj;
    obj.foo();
}
```

```console
Choose the correct output:
1. Base::foo()
2. Derived::foo(int)
3. Base::foo() Derived::foo(int)
4. Compiler error
```

Correct answer is `option 4. Compiler error`

```console
main.cpp: In function 'int main()':
main.cpp:17:12: error: no matching function for call to 'Derived::foo()'
   17 |     obj.foo();
```

The occurrence of a compiler error stems from a concept known as `name hiding`.

## But isn't this function overloading?

No, this is not function overloading. Even though the function names are same they are defined in two different scopes. Concept of function overloading operates within the same scope.

Within the `main` function, when we invoke `obj.foo()`, the compiler iterates through all functions
named `foo` within the scope of `struct Derived`. This process is known as `name lookup`. Once it
finds all the functions with a matching name, it ceases further searches and attempts to match
function arguments. Regrettably, it fails to discover an exact match because the function signature
of the invoked function `foo()` differs from the one found `void foo(int)`.

Consequently, the compiler reports an error, indicating that `no matching function found`.

This issue arises because we've defined a function with the same name in the `struct Derived`,
resulting in the hiding of the implementation `Base::foo`. This phenomenon is termed `name hiding`.

## Solution

### 1. Qualify function call

```c++
int main() {
    Derived obj;
    obj.Base::foo();
}
```

One can explicitly specify the class name or qualify the function call `obj.Base::foo()`. Adding
`Base::` during the call expands the search scope for the compiler and helps to find the required
function.

However this looks ugly.

### 2. `using` directive

```cpp
struct Derived : Base {
    using Base::foo;
    void foo(int) {}
};
```

You can use the `using` directive to bring the parent class function into the scope of child class.
This allows you to access the `struct Base` functions and `struct Derived` using `Derived` object.

## Conclusion

These are the two common approaches to fix the issues related to `name hiding`.
