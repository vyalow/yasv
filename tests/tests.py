import unittest
from collections import namedtuple

from yasv import *


class TestSchema(unittest.TestCase):

    def test_schema(self):
        is_in = IsIn()
        required = Required()

        class TestSchema(Schema):
            foo = Field('Foo', required)
            bar = Field('Bar', is_in([1, 2]))

        s = TestSchema({'foo': 1, 'bar': 2})
        self.assertEqual(s.is_valid(), True)

        Data = namedtuple('Data', ['foo', 'bar'])
        s = TestSchema(Data(foo=1, bar=2))
        self.assertEqual(s.is_valid(), True)

        s = TestSchema({'foo': 1, 'bar': 3})
        self.assertEqual(s.is_valid(), False)
        self.assertEqual(s.fields['bar'].errors,
            ['Value not in presets: (1, 2).'])
        self.assertEqual(s.get_errors(),
            ['Value not in presets: (1, 2).'])

    def test_templates(self):
        required = Required('Is required.')

        class TestSchema(Schema):
            foo = Field('Foo', required)

        s = TestSchema({})
        s.is_valid()
        self.assertEqual(s.get_errors(),
            ['Is required.'])

        class TestSchema(Schema):
            foo = Field('Foo', Required())

        s = TestSchema({})
        s.is_valid()
        self.assertEqual(s.get_errors(),
            ['Empty value.'])

    def test_is_url(self):
        class TestSchema(Schema):
            url = Field('URL', IsURL())

        s = TestSchema({'url': 'http://example.com'})
        self.assertEqual(s.is_valid(), True)

        s = TestSchema({'url': None})
        self.assertEqual(s.is_valid(), True)

        s = TestSchema({'url': 'www.example.com'})
        self.assertEqual(s.is_valid(), False)

    def test_required(self):
        class TestSchema(Schema):
            foo = Field('Foo', Required())

        s = TestSchema({'foo': ' '})
        self.assertEqual(s.is_valid(), False)

    def test_min_len(self):
        class TestSchema(Schema):
            foo = Field('Foo', MinLen()(2))

        s = TestSchema({'foo': '12'})
        self.assertEqual(s.is_valid(), True)

        s = TestSchema({'foo': ' '})
        self.assertEqual(s.is_valid(), False)


if __name__ == '__main__':
    unittest.main()
