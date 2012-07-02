# This file taken from Python, licensed under the Python License Agreement

# tests common to dict and UserDict
import unittest, sys
import collections
try:
    from collections import UserDict # Python 3
except ImportError:
    from UserDict import UserDict # Python 2

class BasicTestMappingProtocol(unittest.TestCase):
    # This base class can be used to check that an object conforms to the
    # mapping protocol

    # Functions that can be useful to override to adapt to dictionary
    # semantics
    type2test = None # which class is being tested (overwrite in subclasses)

    def _reference(self): # pragma: no cover
        """Return a dictionary of values which are invariant by storage
        in the object under test."""
        return {1:2, "key1":"value1", "key2":(1,2,3)}
    def _empty_mapping(self):
        """Return an empty mapping object"""
        return self.type2test()
    def _full_mapping(self, data):
        """Return a mapping object with the value contained in data
        dictionary"""
        x = self._empty_mapping()
        for key, value in data.items():
            x[key] = value
        return x

    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self.reference = self._reference().copy()

        # A (key, value) pair not in the mapping
        key, value = self.reference.popitem()
        self.other = {key:value}

        # A (key, value) pair in the mapping
        key, value = self.reference.popitem()
        self.inmapping = {key:value}
        self.reference[key] = value

    def test_read(self):
        # Test for read only operations on mapping
        p = self._empty_mapping()
        p1 = dict(p) #workaround for singleton objects
        d = self._full_mapping(self.reference)
        if d is p: # pragma: no cover
            p = p1
        #Indexing
        for key, value in self.reference.items():
            self.assertEqual(d[key], value)
        knownkey = list(self.other.keys())[0]
        self.failUnlessRaises(KeyError, lambda:d[knownkey])
        #len
        self.assertEqual(len(p), 0)
        self.assertEqual(len(d), len(self.reference))
        #__contains__
        for k in self.reference:
            self.assert_(k in d)
        for k in self.other:
            self.failIf(k in d)
        #cmp
        self.assertEqual(p, p)
        self.assertEqual(d, d)
        self.assertNotEqual(p, d)
        self.assertNotEqual(d, p)
        #__non__zero__
        if p: self.fail("Empty mapping must compare to False")
        if not d: self.fail("Full mapping must compare to True")
        # keys(), items(), iterkeys() ...
        def check_iterandlist(iter, lst, ref):
            if sys.version_info[0] < 3: # pragma: no cover
                self.assert_(hasattr(iter, 'next'))
            else: # pragma: no cover
                self.assert_(hasattr(iter, '__next__'))
            self.assert_(hasattr(iter, '__iter__'))
            x = list(iter)
            self.assert_(set(x)==set(lst)==set(ref))
        check_iterandlist(iter(d.keys()), list(d.keys()),
                          self.reference.keys())
        check_iterandlist(iter(d), list(d.keys()), self.reference.keys())
        check_iterandlist(iter(d.values()), list(d.values()),
                          self.reference.values())
        check_iterandlist(iter(d.items()), list(d.items()),
                          self.reference.items())
        #get
        key, value = next(iter(d.items()))
        knownkey, knownvalue = next(iter(self.other.items()))
        self.assertEqual(d.get(key, knownvalue), value)
        self.assertEqual(d.get(knownkey, knownvalue), knownvalue)
        self.failIf(knownkey in d)

    def test_write(self):
        # Test for write operations on mapping
        p = self._empty_mapping()
        #Indexing
        for key, value in self.reference.items():
            p[key] = value
            self.assertEqual(p[key], value)
        for key in self.reference.keys():
            del p[key]
            self.failUnlessRaises(KeyError, lambda:p[key])
        p = self._empty_mapping()
        #update
        p.update(self.reference)
        self.assertEqual(dict(p), self.reference)
        items = list(p.items())
        p = self._empty_mapping()
        p.update(items)
        self.assertEqual(dict(p), self.reference)
        d = self._full_mapping(self.reference)
        #setdefault
        key, value = next(iter(d.items()))
        knownkey, knownvalue = next(iter(self.other.items()))
        self.assertEqual(d.setdefault(key, knownvalue), value)
        self.assertEqual(d[key], value)
        self.assertEqual(d.setdefault(knownkey, knownvalue), knownvalue)
        self.assertEqual(d[knownkey], knownvalue)
        #pop
        self.assertEqual(d.pop(knownkey), knownvalue)
        self.failIf(knownkey in d)
        self.assertRaises(KeyError, d.pop, knownkey)
        default = 909
        d[knownkey] = knownvalue
        self.assertEqual(d.pop(knownkey, default), knownvalue)
        self.failIf(knownkey in d)
        self.assertEqual(d.pop(knownkey, default), default)
        #popitem
        key, value = d.popitem()
        self.failIf(key in d)
        self.assertEqual(value, self.reference[key])
        p=self._empty_mapping()
        self.assertRaises(KeyError, p.popitem)

    def test_constructor(self):
        self.assertEqual(self._empty_mapping(), self._empty_mapping())

    def test_bool(self):
        self.assert_(not self._empty_mapping())
        self.assert_(self.reference)
        self.assert_(bool(self._empty_mapping()) is False)
        self.assert_(bool(self.reference) is True)

    def test_keys(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.keys()), [])
        d = self.reference
        self.assert_(list(self.inmapping.keys())[0] in d.keys())
        self.assert_(list(self.other.keys())[0] not in d.keys())
        self.assertRaises(TypeError, d.keys, None)

    def test_values(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.values()), [])

        self.assertRaises(TypeError, d.values, None)

    def test_items(self):
        d = self._empty_mapping()
        self.assertEqual(list(d.items()), [])

        self.assertRaises(TypeError, d.items, None)

    def test_len(self):
        d = self._empty_mapping()
        self.assertEqual(len(d), 0)

    def test_getitem(self):
        d = self.reference
        self.assertEqual(d[list(self.inmapping.keys())[0]],
                         list(self.inmapping.values())[0])

        self.assertRaises(TypeError, d.__getitem__)

    def test_update(self):
        # mapping argument
        d = self._empty_mapping()
        d.update(self.other)
        self.assertEqual(list(d.items()), list(self.other.items()))

        # No argument
        d = self._empty_mapping()
        d.update()
        self.assertEqual(d, self._empty_mapping())

        # item sequence
        d = self._empty_mapping()
        d.update(self.other.items())
        self.assertEqual(list(d.items()), list(self.other.items()))

        # Iterator
        d = self._empty_mapping()
        d.update(self.other.items())
        self.assertEqual(list(d.items()), list(self.other.items()))

        # FIXME: Doesn't work with UserDict
        # self.assertRaises((TypeError, AttributeError), d.update, None)
        self.assertRaises((TypeError, AttributeError), d.update, 42)

        outerself = self
        class SimpleUserDict:
            def __init__(self):
                self.d = outerself.reference
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        i1 = sorted(d.items())
        i2 = sorted(self.reference.items())
        self.assertEqual(i1, i2)

        class Exc(Exception): pass

        d = self._empty_mapping()
        class FailingUserDict:
            def keys(self):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        d.clear()

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = 1
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.i:
                            self.i = 0
                            return 'a'
                        raise Exc
                    next = __next__
                return BogonIter()
            def __getitem__(self, key):
                return key
        self.assertRaises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = ord('a')
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.i <= ord('z'):
                            rtn = chr(self.i)
                            self.i += 1
                            return rtn
                        else: # pragma: no cover
                            raise StopIteration
                    next = __next__
                return BogonIter()
            def __getitem__(self, key):
                raise Exc
        self.assertRaises(Exc, d.update, FailingUserDict())

        d = self._empty_mapping()
        class badseq(object):
            def __iter__(self):
                return self
            def __next__(self):
                raise Exc()
            next = __next__

        self.assertRaises(Exc, d.update, badseq())

        self.assertRaises(ValueError, d.update, [(1, 2, 3)])

    # no test_fromkeys or test_copy as both os.environ and selves don't support it

    def test_get(self):
        d = self._empty_mapping()
        self.assert_(d.get(list(self.other.keys())[0]) is None)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        d = self.reference
        self.assert_(d.get(list(self.other.keys())[0]) is None)
        self.assertEqual(d.get(list(self.other.keys())[0], 3), 3)
        self.assertEqual(d.get(list(self.inmapping.keys())[0]),
                         list(self.inmapping.values())[0])
        self.assertEqual(d.get(list(self.inmapping.keys())[0], 3),
                         list(self.inmapping.values())[0])
        self.assertRaises(TypeError, d.get)
        self.assertRaises(TypeError, d.get, None, None, None)

    def test_setdefault(self):
        d = self._empty_mapping()
        self.assertRaises(TypeError, d.setdefault)

    def test_popitem(self):
        d = self._empty_mapping()
        self.assertRaises(KeyError, d.popitem)
        self.assertRaises(TypeError, d.popitem, 42)

    def test_pop(self):
        d = self._empty_mapping()
        k, v = list(self.inmapping.items())[0]
        d[k] = v
        self.assertRaises(KeyError, d.pop, list(self.other.keys())[0])

        self.assertEqual(d.pop(k), v)
        self.assertEqual(len(d), 0)

        self.assertRaises(KeyError, d.pop, k)


class TestMappingProtocol(BasicTestMappingProtocol):
    def test_constructor(self):
        BasicTestMappingProtocol.test_constructor(self)
        self.assert_(self._empty_mapping() is not self._empty_mapping())
        self.assertEqual(self.type2test(x=1, y=2), self._full_mapping({"x": 1, "y": 2}))

    def test_bool(self):
        BasicTestMappingProtocol.test_bool(self)
        self.assert_(not self._empty_mapping())
        self.assert_(self._full_mapping({"x": "y"}))
        self.assert_(bool(self._empty_mapping()) is False)
        self.assert_(bool(self._full_mapping({"x": "y"})) is True)

    def test_keys(self):
        BasicTestMappingProtocol.test_keys(self)
        d = self._empty_mapping()
        self.assertEqual(list(d.keys()), [])
        d = self._full_mapping({'a': 1, 'b': 2})
        k = d.keys()
        self.assert_('a' in k)
        self.assert_('b' in k)
        self.assert_('c' not in k)

    def test_values(self):
        BasicTestMappingProtocol.test_values(self)
        d = self._full_mapping({1:2})
        self.assertEqual(list(d.values()), [2])

    def test_items(self):
        BasicTestMappingProtocol.test_items(self)

        d = self._full_mapping({1:2})
        self.assertEqual(list(d.items()), [(1, 2)])

    def test_contains(self):
        d = self._empty_mapping()
        self.assert_(not ('a' in d))
        self.assert_('a' not in d)
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assert_('a' in d)
        self.assert_('b' in d)
        self.assert_('c' not in d)

        self.assertRaises(TypeError, d.__contains__)

    def test_len(self):
        BasicTestMappingProtocol.test_len(self)
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assertEqual(len(d), 2)

    def test_getitem(self):
        BasicTestMappingProtocol.test_getitem(self)
        d = self._full_mapping({'a': 1, 'b': 2})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        d['c'] = 3
        d['a'] = 4
        self.assertEqual(d['c'], 3)
        self.assertEqual(d['a'], 4)
        del d['b']
        self.assertEqual(d, self._full_mapping({'a': 4, 'c': 3}))

        self.assertRaises(TypeError, d.__getitem__)

    def test_clear(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        d.clear()
        self.assertEqual(d, self._full_mapping({}))

        self.assertRaises(TypeError, d.clear, None)

    def test_update(self):
        BasicTestMappingProtocol.test_update(self)
        # mapping argument
        d = self._empty_mapping()
        d.update({1:100})
        d.update({2:20})
        d.update({1:1, 2:2, 3:3})
        self.assertEqual(d, self._full_mapping({1:1, 2:2, 3:3}))

        # no argument
        d.update()
        self.assertEqual(d, self._full_mapping({1:1, 2:2, 3:3}))

        # keyword arguments
        d = self._empty_mapping()
        d.update(x=100)
        d.update(y=20)
        d.update(x=1, y=2, z=3)
        self.assertEqual(d, self._full_mapping({"x":1, "y":2, "z":3}))

        # item sequence
        d = self._empty_mapping()
        d.update([("x", 100), ("y", 20)])
        self.assertEqual(d, self._full_mapping({"x":100, "y":20}))

        # Both item sequence and keyword arguments
        d = self._empty_mapping()
        d.update([("x", 100), ("y", 20)], x=1, y=2)
        self.assertEqual(d, self._full_mapping({"x":1, "y":2}))

        # iterator
        d = self._full_mapping({1:3, 2:4})
        d.update(self._full_mapping({1:2, 3:4, 5:6}).items())
        self.assertEqual(d, self._full_mapping({1:2, 2:4, 3:4, 5:6}))

        class SimpleUserDict:
            def __init__(self):
                self.d = {1:1, 2:2, 3:3}
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        self.assertEqual(d, self._full_mapping({1:1, 2:2, 3:3}))

    def test_fromkeys(self):
        self.assertEqual(self.type2test.fromkeys('abc'), self._full_mapping({'a':None, 'b':None, 'c':None}))
        d = self._empty_mapping()
        self.assert_(not(d.fromkeys('abc') is d))
        self.assertEqual(d.fromkeys('abc'), self._full_mapping({'a':None, 'b':None, 'c':None}))
        self.assertEqual(d.fromkeys((4,5),0), self._full_mapping({4:0, 5:0}))
        self.assertEqual(d.fromkeys([]), self._full_mapping({}))
        def g():
            yield 1
        self.assertEqual(d.fromkeys(g()), self._full_mapping({1:None}))
        self.assertRaises(TypeError, {}.fromkeys, 3)
        class dictlike(self.type2test): pass
        self.assertEqual(dictlike.fromkeys('a'), self._full_mapping({'a':None}))
        self.assertEqual(dictlike().fromkeys('a'), self._full_mapping({'a':None}))
        self.assert_(dictlike.fromkeys('a').__class__ is dictlike)
        self.assert_(dictlike().fromkeys('a').__class__ is dictlike)
        # FIXME: the following won't work with UserDict, because it's an old style class
        # self.assert_(type(dictlike.fromkeys('a')) is dictlike)
        class mydict(self.type2test):
            def __new__(cls):
                return UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        # FIXME: the following won't work with UserDict, because it's an old style class
        # self.assert_(isinstance(ud, collections.UserDict))
        self.assertRaises(TypeError, dict.fromkeys)

        class Exc(Exception): pass

        class baddict1(self.type2test):
            def __init__(self):
                raise Exc()

        self.assertRaises(Exc, baddict1.fromkeys, [1])

        class BadSeq(object):
            def __iter__(self):
                return self
            def __next__(self):
                raise Exc()
            next = __next__

        self.assertRaises(Exc, self.type2test.fromkeys, BadSeq())

        class baddict2(self.type2test):
            def __setitem__(self, key, value):
                raise Exc()

        self.assertRaises(Exc, baddict2.fromkeys, [1])

    def test_copy(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        self.assertEqual(d.copy(), self._full_mapping({1:1, 2:2, 3:3}))
        d = self._empty_mapping()
        self.assertEqual(d.copy(), d)
        self.assert_(isinstance(d.copy(), d.__class__))
        self.assertRaises(TypeError, d.copy, None)

    def test_get(self):
        BasicTestMappingProtocol.test_get(self)
        d = self._empty_mapping()
        self.assert_(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        d = self._full_mapping({'a' : 1, 'b' : 2})
        self.assert_(d.get('c') is None)
        self.assertEqual(d.get('c', 3), 3)
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)

    def test_setdefault(self):
        BasicTestMappingProtocol.test_setdefault(self)
        d = self._empty_mapping()
        self.assert_(d.setdefault('key0') is None)
        d.setdefault('key0', [])
        self.assert_(d.setdefault('key0') is None)
        d.setdefault('key', []).append(3)
        self.assertEqual(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        self.assertEqual(len(d['key']), 2)

    def test_popitem(self):
        BasicTestMappingProtocol.test_popitem(self)
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(12):
                size = 2**log2size
                a = self._empty_mapping()
                b = self._empty_mapping()
                for i in range(size):
                    a[repr(i)] = i
                    if copymode < 0:
                        b[repr(i)] = i
                if copymode > 0:
                    b = a.copy()
                for i in range(size):
                    ka, va = ta = a.popitem()
                    self.assertEqual(va, int(ka))
                    kb, vb = tb = b.popitem()
                    self.assertEqual(vb, int(kb))
                    self.assert_(not(copymode < 0 and ta != tb))
                self.assert_(not a)
                self.assert_(not b)

    def test_pop(self):
        BasicTestMappingProtocol.test_pop(self)

        # Tests for pop with specified key
        d = self._empty_mapping()
        k, v = 'abc', 'def'

        # verify longs/ints get same value when key > 32 bits (for 64-bit archs)
        # see SF bug #689659
        x = 4503599627370496
        y = 4503599627370496
        h = self._full_mapping({x: 'anything', y: 'something else'})
        self.assertEqual(h[x], h[y])

        self.assertEqual(d.pop(k, v), v)
        d[k] = v
        self.assertEqual(d.pop(k, 1), v)


class TestHashMappingProtocol(TestMappingProtocol):

    def test_getitem(self):
        TestMappingProtocol.test_getitem(self)
        class Exc(Exception): pass

        class BadEq(object):
            def __eq__(self, other): # pragma: no cover
                raise Exc()
            def __hash__(self):
                return 24

        d = self._empty_mapping()
        d[BadEq()] = 42
        self.assertRaises(KeyError, d.__getitem__, 23)

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.__getitem__, x)

    def test_fromkeys(self):
        TestMappingProtocol.test_fromkeys(self)
        class mydict(self.type2test):
            def __new__(cls):
                return UserDict()
        ud = mydict.fromkeys('ab')
        self.assertEqual(ud, {'a':None, 'b':None})
        self.assert_(isinstance(ud, UserDict))

    def test_pop(self):
        TestMappingProtocol.test_pop(self)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.pop, x)

    def test_mutatingiteration(self): # pragma: no cover
        d = self._empty_mapping()
        d[1] = 1
        try:
            for i in d:
                d[i+1] = 1
        except RuntimeError:
            pass
        else:
            self.fail("changing dict size during iteration doesn't raise Error")

    def test_repr(self): # pragma: no cover
        d = self._empty_mapping()
        self.assertEqual(repr(d), '{}')
        d[1] = 2
        self.assertEqual(repr(d), '{1: 2}')
        d = self._empty_mapping()
        d[1] = d
        self.assertEqual(repr(d), '{1: {...}}')

        class Exc(Exception): pass

        class BadRepr(object):
            def __repr__(self):
                raise Exc()

        d = self._full_mapping({1: BadRepr()})
        self.assertRaises(Exc, repr, d)

    def test_eq(self):
        self.assertEqual(self._empty_mapping(), self._empty_mapping())
        self.assertEqual(self._full_mapping({1: 2}),
                         self._full_mapping({1: 2}))

        class Exc(Exception): pass

        class BadCmp(object):
            def __eq__(self, other):
                raise Exc()
            def __hash__(self):
                return 1

        d1 = self._full_mapping({BadCmp(): 1})
        d2 = self._full_mapping({1: 1})
        self.assertRaises(Exc, lambda: BadCmp()==1)
        #self.assertRaises(Exc, lambda: d1==d2)

    def test_setdefault(self):
        TestMappingProtocol.test_setdefault(self)

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        self.assertRaises(Exc, d.setdefault, x, [])
