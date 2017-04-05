# The Fluent python library

Use python in a more object oriented, saner and shorter way.

## WARNING
First: A word of warning. This library is an experiment. It is based on a wrapper that aggressively 
wraps anything it comes in contact with and tries to stay invisible from then on (apart from adding methods).
However this means that this library is probably quite unsuitable for use in bigger projects. Why? 
Because the wrapper will spread in your runtime image like a virus, 'infecting' more and more objects 
causing strange side effects. That being said, this library is perfect for short scripts and especially 
'one of' shell commands. Use it's power wisely!

## Introduction

This library is heavily inspired by jQuery and underscore / lodash in the javascript world. Or you 
could say that it is inspired by SmallTalk and in extension Ruby and how they deal with collections 
and how to work with them.

In JS the problem is that the standard library sucks very badly and is missing many of the 
most important convenience methods. Python is better in this regard, in that it has (almost) all 
those methods available somewhere. BUT: quite a lot of them are available on the wrong object or 
are free methods where they really should be methods. Examples: `str.join` really should be on iterable.
`map`, `zip`, `filter` should really be on iterable. Part of this problem comes from the design 
choice of the python language, to provide a strange kind of minimal duck typing interface with the __*__ 
methods that the free methods like `map`, `zip`, `filter` then use. This however has the unfortunate
side effect in that writing python code using these methods often requires the reader to mentally skip 
back and forth in a line to parse what it does. While this is not too bad for simple usage of these 
functions, it becomes a nightmare if longer statements are built up from them.

Don't believe me? Try to parse this simple example as fast as you can:

    >>> map(print, map(str.upper, sys.stdin.read().split('\n')))

How many backtrackings did you have to do? To me this code means, finding out that it starts in the 
middle at `sys.stdin.read().split('\n')`, then I have to backtrack to `map(str.upper, …)`, then to 
`map(print, …)`. Then while writing, I have to make sure that the number of parens at the end are 
correct, which is something I usually have to use editor support for as it's quite hard to accurately 
identify where the matching paren is.

The problem with this? This is hard! Hard to write, as it doesn't follow the way I think about this 
statement. Literally, this means I usually write these statements from the inside out and wrap them
using my editor as I write them. As demonstrated above, it's also hard to read - requireing quite a 
bit of backtracking.

So, what's the problem you say? Just don't do it, it's not pythonic you say! Well, Python has two 
main workarounds available for this mess. One is to use list comprehension / generator 
statements like this:

    >>> [print(line.upper()) for line in sys.stdin.read().split('\n')]

This is clearly better. Now you only have to skip back and forth once instead of twice Yay! Win! 
To me that is not a good workaround. Sure it's nice to easily be able to create generators this 
way, but it still requires of me to find where the statement starts and to backtrack to the beginning 
to see what is happening. Oh, but they support filtering too!

    >>> [print(line.upper()) for line in sys.stdin.read().split('\n') if line.upper().startswith('FNORD')]

Well, this is little better. For one thing, this doesn't solve the backtracking problem, but more 
importantly, if the filtering has to be done on the processed version (here artificially on 
`line.upper().startswith()`) then the operation has to be applied twice - which sucks because you have to write it twice, but also because it is computed twice.

The solution? Nest them!

    >>> [print(line) for line in (line.upper() for line in sys.stdin.read().split('\n')) if line.startswith('FNORD')]

Do you start seing the problem?

Compare it to this:

    >>> for line in sys.stdin.read().split('\n'):
    >>>     uppercased = line.upper()
    >>>     if uppercased.startswith('FNORD'):
    >>>         print(uppercased)

Almost all my complaints are gone. It reads and writes almost completely in order it is computed.
Easy to read, easy to write - but one drawback. It's not an expression - it's a bunch of statements.
Which means that it's not easily combinable and abstractable with higher order methods or generators. 
Also (to complain on a high level), you had to invent two variable names `line` and `uppercased`. 
While that is not bad, especially if they explain what is going on - in this case it's not really 
helping _and_ (drummroll) it requires some backtracking and buildup of mental state to read. Oh well.

Of course you can use explaining variables to untangle the mess of using higher order functions too:

Consider this code:

    >>> cross_product_of_dependency_labels = \
    >>>     set(map(frozenset, itertools.product(*map(attrgetter('_labels'), dependencies))))

That certainly is hard to read (and write). Pulling out explaining variables, makes it better. Like so:

    >>> labels = map(attrgetter('_labels'), dependencies)
    >>> cross_product_of_dependency_labels = set(map(frozenset, itertools.product(*labels)))

Better, but still hard to read. Sure, those explaining variables are nice and sometimes 
essential to understand the code. - but it does take up space in lines, and space in my head 
while parsing this code. The question would be - is this really easier to read than something 
like this?

    >>> cross_product_of_dependency_labels = _(dependencies) \
    >>>     .map(_.each._labels) \
    >>>     .star_call(itertools.product) \
    >>>     .map(frozenset) \
    >>>     .call(set)

Sure you are not used to this at first, but consider the advantages. The intermediate variable 
names are abstracted away - the data flows through the methods completely naturally. No jumping 
back and forth to parse this at all. It just reads and writes exactly in the order it is computed.
What I think that I want to accomplish, I can write down directly in order. Oh, and I don't have 
to keep track of extra closing parantheses at the end of the expression.

So what is the essence of all of this?

Python is an object oriented language - but it doesn't really use what object orientation has tought 
us about how we can work with collections and higher order methods in the languages that came before it
(especially SmallTalk, but more recently also Ruby). Why can't I make those beautiful fluent call chains 
that SmallTalk could do 20 years ago in Python today?

Well, now you can.

## Features

To enable this style of coding this library has some features that might not be so obvious at first.

### Aggressive (specialized) wrapping

The most important entry point for this library is the function `wrap` or the perhaps preferrable and 
shorter alias `_`:

    >>> _(something)
    >>> # or
    >>> wrap(something)

`wrap` is a factory function that returns a subclass of Wrapper, the basic and main object of this library.

This does two things: First it ensures that every attribute access, item access or method call off of 
the wrapped object will also return a wrapped object. This means that once you wrap something, unless 
you unwrap it explicitly via `.unwrap` or `._` it stays wrapped - pretty much no matter what you do 
with it. The second thing this does is that it returns a subclass of Wrapper that has a specialized set 
of methods depending on the type of what is wrapped. I envision this to expand in the future, but right 
now the most usefull wrappers are: Iterable, where we add all the python collection functions (map, 
filter, zip, reduce, …) as well as a good batch of methods from itertools and a few extras for good 
measure. Callable, where we add `.curry()` and `.compose()` and Text, where most of the regex methods 
are added.

### Imports as expressions

Import statements are (ahem) statements in python. This is fine, but can be really annoying at times.
Consider this shell text filter written in python:

    $ curl -sL 'https://www.iblocklist.com/lists.php' | egrep -A1 'star_[345]' | python3 -c "import sys, re; from xml.sax.saxutils import unescape; print('\n'.join(map(unescape, re.findall(r'value=\'(.*)\'', sys.stdin.read()))))" 

Sure it has all the backtracking problems I talked about already. Using fluent this would already be much better.

    $ curl -sL 'https://www.iblocklist.com/lists.php' \
        | egrep -A1 'star_[345]' \
        | python3 -c "from fluent import *; import sys, re; from xml.sax.saxutils import unescape; _(sys.stdin.read()).findall(r'value=\'(.*)\'').map(unescape).map(print)"

But this still leaves the problem that it has to start with this fluff 

    from fluent import *; import sys, re; from xml.sax.saxutils import unescape;

This doesn't really do anything to make it easier to read and write and is almost half the characters 
it took to achieve the wanted effect. Wouldn't it be nice if you could have 
some kind of object (lets call it `lib` for lack of a better word), where you could just access the whole 
python library via attribute access and let it's machinery handle importing behind the scenes?

Like this:

    $ curl -sL 'https://www.iblocklist.com/lists.php' | egrep -A1 'star_[345]' | python3 -m fluent "lib.sys.stdin.read().findall(r'value=\'(.*)\'').map(lib.xml.sax.saxutils.unescape).map(print)"

How's that for reading and writing if all the imports are inlined? Oh, and of course everything imported 
via `lib` comes already pre-wrapped, so your code becomes even shorter.

More formally:The `lib` object, which is a wrapper around the python import machinery, allows to import 
anything that is accessible by import to be imported as an expression for inline use.

So instead of

    >>> import sys
    >>> input = sys.stdin.read()

You can do

    >>> input = lib.sys.stdin.read()

As a bonus, everything imported via lib is already pre-wrapped, so you can chain off of it immediately.

`lib` is also available on `_` which is itself just an alias for `wrap`. This is usefull if you want 
to import fewer symbols from fluent or want to import the library under a custom name

    >>> from fluent import _ # alias for wrap
    >>> _.lib.sys.stdin.split('\n').map(str.upper).map(print)

    >>> from fluent import _ as fluent # alias for wrap
    >>> fluent.lib.sys.stdin.split('\n').map(str.upper).map(print)

Not sure if that is so super usefull though, as you could also just do:

    >>> import fluent
    >>> fluent.lib.sys.stdin.split('\n').map(str.upper).map(print)

### Generating lambda's from expressions

`lambda` is great - it's often exactly what the doctor ordered. But it can also be a bit annyoing
 if you have to write it down everytime you just want to get an attribute or call a method on every 
object in a collection.

    >>> _([dict(fnord='foo'), dict(fnord='bar')]).map(lambda each: each['fnord']) == ['foo', 'bar]
    >>> class Foo(object):
    >>>     attr = 'attrvalue'
    >>>     def method(self, arg): return 'method+'+arg
    >>> _([Foo(), Foo()]).map(lambda each: each.attr) == ['attrvalue', 'attrvalue']
    >>> _([Foo(), Foo()]).map(lambda each: each.method('arg')) == ['method+arg', 'method+arg']

Sure it works, but wouldn't it be nice if we could save a variable and do this a bit shorter? 
I mean, python does have attrgetter, itemgetter and methodcaller - they are just a bit 
inconvenient to use:

    >>> from operator import itemgetter, attrgetter, methodcaller
    >>> _([dict(fnord='foo'), dict(fnord='bar')]).map(itemgetter('fnord')) == ['foo', 'bar]
    >>> class Foo(object):
    >>>     attr = 'attrvalue'
    >>>     def method(self, arg): return 'method+'+arg
    >>> _([Foo(), Foo()]).map(attrgetter(attr)) == ['attrvalue', 'attrvalue']
    >>> _([Foo(), Foo()]).map(methodcaller(method, 'arg')) == ['method+arg', 'method+arg']

So there is an object `_.each` that just exposes a bit of syntactic shugar for these 
(and a few operators). Basically, everything you do to `_.each` it will do to each object
in the collection:

    >>> _([1,2,3]).map(_.each + 3) == [4,5,6]
    >>> _([1,2,3]).filter(_.each < 3) == [1,2]
    >>> _([1,2,3]).map(- _.each) == [-1,-2,-3]
    >>> _([dict(fnord='foo'), dict(fnord='bar')]).map(_.each['fnord']) == ['foo', 'bar]
    >>> class Foo(object):
    >>>     attr = 'attrvalue'
    >>>     def method(self, arg): return 'method+'+arg
    >>> _([Foo(), Foo()]).map(_.each.attr) == ['attrvalue', 'attrvalue']
    >>> _([Foo(), Foo()]).map(_.each.call.method('arg')) == ['method+arg', 'method+arg']

Yeah I know `_.each.call.*()` is crude - but I haven't found a good syntax to get rid of 
the .call yet. Feedback welcome.

### Chaining off of methods that return None

A major nuissance for using fluent interfaces are methods that return None. Now this is mostly 
a feature of python, where methods that don't have a return statement return None.
While this is way better than e.g. Ruby where that will just return the value of the last 
expression - which means objects constantly leak internals, it is very annoying if you want to 
chain off of one of these method calls. Fear not though, fluent has you covered. :) 
Fluent wrapped objects will behave more like SmallTalk objects, in that they pretend
that every method that returns None actually returned self - thus allowing chaining. So this just works:

    >>> _([3,2,1]).sort().reverse().call(print)

Even though both sort() and reverse() return None

Of course, if you unwrap at any point with `.unwrap` or `._` you will get the true return value of `None`.

### Easy Shell Filtering with Python

@TODO add examples


## Famous Last Words

This library tries to do a little of what underscore does for javascript. Just provide the missing glue to make the standard library nicer and easier to use - especially for short oneliners or short script. Have fun!

While I know that this is not something you want to use in big projects (see warning at the beginning) 
I envision this to be very usefull in quick python scripts and shell one liner filters, where python was previously just that little bit too hard to use, that 'overflowed the barrel' and prevented you from doing so.
"""
