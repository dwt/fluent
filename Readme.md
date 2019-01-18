# The Fluent python library

Fluent helps you write more object-oriented and concise python code.

It is inspired by `jQuery` and `underscore` / `lodash` from the JavaScript world. It also takes some inspiration from Ruby / SmallTalk -- in particular, collections and how to work with them.

Please Note: **This library is an experiment.** It is based on a wrapper that aggressively wraps anything it comes in contact with and tries to stay invisible. We'll address this in section **Caveats** below.

[![Documentation Status](https://readthedocs.org/projects/fluentpy/badge/?version=latest)](https://fluentpy.readthedocs.io/en/latest/?badge=latest)

## Introduction: Why use `fluentpy`?

The Python standard library includes many useful, time-saving convenience methods such as `map`, `zip`, `filter` and `join`. The problem that motivated me to write `fluentpy` is that these convenience methods are often available as free functions or on (arguably) the wrong object.

For example, `map`, `zip`, and `filter` all operate on `iterable` objects but they are implemented as free functions. This not only goes against my sense of how object oriented code should behave, but more importantly, writing python code using these free functions requires that the reader must often mentally skip back and forth in a line of code to understand what it does, making the code more difficult to understand.

Let's use the following simple example to analyze this problem:

    >>> map(print, map(str.upper, sys.stdin.read().split('\n')))

How many backtrackings did you have to do? I read this code as follows: 

I start in the middle at `sys.stdin.read().split('\n')`, then I backtrack to `map(str.upper, …)`, then to `map(print, …)`. I also have to make sure that the parentheses all match up.

I find code like this hard to write and hard to understand, as it doesn't follow the way I think about this statement. I don't like to have to write or read statements from the inside out and wrap them using my editor as I write them. As demonstrated above, it's also hard to read - requiring quite a bit of backtracking.

One alternative to the above approach is to use list comprehension / generator statements like this:

    >>> [print(line.upper()) for line in sys.stdin.read().split('\n')]

This is clearly better: I only have to skip back and forth once instead of twice.

This approach still leaves room for improvement though because I have to find where the statement starts and to then backtrack to the beginning to see what is happening. Adding filtering to list comprehensions doesn't help:

    >>> [print(line.upper()) for line in sys.stdin.read().split('\n') if line.upper().startswith('FNORD')]

The backtracking problem persists. Additionally, if the filtering has to be done on the processed version (here artificially on `line.upper().startswith()`) then the operation has to be applied twice - which sucks because you have to write it twice, but also because it is computed twice.

The solution? Nest them!

    >>> [print(line) for line in \
    >>>     (line.upper() for line in sys.stdin.read().split('\n')) \
    >>>          if line.startswith('FNORD')]

Which gets us back to all the initial problems with nested statements and manually having to check for the right amount of closing parens.

Compare it to this:

    >>> for line in sys.stdin.read().split('\n'):
    >>>     uppercased = line.upper()
    >>>     if uppercased.startswith('FNORD'):
    >>>         print(uppercased)

Almost all my complaints are gone. It reads and writes almost completely in order it is computed.

Easy to read, easy to write. So that is usually what I end up doing.

But it has a huge drawback: It's not an expression - it's a bunch of statements.

Why is that bad? Because it means, that it's not easily combinable and abstract-able with higher order methods or generators. Because I have to invent variable names for things that are completely clear from context and that just serve as grease to express the flow of data through the program.

Don't get me wrong, this is the most important function of variables in programs. But in this case, it just makes the code longer and makes it harder to see how data flows through the expressions.

Plus (drumroll): parsing this still requires some backtracking and buildup of mental state to read.

Oh well.

Lets see this in action:

    >>> cross_product_of_dependency_labels = \
    >>>     set(map(frozenset, itertools.product(*map(attrgetter('_labels'), dependencies))))

That certainly is hard to read (and write). Pulling out explaining variables, makes it better. Like so:

    >>> labels = map(attrgetter('_labels'), dependencies)
    >>> cross_product_of_dependency_labels = set(map(frozenset, itertools.product(*labels)))

Better, but still hard to read. Sure, those explaining variables are nice and sometimes essential to understand the code. - but it does take up space in lines, and space in my head while parsing this code. The question would be - is this really easier to read than something like this?

    >>> cross_product_of_dependency_labels = (
    ...     _(dependencies)
    ...     .map(_.each._labels)
    ...     .star_call(itertools.product)
    ...     .map(frozenset)
    ...     .call(set)
    ...     ._
    ... )

Sure you are not used to this at first, but consider the advantages. The intermediate variable names are abstracted away - the data flows through the methods completely naturally. No jumping back and forth to parse this at all. It just reads and writes exactly in the order it is computed.

To me this means, that what I think that I want to accomplish, I can write down directly in order. And I don't have to keep track of extra closing parentheses at the end of the expression.

So what is the essence of all of this?

Python is an object oriented language - but it doesn't really use what object orientation has taught us about how we can work with collections and higher order methods in the languages that came before it (I think of SmallTalk here, but more recently also Ruby). Why can't I make those beautiful fluent call chains that SmallTalk could do 20 years ago in Python today?

Well, now I can and you can too.

## Features

To enable this style of coding this library has some features that might not be so obvious at first.

### Importing the library

It is recommended to import and use the library by renaming it to something locally unique.:

    >>> import fluentpy as _f

or 

    >>> import fluentpy as _

I prefer `_` for small projects and `_f` for larger projects where `gettext` is used.

If you want you can also import the library in the classic way:

    >>> from fluentpy import _, lib, each

But it is not required to import all these symbols, as they are all also available as attributes on `_`. Also, the library exposes itself as an executable module, i.e. the module `fluentpy` itself is the central wrapper function and can be used directly by renaming it to what you need locally.

### Aggressive (specialized) wrapping

`_` is actually the function `wrap` in the `fluentpy` module, which is a factory function that returns a subclass of Wrapper, the basic and main object of this library.

This does two things: First it ensures that every attribute access, item access or method call off of the wrapped object will also return a wrapped object. This means that once you wrap something, unless you unwrap it explicitly via `.unwrap` or `._` it stays wrapped - pretty much no matter what you do with it. The second thing this does is that it returns a subclass of Wrapper that has a specialized set of methods, depending on the type of what is wrapped. I envision this to expand in the future, but right now the most useful wrappers are: `Iterable`, where we add all the python collection functions (map, filter, zip, reduce, …), as well as a good batch of methods from `itertools` and a few extras for good measure. Callable, where we add `.curry()` and `.compose()` and Text, where most of the regex methods are added. [Explore the method documentation for what you can do]()).

TODO add link!


### Easy Shell Filtering with Python

It could often be super easy to achieve something on the shell, with a bit of python. But, the backtracking (while writing) as well as the tendency of python commands to span many lines, makes this often just impractical enough that you won't do it.

That's why `fluentpy` is an executable module, so that you can use it on the shell like this:

    $ python3 -m fluentpy "lib.sys.stdin.readlines().map(str.lower).map(print)"

In this mode, the variables 'lib', '_' and 'each' are injected into the namespace of of the python commands given as the first positional argument.

### Imports as expressions

Import statements are (ahem) statements in python. This is fine, but can be really annoying at times.

Consider this shell text filter written in python:

    $ curl -sL 'https://example.com/lists.php' \
    >    | egrep -A1 'star_[345]' \
    >    | python3 -c "import sys, re; from xml.sax.saxutils import unescape; \
    >          print('\n'.join(map(unescape, re.findall(r'value=\'(.*)\'', sys.stdin.read()))))" 

Sure it has all the backtracking problems I talked about already. Using `fluentpy` this could be much shorter.

    $ curl -sL 'https://example.com/lists.php' \
    >   | egrep -A1 'star_[345]' \
    >   | python3 -c "import fluentpy as _; \
              import sys, re; from xml.sax.saxutils import unescape; \
    >         _(sys.stdin.read()).findall(r'value=\'(.*)\'').map(unescape).map(print)"

This still leaves the problem that it has to start with this fluff 

    import fluentpy as _; import sys, re; from xml.sax.saxutils import unescape;

This doesn't really do anything to make it easier to read and write and is almost half the characters it took to achieve the wanted effect. Wouldn't it be nice if you could have some kind of object (lets call it `lib` for lack of a better word), where you could just access the whole python library via attribute access and let its machinery handle importing behind the scenes?

Like this:

    $ curl -sL 'https://www.iblocklist.com/lists.php' | egrep -A1 'star_[345]' \
    >   | python3 -m fluentpy "lib.sys.stdin.read().findall(r'value=\'(.*)\'') \
    >                        .map(lib.xml.sax.saxutils.unescape).map(print)"

How's that for reading and writing if all the imports are inlined? Oh, and of course everything imported via `lib` comes already pre-wrapped, so your code becomes even shorter.

More formally: The `lib` object, which is a wrapper around the python import machinery, allows to import anything that is accessible by import to be imported as an expression for inline use.

So instead of

    >>> import sys
    >>> input = sys.stdin.read()

You can do

    >>> input = _.lib.sys.stdin.read()

As a bonus, everything imported via lib is already pre-wrapped, so you can chain off of it immediately.

### Generating lambdas from expressions

`lambda` is great - it's often exactly what the doctor ordered. But it can also be annoying if you have to write it down every time you just want to get an attribute or call a method on every object in a collection.

    >>> _([{'fnord'='foo'}, {'fnord'='bar'}]).map(lambda each: each['fnord']) == ['foo', 'bar]
    >>> class Foo(object):
    >>>     attr = 'attrvalue'
    >>>     def method(self, arg): return 'method+'+arg
    >>> _([Foo(), Foo()]).map(lambda each: each.attr) == ['attrvalue', 'attrvalue']
    >>> _([Foo(), Foo()]).map(lambda each: each.method('arg')) == ['method+arg', 'method+arg']

Sure it works, but wouldn't it be nice if we could save a variable and do this a bit shorter?

Python does have `attrgetter`, `itemgetter` and `methodcaller` - they are just a bit inconvenient to use:

    >>> from operator import itemgetter, attrgetter, methodcaller
    >>> _([{'fnord'='foo'}, {'fnord'='bar'}]).map(itemgetter('fnord')) == ['foo', 'bar]
    >>> class Foo(object):
    >>>     attr = 'attrvalue'
    >>>     def method(self, arg): return 'method+'+arg
    >>> _([Foo(), Foo()]).map(attrgetter(attr)) == ['attrvalue', 'attrvalue']
    >>> _([Foo(), Foo()]).map(methodcaller('method', 'arg')) == ['method+arg', 'method+arg']

To ease this the object `_.each` is provided, that just exposes a bit of syntactic sugar for these (and the other operators). Basically, everything you do to `_.each` it will do to each object in the collection:

    >>> _([1,2,3]).map(_.each + 3) == [4,5,6]
    >>> _([1,2,3]).filter(_.each < 3) == [1,2]
    >>> _([1,2,3]).map(- _.each) == [-1,-2,-3]
    >>> _([dict(fnord='foo'), dict(fnord='bar')]).map(_.each['fnord']) == ['foo', 'bar]
    >>> class Foo(object):
    >>>     attr = 'attrvalue'
    >>>     def method(self, arg): return 'method+'+arg
    >>> _([Foo(), Foo()]).map(_.each.attr) == ['attrvalue', 'attrvalue']
    >>> _([Foo(), Foo()]).map(_.each.call.method('arg')) == ['method+arg', 'method+arg']

I know `_.each.call.*()` is crude - but I haven't found a good syntax to get rid of the .call yet. Feedback welcome.

### Chaining off of methods that return None

A major nuisance for using fluent interfaces are methods that return None. Sadly, many methods in python return None, if they mostly exhibit a side effect on the object. Consider for example `list.sort()`.

This is a feature of python, where methods that don't have a return statement return None.

While this is way better than e.g. Ruby where that will just return the value of the last expression - which means objects constantly leak internals - it is very annoying if you want to chain off of one of these method calls.

Fear not though, `fluentpy` has you covered. :)

Fluent wrapped objects will have a `self` property, that allows you to continue chaining off of the previous 'self' object.

    >>> _([3,2,1]).sort().self.reverse().self.call(print)

Even though both `sort()` and `reverse()` return `None`.

Of course, if you unwrap at any point with `.unwrap` or `._` you will get the true return value of `None`.

## Caveats and lessons learned

### Start and end `fluentpy` expressions on each line

If you do not end each fluent statement with a `.unwrap` or `._` operation to get a normal python object back, the wrapper will spread in your runtime image like a virus, 'infecting' more and more objects causing strange side effects. So remember: Always religiously unwrap your objects at the end of a fluent statement, when using `fluentpy` in bigger projects.

    >>> _('foo').uppercase().match('(foo)').group(0)._

I have found that it is usually a good idea _not_ to commit wrapped objects to variables but instead to unwrap them. This is especially sensible, since fluent chains have references to all intermediate values, so you want to unwrap chains to give the garbage collector the permission to release all those objects.

That being said, `str()` and `repr()` output is clearly marked, so this is easy to debug. Also, not having to unwrap may be perfect for short scripts and especially 'one-off' shell commands. Use `fluentpy`'s power wisely!

### Split expression chains into multiple lines

Longer fluent call chains are best written on multiple lines. This helps readability and eases commenting on lines (as your code can become very terse this way).

For short chains one line might be fine.

    _(open('day1-input.txt')).read().replace('\n','').call(eval)._

For longer chains multiple lines are much cleaner.

    day1_input = (
        _(open('day1-input.txt'))
        .readlines()
        .imap(eval)
        ._
    )
    
    seen = set()
    def havent_seen(number):
        if number in seen:
            return False
        seen.add(number)
        return True
    
    (
        _(day1_input)
        .icycle()
        .iaccumulate()
        .idropwhile(havent_seen)
        .get(0)
        .print()
    )

### Consider the performance implications of `fluentpy`

This library works by creating another instance of its wrapper object for every attribute access, item get or method call you make on an object. Also those objects retain a history chain to all previous wrappers in the chain (to cope with functions that return `None`).

This means that in tight inner loops, where even allocating one more object would harshly impact the performance of your code, you probably don't want to use `fluentpy`.

Also (again) this means that you don't want to commit fluent objects to long lived variables, as that could be the source of a major memory leak.

And for everywhere else: go to town! Coding Python in a fluent way can be so much fun!

## Famous Last Words

This library tries to do a little of what libraries like `underscore` or `lodash` or `jQuery` do for Javascript. Just provide the missing glue to make the standard library nicer and easier to use. Have fun!

I envision this library to be especially useful in short python scripts and shell one liners or shell filters, where python was previously just that little bit too hard to use and prevented you from doing so.

I also really like its use in notebooks to smoothly explore some library, code or concept.
