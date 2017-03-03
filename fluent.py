#!/usr/bin/env python3

"""
Usage:
	
	foo

>>> from fluent_interface import *
>>> import sys
>>> str(sys.stdin).split().map().join()(print)

>>> from fluent import _ # as something if it colides

then start everything with:

>>> _(something)…

to get the right wrapper.

should also have 
    _.imp.$something that could be imported
    _.list, -.str, _.tuple, _.dict, … all the wrappers
    _.wrapper for the generic wrapping logic

This library tries to do a little of what underscore does for javascript. Just provide the missing glue to make the standard library nicer to use.

Consider what to do for __ functions as they cannot easily be wrapped. Implement them all on the wraper?

"""
from __future__ import print_function

__all__ = [
    'list',
    'str',
    'imp', # wrapper for python stdlib, access every stdlib package directly on this without need to import it
]
import re
import types
import functools

__list, __str = (list, str)


# REFACT can I change func so all classes that mix it in will get all their method with func wrapped instances?
class func(object):
    
    def __init__(self, a_function):
        self.__function = a_function
    
    def __getattr__(self, attribute_name):
        return self.__function[attribute_name]
    
    # general utilities
    __call__ = call = lambda self, function: function(self)
    apply = lambda self, function: function(*self)
    tee = lambda self, function: function(self) or self
    
    ## REFACT from here on these are pretty function specific, isolate?
    
    # TODO find out how curry would work, and if func.cast could actually be func.curry
    # REFACT lookup functional library that allow prefilling in the first call and how they do placeholder arguments
    curry = partial = lambda self, *args, **kwargs: functools.partial(self.__function, *args, **kwargs)
    # REFACT this gets out of the ecosystem - but if it doesn't func cann not override __call__
    
    # REFACT find a way to make that just a regular thing
    # chain,cast,compose somehow has the argument order reversed
    # should be >>> str.split = str.split.cast(list)
    # as soon as I get a real function constructor that is usable, cls would become inner
    wrap = chain = cast = compose = classmethod(lambda cls, inner, outer: lambda *args, **kwargs: outer(inner(*args, **kwargs)))
    
class list(list, func): pass
# REFACT add tupple(...)
# REFACT add list(1,2,3, ...) constructor
# REFACT should str get the list methods?
class str(str, func): pass



list.join = lambda self, with_what: str(self.map(str)(with_what.join))
list.format = lambda self, format_string: str(format_string.format(*self))
list.map = lambda self, iterator: list(map(iterator, self))


str.findall = lambda self, pattern: list(re.findall(pattern, self))
 # REFACT can this be generalized to a mixin?
# str.apply = lambda self, function: function(*self)
# str.map = lambda self, iterator: list(map(iterator, self))
# str.split = lambda self, *args, **kwargs: list(__str.split(self, *args, **kwargs))
# str.split = list.cast(__str.split)
# str.split = str.split.cast(list)
# str.split = str.split.chain(list)
# str.split = func.compose(str.split, list)
str.split = func.wrap(str.split, list)
str.upper = lambda self: str(__str.upper(self))
str.prepend = lambda self, other: str(other + self)
str.format = lambda self, format_string: str(format_string.format(self))

# REFACT accept regex as first argument and route to re.split then instead

# REFACT add auto-enhancer object (proxy that auto wraps method / function returns in a suitable subclass)
# REFACT add imp auto importer, that pre-wraps everything he imports. End effect should be that python is seamlessly usable like this.
# REFACT add python -m fluent 'code…' support which auto injects module importer and 
# TODO stuff to implement: zip, len, a way to get at the underlaying value
# TODO add flatten to listlikes
# TODO add sort, groupby, grouped
# TODO add convenience keyword arguments to map etc.
# map(attr='attrname') as shortcut for map(attrgetter('attrname'))
# map(item='itemname') as shortcut for map(itemgetter('itemname'))


import unittest
from pyexpect import expect

class FluentTest(unittest.TestCase):
    pass

class FuncTest(unittest.TestCase):
    
    def test_call(self):
        expect(list([1,2,3]).call(min)) == 1
        expect(list([1,2,3])(min)) == 1
        expect(str('foo').call(str.upper)) == 'FOO'
        expect(str('foo')(str.upper)) == 'FOO'
    
    def test_apply(self):
        expect(list([1,2,3]).apply(lambda x, y, z: z-x-y)) == 0
    
    def test_tee(self):
        side_effect = {}
        def tee(a_list): side_effect['tee'] = a_list.join('-')
        expect(list([1,2,3]).tee(tee)) == [1,2,3]
        expect(side_effect['tee']) == '1-2-3'
    
    def test_curry(self):
        expect(func(lambda x, y: x*y).curry(2, 3)()) == 6
        expect(func(lambda x=1, y=2: x*y).curry(x=3)()) == 6
    
    def test_compose_cast_wraps_chain(self):
        expect(func.compose(lambda x: x*2, lambda x: x+3)(5)) == 13
        expect(func.compose(str.strip, str.capitalize)('  fnord  ')) == 'Fnord'

class FuncWraperTest(unittest.TestCase):
    
    def test_can_still_call_through(self):
        pass

class ListTest(FluentTest):
    
    def test_join(self):
        expect(list(['1','2','3']).join(' ')) == '1 2 3'
        expect(list([1,2,3]).join(' ')) == '1 2 3'
    
    def test_map(self):
        expect(list([1,2,3]).map(lambda x: x * x)) == [1, 4, 9]
    
    def test_format(self):
        expect(list([1,2,3]).format('{} - {} : {}')) == '1 - 2 : 3'
    
    def test_call(self):
        expect(list(['1','2','3']).call(lambda l: ''.join(l))) == '123'


class StrTest(FluentTest):
    
    def test_findall(self):
        expect(str("bazfoobar").findall('ba[rz]')) == ['baz', 'bar']
    
    def test_split(self):
        expect(str('foo\nbar\nbaz').split('\n')) == ['foo', 'bar', 'baz']
        # supports chaining
        expect(str('foo\nbar\nbaz').split('\n').map(str.upper)) == ['FOO', 'BAR', 'BAZ']
        
    def test_prepend(self):
        expect(str('foo').prepend('Fnord: ')) == 'Fnord: foo'
    
    def test_format(self):
        expect(str('foo').format('bar {} baz')) == 'bar foo baz'

class Integration(FluentTest):
    
    def test_extrac_and_decode_URIs(self):
        from xml.sax.saxutils import unescape
        line = '''<td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
            <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ydxerpxkpcfqjaybcssw' readonly='readonly' onClick="select_text('ydxerpxkpcfqjaybcssw');" value='http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz'></td>'''

        actual = str(line).findall(r'value=\'(.*)\'').map(unescape)
        expect(actual) == ['http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&fileformat=p2p&archiveformat=gz']
    
def test():
    from xml.sax.saxutils import unescape
    
    """
    rico:~ dwt$ curl -sL 'https://www.iblocklist.com/lists.php' | egrep -A1 'star_[345]' | python -c "from __future__ import print_function; import sys, re; from from xml.sax.saxutils import unescape; print(map(unescape, re.findall(r'value=\'(.*)\'', sys.stdin.read())))"
    
    # CHECK wenn man das commando eh an -m fluent übergibt kann man auch das global objekt überschreiben und im getattr darin die imports dynamisch auflösen
    python -m fluent "str(sys.stdin).split('\n').map(xml.sax.unescape).map(print)"
    python -m fluent "[print(line) for line in [xml.sax.unescape(line) for line in sys.stdin.split('\n')]]
    """


    line = '''<td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ydxerpxkpcfqjaybcssw' readonly='readonly' onClick="select_text('ydxerpxkpcfqjaybcssw');" value='http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz'></td>'''

    str(line).findall(r'value=\'(.*)\'').map(unescape).map(print)
    str(line).findall(r'value=\'(.*)\'').map(unescape).join('\n').call(print)
    str(line).findall(r'value=\'(.*)\'').map(unescape).join('\n')(print)
    str(line).findall(r'value=\'(.*)\'').map(unescape).apply(print)
    str('lalala').upper().call(print)
    str('fnord').upper()(print)
    str('fnord').upper().prepend('Formatted: ')(print)
    str('fnord').upper().format('Formatted: {}')(print)
    list(['foo', 'bar', 'baz']).map(str.upper).tee(print).join(' ')(print)
    str('foo,bar,baz').split(',').map(print)
    # def to_curry(one, two, three):
    #     print(one, two, three)
    # functools.partial(to_curry, 1, 2, 3)()

    lines = '''<td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ydxerpxkpcfqjaybcssw' readonly='readonly' onClick="select_text('ydxerpxkpcfqjaybcssw');" value='http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='gyisgnzbhppbvsphucsw' readonly='readonly' onClick="select_text('gyisgnzbhppbvsphucsw');" value='http://list.iblocklist.com/?list=gyisgnzbhppbvsphucsw&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='uwnukjqktoggdknzrhgh' readonly='readonly' onClick="select_text('uwnukjqktoggdknzrhgh');" value='http://list.iblocklist.com/?list=uwnukjqktoggdknzrhgh&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='imlmncgrkbnacgcwfjvh' readonly='readonly' onClick="select_text('imlmncgrkbnacgcwfjvh');" value='http://list.iblocklist.com/?list=imlmncgrkbnacgcwfjvh&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='plkehquoahljmyxjixpu' readonly='readonly' onClick="select_text('plkehquoahljmyxjixpu');" value='http://list.iblocklist.com/?list=plkehquoahljmyxjixpu&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='gihxqmhyunbxhbmgqrla' readonly='readonly' onClick="select_text('gihxqmhyunbxhbmgqrla');" value='http://list.iblocklist.com/?list=gihxqmhyunbxhbmgqrla&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='dgxtneitpuvgqqcpfulq' readonly='readonly' onClick="select_text('dgxtneitpuvgqqcpfulq');" value='http://list.iblocklist.com/?list=dgxtneitpuvgqqcpfulq&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='llvtlsjyoyiczbkjsxpf' readonly='readonly' onClick="select_text('llvtlsjyoyiczbkjsxpf');" value='http://list.iblocklist.com/?list=llvtlsjyoyiczbkjsxpf&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='xoebmbyexwuiogmbyprb' readonly='readonly' onClick="select_text('xoebmbyexwuiogmbyprb');" value='http://list.iblocklist.com/?list=xoebmbyexwuiogmbyprb&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='cwworuawihqvocglcoss' readonly='readonly' onClick="select_text('cwworuawihqvocglcoss');" value='http://list.iblocklist.com/?list=cwworuawihqvocglcoss&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='xshktygkujudfnjfioro' readonly='readonly' onClick="select_text('xshktygkujudfnjfioro');" value='http://list.iblocklist.com/?list=xshktygkujudfnjfioro&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='mcvxsnihddgutbjfbghy' readonly='readonly' onClick="select_text('mcvxsnihddgutbjfbghy');" value='http://list.iblocklist.com/?list=mcvxsnihddgutbjfbghy&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='usrcshglbiilevmyfhse' readonly='readonly' onClick="select_text('usrcshglbiilevmyfhse');" value='http://list.iblocklist.com/?list=usrcshglbiilevmyfhse&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_5.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='xpbqleszmajjesnzddhv' readonly='readonly' onClick="select_text('xpbqleszmajjesnzddhv');" value='http://list.iblocklist.com/?list=xpbqleszmajjesnzddhv&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ficutxiwawokxlcyoeye' readonly='readonly' onClick="select_text('ficutxiwawokxlcyoeye');" value='http://list.iblocklist.com/?list=ficutxiwawokxlcyoeye&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='ghlzqtqxnzctvvajwwag' readonly='readonly' onClick="select_text('ghlzqtqxnzctvvajwwag');" value='http://list.iblocklist.com/?list=ghlzqtqxnzctvvajwwag&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='bcoepfyewziejvcqyhqo' readonly='readonly' onClick="select_text('bcoepfyewziejvcqyhqo');" value='http://list.iblocklist.com/?list=bcoepfyewziejvcqyhqo&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='cslpybexmxyuacbyuvib' readonly='readonly' onClick="select_text('cslpybexmxyuacbyuvib');" value='http://list.iblocklist.com/?list=cslpybexmxyuacbyuvib&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_4.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='pwqnlynprfgtjbgqoizj' readonly='readonly' onClick="select_text('pwqnlynprfgtjbgqoizj');" value='http://list.iblocklist.com/?list=pwqnlynprfgtjbgqoizj&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='jhaoawihmfxgnvmaqffp' readonly='readonly' onClick="select_text('jhaoawihmfxgnvmaqffp');" value='http://list.iblocklist.com/?list=jhaoawihmfxgnvmaqffp&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    --
    <td><img src='/sitefiles/star_3.png' height='15' width='75' alt=''></td>
    <td><input style='width:200px; outline:none; border-style:solid; border-width:1px; border-color:#ccc;' type='text' id='zbdlwrqkabxbcppvrnos' readonly='readonly' onClick="select_text('zbdlwrqkabxbcppvrnos');" value='http://list.iblocklist.com/?list=zbdlwrqkabxbcppvrnos&amp;fileformat=p2p&amp;archiveformat=gz'></td>
    '''

    # str(lines).findall(r'value=\'(.*)\'').map(unescape).apply(print)

    blocklists = [u'http://list.iblocklist.com/?list=ydxerpxkpcfqjaybcssw&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=gyisgnzbhppbvsphucsw&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=uwnukjqktoggdknzrhgh&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=imlmncgrkbnacgcwfjvh&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=plkehquoahljmyxjixpu&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=gihxqmhyunbxhbmgqrla&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=dgxtneitpuvgqqcpfulq&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=llvtlsjyoyiczbkjsxpf&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=xoebmbyexwuiogmbyprb&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=cwworuawihqvocglcoss&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=xshktygkujudfnjfioro&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=mcvxsnihddgutbjfbghy&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=usrcshglbiilevmyfhse&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=xpbqleszmajjesnzddhv&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=ficutxiwawokxlcyoeye&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=ghlzqtqxnzctvvajwwag&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=bcoepfyewziejvcqyhqo&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=cslpybexmxyuacbyuvib&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=pwqnlynprfgtjbgqoizj&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=jhaoawihmfxgnvmaqffp&amp;fileformat=p2p&amp;archiveformat=gz', u'http://list.iblocklist.com/?list=zbdlwrqkabxbcppvrnos&amp;fileformat=p2p&amp;archiveformat=gz']

if __name__ == '__main__':
    unittest.main()
    # test()
