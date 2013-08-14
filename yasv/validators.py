import re
import sys
import abc

from six import with_metaclass, string_types, iteritems

from yasv.errors import ValidationError


class Validator(object):
    """ Base abstract class for any validators.
    """
    templates = {}

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._message = ''

    def on_missing(self):
        return True

    def on_value(self):
        return True

    def specified_type(self):
        return True

    def apply_rules(self):
        return self.specified_type() and self.on_missing() and self.on_value()

    def validate(self, field, fields):
        self.value = field.cleaned_data
        self.fields = fields
        self.field = field
        if not self.apply_rules():
            raise ValidationError(self._message)

        field._cleaned_data = self.value

    def context(self, *args, **kwargs):
        instance = self.__class__(*self._args, **self._kwargs)
        for name, arg in iteritems(kwargs):
            setattr(instance, name, arg)
        return instance

    def message(self, key, *args):
        self._message = self.templates.get(key, '').format(*args)


class Required(Validator):
    """ Validates that the field contains data.
    """
    templates = {'required': 'Value is required.'}

    def on_missing(self):
        if bool(self.value):
            return True
        else:
            self.message('required')
            return False



class String(Validator):
    """ Base class for validators. Check that the data is instance of
    str or unicode.
    """
    templates = {
        'wrong type': u'Illegal type. String expected: <{0}>.',
    }

    def specified_type(self):
        if isinstance(self.value, string_types):
            return True
        else:
            self.message('wrong_type', type(self.value).__name__)
            return False


class HasLength(Validator):
    """ Base class for validators. Check that the data has __len__ method.
    """
    def specified_type(self):
        return True if hasattr(self.value, '__len__') else False


class IsIn(Validator):
    """ Validates that the data is in presets.
    """
    templates = {'default': 'Value have to be in: ({0}).'}

    def on_value(self):
        if self.value in self.presets:
            return True
        else:
            self.message('default', self.presets)
            return False

    def __call__(self, presets):
        return self.context(presets=presets)


class NotIn(Validator):
    """ Validates that the data is not in presets.
    """
    templates = {'default': "Value don't have to be in: ({0})."}

    def on_value(self):
        if self.value not in self.presets:
            return True
        else:
            self.message('default', self.presets)
            return False

    def __call__(self, presets):
        return self.context(presets=presets)


class RegexpValidator(String, with_metaclass(abc.ABCMeta)):
    """ Base class for regexp validators.
    """
    def __init__(self, *args, **kwargs):
        super(RegexpValidator, self).__init__(*args, **kwargs)
        self.regex = re.compile(self.get_regexp_str(), re.IGNORECASE)

    @abc.abstractmethod
    def get_regexp_str(self):
        pass

    def on_value(self):
        if not self.value or self.regex.match(self.value):
            return True
        else:
            self.message('default')
            return False


class IsURL(RegexpValidator):
    """ Validates that the data is a valid URL.
    """
    templates = {'default': 'Invalid URL.'}

    def get_regexp_str(self):
        require_tld = self._kwargs.get('require_tld', True)
        tld_part = (require_tld and r'\.[a-z]{2,10}' or '')
        return (r'^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})'
                r'(:[0-9]+)?(\/.*)?$' % tld_part)


class Length(HasLength):
    """ Validates that the length of data more than min length and
    less than max.
    """
    templates = {
        'max': 'Length must be less than {0}.',
        'min': 'Length must be more than {0}.',
        'both': 'Length must be between {0} and {1}.',
    }

    def on_value(self):
        if self.max and self.min:
            if self.max >= len(self.value) >= self.min:
                return True
            else:
                self.message('both', self.min, self.max)
                return False
        elif self.max:
            if self.max >= len(self.value):
                return True
            else:
                self.message('max', self.max)
                return False
        else:
            if len(self.value) >= self.min:
                return True
            else:
                self.message('min', self.min)
                return False

    def __call__(self, min=-1, max=sys.maxsize):
        assert min <= max, '`min` cannot be more than `max`.'
        return self.context(min=min, max=max)


class InRange(Validator):
    """Validates that data more than min and less than max"""
    templates = {
        'max': 'Value must be less than {0}.',
        'min': 'Value must be more than {0}.',
        'both': 'Value must be between {0} and {1}.',
    }

    def on_value(self):
        if self.max and self.min:
            if self.max >= self.value >= self.min:
                return True
            else:
                self.message('both', self.min, self.max)
                return False
        elif self.max:
            if self.max >= self.value:
                return True
            else:
                self.message('max', self.max)
                return False
        else:
            if self.value >= self.min:
                return True
            else:
                self.message('min', self.min)
                return False

    def __call__(self, min=None, max=None):
        assert min <= max, '`min` cannot be more than `max`.'
        return self.context(min=min, max=max)


required = Required()
is_in = IsIn()
not_in = NotIn()
is_url = IsURL()
length = Length()
in_range = InRange()
