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

Field access

```
>>> s.fields['bar'].label
'Bar'
>>> s.fields['bar'].data
3
>>> s.fields['bar'].errors
['Value not in presets: (1, 2).']
```

Custom error message

```python
from yasv.core import Schema, Field
from yasv.validators import IsIn


is_in = IsIn('Value not in [{0}]')


class TestSchema(Schema):
    foo = Field('Foo', is_in([1, 2]))
```

```
>>> s = TestSchema({'foo': 3})
>>> s.is_valid()
False
>>> s.get_errors()
['Value not in [1, 2]']
```
