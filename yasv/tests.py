import unittest

from yasv import *


class TestSchema(unittest.TestCase):

    def test_schema(self):
        is_in = IsIn()
        required = Required()
        s = Schema({
            'foo': Field('Foo', required),
            'bar': Field('Bar', is_in([1, 2])),
        })
        d = s.validate({
            'foo': 1,
            'bar': 2
        })
        self.assertEqual(d, {'foo': 1, 'bar': 2})

        try:
            s.validate({
                'foo': 1,
                'bar': 3
            })
        except ValidationError, e:
            response = {
                'foo': {
                    'errors': [],
                    'value': 1,
                    'label': 'Foo'
                },
                'bar': {
                    'errors': ['Value not in presets: (1, 2).'],
                    'value': 3,
                    'label': 'Bar',
                },
            }
            self.assertEqual(e.error_response, response)
        else:
            self.fail('Exception was not raised for invalid data')

    def test_is_url(self):
        s = Schema({'url': Field('URL', IsURL())})

        valid_data = {'url': 'http://example.com'}
        d = s.validate(valid_data)
        self.assertEqual(d, valid_data)

        valid_data = {'url': None}
        d = s.validate(valid_data)
        self.assertEqual(d, valid_data)

        invalid_data = {'url': 'www.example.com'}
        with self.assertRaises(ValidationError):
            s.validate(invalid_data)

    def test_required(self):
        s = Schema({'foo': Field('Foo', Required())})

        invalid_data = {'foo': ' '}
        with self.assertRaises(ValidationError):
            s.validate(invalid_data)

    def test_min_len(self):
        s = Schema({'foo': Field('Foo', MinLen()(2))})

        valid_data = {'foo': '12'}
        d = s.validate(valid_data)
        self.assertEqual(d, valid_data)

        invalid_data = {'foo': ' '}
        with self.assertRaises(ValidationError):
            s.validate(invalid_data)


if __name__ == '__main__':
    unittest.main()
