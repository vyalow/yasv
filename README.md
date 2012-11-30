yasv
=========

Yet Another Simple Validator

### Example

```python
from yasv.core import Schema, Field
from yasv.validators import is_in, required


class TestSchema(Schema):
    foo = Field('Foo', required)
    bar = Field('Bar', is_in([1, 2]))
```

Valid data

```
>>> s = TestSchema({'foo': 1, 'bar': 2})
>>> s.is_valid()
True
>>> s.cleaned_data
{'foo': 1, 'bar': 2}
```

Invalid data

```
>>> s = TestSchema({'foo': 1, 'bar': 3})
>>> s.is_valid()
False
>>> s.get_errors()
['Value not in presets: (1, 2).']
```