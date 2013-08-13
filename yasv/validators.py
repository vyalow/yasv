import re
import sys
import abc

from six import with_metaclass, string_types, iteritems

from yasv.errors import ValidationError


__all__ = [
    'Validator',
    'required', 'Required',
    'is_url', 'IsURL',
    'is_in', 'IsIn',
    'not_in', 'NotIn',
    'length', 'Length',
    'in_range', 'InRange',
]


class Validator(object):
    """ Base abstract class for any validators.
    """
    def __init__(self, *args, **kwargs):
        self._template = None
        self._args = args
        self._kwargs = kwargs

        for arg in args:
            if isinstance(arg, string_types):
                self._template = arg

        if self._template:
            self.template = self._template
        else:
            self.template = self.default_template

    def apply_rules(self):
        return (self.specified_type() and self.on_missing() and self.on_blank()
                and self.on_value())

    def validate(self, field, fields):
        self.value = field.cleaned_data
        self.fields = fields
        if not self.apply_rules():
            raise ValidationError(self.process_template(field))

        field._cleaned_data = self.value

    def template_params(self):
        return ()

    def on_missing(self):
        return True

    def on_blank(self):
        return True

    def on_value(self):
        return True

    def specified_type(self):
        return True

    @property
    def default_template(self):
        return ''

    def get_template(self, field):
        return self.template

    def process_template(self, field):
        return self.get_template(field).format(*self.template_params())

    def context(self, *args, **kwargs):
        instance = self.__class__(*self._args, **self._kwargs)
        for name, arg in iteritems(kwargs):
            setattr(instance, name, arg)
        return instance


class Required(Validator):
    """ Validates that the field contains data.
    """
    default_template = 'Value is required.'

    def on_missing(self):
        return bool(self.value)


class String(Validator):
    """ Base class for validators. Check that the data is instance of
    str or unicode.
    """
    def specified_type(self):
        if isinstance(self.value, string_types):
            return True
        else:
            return False


class HasLength(Validator):
    """ Base class for validators. Check that the data has __len__ method.
    """
    def specified_type(self):
        return True if hasattr(self.value, '__len__') else False


class PresetsBase(Validator):
    """ Base class for `IsIn` and `NotIn` validators.
    """
    def template_params(self):
        to_str = lambda x: str(x) if not isinstance(x, string_types) else x
        return ', '.join(map(to_str, self.presets)),

    def __call__(self, presets):
        return self.context(presets=presets)


class IsIn(PresetsBase):
    """ Validates that the data is in presets.
    """
    default_template = 'Value not in presets: ({0}).'

    def on_value(self):
        return self.value in self.presets


class NotIn(PresetsBase):
    """ Validates that the data is not in presets.
    """
    default_template = 'Value have not to be in presets: ({0}).'

    def on_value(self):
        return self.value not in self.presets


class RegexpValidator(String, with_metaclass(abc.ABCMeta)):
    """ Base class for regexp validators.
    """
    def __init__(self, *args, **kwargs):
        super(RegexpValidator, self).__init__(*args, **kwargs)
        self.regex = re.compile(self.get_regexp_str(), re.IGNORECASE)

    @abc.abstractmethod
    def get_regexp_str(self):
        """"""

    def on_value(self):
        return True if not self.value or self.regex.match(self.value) else False


class IsURL(RegexpValidator):
    """ Validates that the data is a valid URL.
    """
    default_template = 'Invalid URL.'

    def get_regexp_str(self):
        require_tld = self._kwargs.get('require_tld', True)
        tld_part = (require_tld and r'\.[a-z]{2,10}' or '')
        return (r'^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})'
                r'(:[0-9]+)?(\/.*)?$' % tld_part)


class Length(HasLength):
    """ Validates that the length of data more than min length and
    less than max.
    """
    default_template = 'Length must be between {0} and {1}.'

    def template_params(self):
        return str(self.min), str(self.max)

    def on_value(self):
        return self.max >= len(self.value) >= self.min

    def __call__(self, min=-1, max=sys.maxsize):
        assert min != -1 and max != sys.maxsize,\
            ('`min` and `max` parameters must be specified.')
        assert min <= max, '`min` cannot be more than `max`.'
        return self.context(min=min, max=max)


class InRange(Validator):
    """Validates that data more than min and less than max"""
    default_template = "Value must be between {0} and {1}."

    def template_params(self):
        return str(self.min), str(self.max)

    def on_value(self):
        return self.max >= self.value >= self.min

    def __call__(self, min=None, max=None):
        assert min is not None and max is not None,\
            ('`min` and `max` parameters must be specified.')
        assert min <= max, '`min` cannot be more than `max`.'
        return self.context(min=min, max=max)


required = Required()
is_in = IsIn()
not_in = NotIn()
is_url = IsURL()
length = Length()
in_range = InRange()
