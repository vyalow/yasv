import sys


__all__ = ['string_types', 'iteritems', 'itervalues', 'izip']


if sys.version_info[0] >= 3:
    string_types = str,
    iteritems = lambda o: o.items()
    itervalues = lambda o: o.values()
    izip = zip

else:
    string_types = str, unicode
    iteritems = lambda o: o.iteritems()
    itervalues = lambda o: o.itervalues()
    from itertools import izip


def with_metaclass(meta, base=object):
    return meta("NewBase", (base,), {})
