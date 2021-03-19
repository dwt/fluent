# fluentpy - The fluent Python library

Fluentpy provides fluent interfaces to existing APIs such as the standard library, allowing you to use them in an object oriented and fluent style.

Fluentpy is inspired by JavaScript's `jQuery` and `underscore` / `lodash` and takes some inspiration from the collections API in Ruby and SmallTalk.

Please note: **This library is based on an wrapper**, that returns another wrapper for any operation you perform on a wrapped value. See the section **Caveats** below for details.

See [Fowler](https://www.martinfowler.com/bliki/FluentInterface.html), [Wikipedia](https://de.wikipedia.org/wiki/Fluent_Interface) for definitions of fluent interfaces.

[![Documentation Status](https://readthedocs.org/projects/fluentpy/badge/?version=latest)](https://fluentpy.readthedocs.io/en/latest/?badge=latest) [![CircleCI](https://circleci.com/gh/dwt/fluent.svg?style=svg)](https://circleci.com/gh/dwt/fluent)
![Dependable API Evolution](https://img.shields.io/badge/Dependable%20API%20Evolution-1.0-success)

## Motivation: Why use `fluentpy`?

Many of the most useful standard library methods such as `map`, `zip`, `filter` and `join` are either free functions or available on the wrong type or module. This prevents fluent method chaining.

Let's consider this example:

    >>> list(map(str.upper, sorted("ba,dc".split(","), reverse=True)))
    ['DC', 'BA']

To understand this code, I have to start in the middle at `"ba,dc".split(",")`, then backtrack to `sorted(…, reverse=True)`, then to `list(map(str.upper, …))`. All the while making sure that the parentheses all match up.

Wouldn't it be nice if we could think and write code in the same order? Something like how you would write this in other languages?

    >>> _("ba,dc").split(",").sorted(reverse=True).map(str.upper)._
    ['DC', 'BA']

"Why no, but python has list comprehensions for that", you might say? Let's see:

    >>> [each.upper() for each in sorted("ba,dc".split(","), reverse=True)]
    ['DC', 'BA']

This is clearly better: To read it, I have to skip back and forth less. It still leaves room for improvement though. Also, adding filtering to list comprehensions doesn't help:

    >>> [each.upper() for each in sorted("ba,dc".split(","), reverse=True) if each.upper().startswith('D')]
    ['DC']

The backtracking problem persists. Additionally, if the filtering has to be done on the processed version (on `each.upper().startswith()`), then the operation has to be applied twice - which sucks because you write it twice and compute it twice.

The solution? Nest them!

    >>> [each for each in 
            (inner.upper() for inner in sorted("ba,dc".split(","), reverse=True))
            if each.startswith('D')]
    ['DC']

Which gets us back to all the initial problems with nested statements and manually having to check closing parentheses.

Compare it to this:

    >>> processed = []
    >>> parts = "ba,dc".split(",")
    >>> for item in sorted(parts, reverse=True):
    >>>     uppercases = item.upper()
    >>>     if uppercased.startswith('D')
    >>>         processed.append(uppercased)

With basic Python, this is as close as it gets for code to read in execution order. So that is usually what I end up doing.

But it has a huge drawback: It's not an expression - it's a bunch of statements. That makes it hard to combine and abstract over it with higher order methods or generators. To write it you are forced to invent names for intermediate variables that serve no documentation purpose, but force you to remember them while reading.

Plus (drumroll): parsing this still requires some backtracking and especially build up of mental state to read.

Oh well.

So let's return to this:

    >>> (
        _("ba,dc")
        .split(",")
        .sorted(reverse=True)
        .map(str.upper)
        .filter(_.each.startswith('D')._)
        ._
    )
    ('DC',)

Sure you are not used to this at first, but consider the advantages. The intermediate variable names are abstracted away - the data flows through the methods completely naturally. No jumping back and forth to parse this at all. It just reads and writes exactly in the order it is computed. As a bonus, there's no parentheses stack to keep track of. And it is shorter too!

So what is the essence of all of this?

Python is an object oriented language - but it doesn't really use what object orientation has taught us about how we can work with collections and higher order methods in the languages that came before it (I think of SmallTalk here, but more recently also Ruby). Why can't I make those beautiful fluent call chains that SmallTalk could do 30 years ago in Python?

Well, now I can and you can too.

## Features

### Importing the library

It is recommended to rename the library on import:

    >>> import fluentpy as _

or

    >>> import fluentpy as _f

I prefer `_` for small projects and `_f` for larger projects where `gettext` is used.

### Super simple fluent chains

`_` is actually the function `wrap` in the `fluentpy` module, which is a factory function that returns a subclass of `Wrapper()`. This is the basic and main object of this library.

This does two things: First it ensures that every attribute access, item access or method call off of the wrapped object will also return a wrapped object. This means, once you wrap something, unless you unwrap it explicitly via `._` or `.unwrap` or `.to(a_type)` it stays wrapped - pretty much no matter what you do with it. The second thing this does is that it returns a subclass of Wrapper that has a specialized set of methods, depending on the type of what is wrapped. I envision this to expand in the future, but right now the most useful wrappers are: `IterableWrapper`, where we add all the Python collection functions (map, filter, zip, reduce, …), as well as a good batch of methods from `itertools` and a few extras for good measure. CallableWrapper, where we add `.curry()` and `.compose()` and TextWrapper, where most of the regex methods are added. 

Some examples:
    
    # View documentation on a symbol without having to wrap the whole line it in parantheses
    >>> _([]).append.help()
    Help on built-in function append:

    append(object, /) method of builtins.list instance
        Append object to the end of the list.
    
    # Introspect objects without awkward wrapping stuff in parantheses
    >>> _(_).dir()
    fluentpy.wrap(['CallableWrapper', 'EachWrapper', 'IterableWrapper', 'MappingWrapper', 'ModuleWrapper', 'SetWrapper', 'TextWrapper', 'Wrapper', 
    '_', '_0', '_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', 
    …
    , '_args', 'each', 'lib', 'module', 'wrap'])
    >>> _(_).IterableWrapper.dir()
    fluentpy.wrap(['_', 
    …, 
    'accumulate', 'all', 'any', 'call', 'combinations', 'combinations_with_replacement', 'delattr', 
    'dir', 'dropwhile', 'each', 'enumerate', 'filter', 'filterfalse', 'flatten', 'freeze', 'get', 
    'getattr', 'groupby', 'grouped', 'hasattr', 'help', 'iaccumulate', 'icombinations', '
    icombinations_with_replacement', 'icycle', 'idropwhile', 'ieach', 'ienumerate', 'ifilter', 
    'ifilterfalse', 'iflatten', 'igroupby', 'igrouped', 'imap', 'ipermutations', 'iproduct', 'ireshape', 
    'ireversed', 'isinstance', 'islice', 'isorted', 'issubclass', 'istar_map', 'istarmap', 'itee', 
    'iter', 'izip', 'join', 'len', 'map', 'max', 'min', 'permutations', 'pprint', 'previous', 'print', 
    'product', 'proxy', 'reduce', 'repr', 'reshape', 'reversed', 'self', 'setattr', 'slice', 'sorted', 
    'star_call', 'star_map', 'starmap', 'str', 'sum', 'to', 'type', 'unwrap', 'vars', 'zip'])
    
    # Did I mention that I hate wrapping everything in parantheses?
    >>> _([1,2,3]).len()
    3
    >>> _([1,2,3]).print()
    [1,2,3]
    
    # map over iterables and easily curry functions to adapt their signatures
    >>> _(range(3)).map(_(dict).curry(id=_, delay=0)._)._
    ({'id': 0, 'delay': 0}, {'id': 1, 'delay': 0}, {'id': 2, 'delay': 0})
    >>> _(range(10)).map(_.each * 3).filter(_.each < 10)._
    (0, 3, 6, 9)
    >>> _([3,2,1]).sorted().filter(_.each<=2)._
    [1,2]
    
    # Directly work with regex methods on strings
    >>> _("foo,  bar,      baz").split(r",\s*")._
    ['foo', 'bar', 'baz']
    >>> _("foo,  bar,      baz").findall(r'\w{3}')._
    ['foo', 'bar', 'baz']
    
    # Embedd your own functions into call chains
    >>> seen = set()
    >>> def havent_seen(number):
    ...     if number in seen:
    ...         return False
    ...     seen.add(number)
    ...     return True
    >>> (
    ...     _([1,3,1,3,4,5,4])
    ...     .dropwhile(havent_seen)
    ...     .print()
    ... )
    (1, 3, 4, 5, 4)

And much more. [Explore the method documentation for what you can do](https://fluentpy.readthedocs.io/en/latest/fluentpy/fluentpy.html).

### Imports as expressions

Import statements are (ahem) statements in Python. This is fine, but can be really annoying at times.

The `_.lib` object, which is a wrapper around the Python import machinery, allows to import anything that is accessible by import to be imported as an expression for inline use.

So instead of

    >>> import sys
    >>> input = sys.stdin.read()

You can do

    >>> lines = _.lib.sys.stdin.readlines()._

As a bonus, everything imported via lib is already pre-wrapped, so you can chain off of it immediately.

### Generating lambdas from expressions

`lambda` is great - it's often exactly what the doctor ordered. But it can also be annoying if you have to write it down every time you just want to get an attribute or call a method on every object in a collection. For Example:

    >>> _([{'fnord':'foo'}, {'fnord':'bar'}]).map(lambda each: each['fnord'])._
    ('foo', 'bar')
    
    >>> class Foo(object):
    >>>     attr = 'attrvalue'
    >>>     def method(self, arg): return 'method+'+arg
    >>> _([Foo(), Foo()]).map(lambda each: each.attr)._
    ('attrvalue', 'attrvalue')
    
    >>> _([Foo(), Foo()]).map(lambda each: each.method('arg'))._
    ('method+arg', 'method+arg')

Sure it works, but wouldn't it be nice if we could save a variable and do this a bit shorter?

Python does have `attrgetter`, `itemgetter` and `methodcaller` - they are just a bit inconvenient to use:

    >>> from operator import itemgetter, attrgetter, methodcaller
    >>> __([{'fnord':'foo'}, {'fnord':'bar'}]).map(itemgetter('fnord'))._
    ('foo', 'bar')
    >>> _([Foo(), Foo()]).map(attrgetter('attr'))._
    ('attrvalue', 'attrvalue')

    >>> _([Foo(), Foo()]).map(methodcaller('method', 'arg'))._
    ('method+arg', 'method+arg')
    
    _([Foo(), Foo()]).map(methodcaller('method', 'arg')).map(str.upper)._
    ('METHOD+ARG', 'METHOD+ARG')

To ease this, `_.each` is provided. `each` exposes a bit of syntactic sugar for these (and the other operators). Basically, everything you do to `_.each` it will record and later 'play back' when you generate a callable from it by either unwrapping it, or applying an operator like `+ - * / <', which automatically call unwrap.

    >>>  _([1,2,3]).map(_.each + 3)._
    (4, 5, 6)
    
    >>> _([1,2,3]).filter(_.each < 3)._
    (1, 2)
    
    >>> _([1,2,3]).map(- _.each)._
    (-1, -2, -3)
    
    >>> _([dict(fnord='foo'), dict(fnord='bar')]).map(_.each['fnord']._)._
    ('foo', 'bar')
    
    >>> _([Foo(), Foo()]).map(_.each.attr._)._
    ('attrvalue', 'attrvalue')
    
    >>> _([Foo(), Foo()]).map(_.each.method('arg')._)._
    ('method+arg', 'method+arg')
    
    >>> _([Foo(), Foo()]).map(_.each.method('arg').upper()._)._
    ('METHOD+ARG', 'METHOD+ARG')
    # Note that there is no second map needed to call `.upper()` here!
    

The rule is that you have to unwrap `._` the each object to generate a callable that you can then hand off to `.map()`, `.filter()` or wherever you would like to use it.

### Chaining off of methods that return None

A major nuisance for using fluent interfaces are methods that return None. Sadly, many methods in Python return None, if they mostly exhibit a side effect on the object. Consider for example `list.sort()`. But also all methods that don't have a `return` statement return None. While this is way better than e.g. Ruby where that will just return the value of the last expression - which means objects constantly leak internals - it is very annoying if you want to chain off of one of these method calls.

Fear not though, Fluentpy has you covered. :)

Fluent wrapped objects will have a `self` property, that allows you to continue chaining off of the previous 'self' object.

    >>> _([3,2,1]).sort().self.reverse().self.call(print)

Even though both `sort()` and `reverse()` return `None`.

Of course, if you unwrap at any point with `.unwrap` or `._` you will get the true return value of `None`.


### Easy Shell Filtering with Python

It could often be super easy to achieve something on the shell, with a bit of Python. But, the backtracking (while writing) as well as the tendency of Python commands to span many lines (imports, function definitions, ...), makes this often just impractical enough that you won't do it.

That's why `fluentpy` is an executable module, so that you can use it on the shell like this:

    $ echo 'HELLO, WORLD!' \
        | python3 -m fluentpy "lib.sys.stdin.readlines().map(str.lower).map(print)"
    hello, world!


In this mode, the variables `lib`, `_` and `each` are injected into the namespace of of the `python` commands given as the first positional argument.

Consider this shell text filter, that I used to extract data from my beloved but sadly pretty legacy del.icio.us account. The format looks like this:

    $ tail -n 200 delicious.html|head
    <DT><A HREF="http://intensedebate.com/" ADD_DATE="1234043688" PRIVATE="0" TAGS="web2.0,threaded,comments,plugin">IntenseDebate comments enhance and encourage conversation on your blog or website</A>
    <DD>Comments on static websites
    <DT><A HREF="http://code.google.com/intl/de/apis/socialgraph/" ADD_DATE="1234003285" PRIVATE="0" TAGS="api,foaf,xfn,social,web">Social Graph API - Google Code</A>
    <DD>API to try to find metadata about who is a friend of who.
    <DT><A HREF="http://twit.tv/floss39" ADD_DATE="1233788863" PRIVATE="0" TAGS="podcast,sun,opensource,philosophy,floss">The TWiT Netcast Network with Leo Laporte</A>
    <DD>Podcast about how SUN sees the society evolve from a hub and spoke to a mesh society and how SUN thinks it can provide value and profit from that.
    <DT><A HREF="http://www.xmind.net/" ADD_DATE="1233643908" PRIVATE="0" TAGS="mindmapping,web2.0,opensource">XMind - Social Brainstorming and Mind Mapping</A>
    <DT><A HREF="http://fun.drno.de/pics/What.jpg" ADD_DATE="1233505198" PRIVATE="0" TAGS="funny,filetype:jpg,media:image">What.jpg 480×640 pixels</A>
    <DT><A HREF="http://fun.drno.de/pics/english/What_happens_to_your_body_if_you_stop_smoking_right_now.gif" ADD_DATE="1233504659" PRIVATE="0" TAGS="smoking,stop,funny,informative,filetype:gif,media:image">What_happens_to_your_body_if_you_stop_smoking_right_now.gif 800×591 pixels</A>
    <DT><A HREF="http://www.normanfinkelstein.com/article.php?pg=11&ar=2510" ADD_DATE="1233482064" PRIVATE="0" TAGS="propaganda,israel,nazi">Norman G. Finkelstein</A>

    $ cat delicious.html | grep hosting \                                                                               :(
       | python3  -c 'import sys,re; \
           print("\n".join(re.findall(r"HREF=\"([^\"]+)\"", sys.stdin.read())))'
    https://uberspace.de/
    https://gitlab.com/gitlab-org/gitlab-ce
    https://www.docker.io/

Sure it works, but with all the backtracking problems I talked about already. Using `fluentpy` this could be much nicer to write and read:

     $ cat delicious.html | grep hosting \
         | python3 -m fluentpy 'lib.sys.stdin.read().findall(r"HREF=\"([^\"]+)\"").map(print)'  
    https://uberspace.de/
    https://gitlab.com/gitlab-org/gitlab-ce
    https://www.docker.io/

## Caveats and lessons learned

### Start and end Fluentpy expressions on each line

If you do not end each fluent statement with a `._`, `.unwrap` or `.to(a_type)` operation to get a normal Python object back, the wrapper will spread in your runtime image like a virus, 'infecting' more and more objects causing strange side effects. So remember: Always religiously unwrap your objects at the end of a fluent statement, when using `fluentpy` in bigger projects.

    >>> _('foo').uppercase().match('(foo)').group(0)._

It is usually a bad idea to commit wrapped objects to variables. Just unwrap instead. This is especially sensible, since fluent chains have references to all intermediate values, so unwrapping chains give the garbage collector the permission to release all those objects.

Forgetting to unwrap an expression generated from `_.each` may be a bit surprising, as every call on them just causes more expression generation instead of triggering their effect.

That being said, `str()` and `repr()` output of fluent wrapped objects is clearly marked, so this is easy to debug. 

Also, not having to unwrap may be perfect for short scripts and especially 'one-off' shell commands. However: Use Fluentpys power wisely!

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

### Consider the performance implications of Fluentpy

This library works by creating another instance of its wrapper object for every attribute access, item get or method call you make on an object. Also those objects retain a history chain to all previous wrappers in the chain (to cope with functions that return `None`).

This means that in tight inner loops, where even allocating one more object would harshly impact the performance of your code, you probably don't want to use `fluentpy`.

Also (again) this means that you don't want to commit fluent objects to long lived variables, as that could be the source of a major memory leak.

And for everywhere else: go to town! Coding Python in a fluent way can be so much fun!

## Famous Last Words

This library tries to do a little of what libraries like `underscore` or `lodash` or `jQuery` do for Javascript. Just provide the missing glue to make the standard library nicer and easier to use. Have fun!

I envision this library to be especially useful in short Python scripts and shell one liners or shell filters, where Python was previously just that little bit too hard to use and prevented you from doing so.

I also really like its use in notebooks or in a python shell to smoothly explore some library, code or concept.
