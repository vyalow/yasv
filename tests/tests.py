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
        self.assertEqual(s['bar'].errors,
                         ['Value not in presets: (1, 2).'])
        self.assertEqual(s.get_errors(),
                         {'bar': ['Value not in presets: (1, 2).']})

        class PriceValidator(Validator):

            def on_value(self):
                if self.value > 10:
                    self.fields['type'].cleaned_data = 'volleyball'
                else:
                    self.fields['type'].cleaned_data = 'football'
                return True

        class BallSchema(Schema):
            price = Field(PriceValidator())
            type = Field()

        b = BallSchema({'price': 1, 'type': 'basketball'})
        self.assertEqual(b.is_valid(), True)
        self.assertEqual(b['type'].cleaned_data, 'football')
        self.assertEqual(b['type'].raw_data, 'basketball')

    def test_templates(self):
        required = Required('Is required.')

        class TestSchema(Schema):
            foo = Field('Foo', required)

        s = TestSchema({})
        s.is_valid()
        self.assertEqual(s.get_errors(), {'foo': ['Is required.']})

        class TestSchema(Schema):
            foo = Field('Foo', Required())

        s = TestSchema({})
        s.is_valid()
        self.assertEqual(s.get_errors(), {'foo': ['Value is required.']})

    def test_is_url(self):
        class TestSchema(Schema):
            url = Field('URL', IsURL())

        s = TestSchema({'url': 'http://example.com'})
        self.assertEqual(s.is_valid(), True)

        s = TestSchema({'url': 3})
        self.assertEqual(s.is_valid(), False)

        s = TestSchema({'url': None})
        self.assertEqual(s.is_valid(), False)

        s = TestSchema({'url': 'www.example.com'})
        self.assertEqual(s.is_valid(), False)

    def test_required(self):
        class TestSchema(Schema):
            foo = Field('Foo', Required())

        s = TestSchema({})
        self.assertEqual(s.is_valid(), False)

    def test_length(self):
        class TestSchema(Schema):
            foo = Field('Foo', length(min=2, max=4))

        s = TestSchema({'foo': '12'})
        self.assertEqual(s.is_valid(), True)

        s = TestSchema({'foo': ' '})
        self.assertEqual(s.is_valid(), False)

        s = TestSchema({'foo': '12345'})
        self.assertEqual(s.is_valid(), False)

        s = TestSchema({'foo': None})
        self.assertEqual(s.is_valid(), False)

        s = TestSchema({'foo': 1})
        self.assertEqual(s.is_valid(), False)

    def test_in_range(self):
        class TestSchema(Schema):
            foo = Field('Foo', in_range(min=2, max=4))

        s = TestSchema({'foo': 3})
        self.assertEqual(s.is_valid(), True)

        s = TestSchema({'foo': 12345})
        self.assertEqual(s.is_valid(), False)

    def test_is_in(self):
        class TestSchema(Schema):
            foo = Field('Foo', is_in([1, '!']))

        s = TestSchema({'foo': ''})
        self.assertEqual(s.is_valid(), False)

        s = TestSchema({'foo': 1})
        self.assertEqual(s.is_valid(), True)

    def test_not_in(self):
        class TestSchema(Schema):
            foo = Field('Foo', not_in([1, '!']))

        s = TestSchema({'foo': ''})
        self.assertEqual(s.is_valid(), True)

        s = TestSchema({'foo': 1})
        self.assertEqual(s.is_valid(), False)

    def test_process_template(self):
        def process_template(self, field):
            template = self._template if self._template else self.default_template
            template = 'Error with "%s". %s' % (field.label, template)
            return template.format(*self.template_params())
        required = Required(process_template)

        class TestSchema(Schema):
            foo = Field('Foo', required)

        s = TestSchema({})
        s.is_valid()
        self.assertEqual(s.get_errors(),
                         {'foo': ['Error with "Foo". Value is required.']})

if __name__ == '__main__':
    unittest.main()
