import re
import sys
import abc
import types

from yasv.compat import with_metaclass


__all__ = [
    'required', 'Required',
    'not_blank', 'NotBlank',
    'not_empty', 'NotEmpty',
    'is_url', 'IsURL',
    'is_in', 'IsIn',
    'not_in', 'NotIn',
    'length', 'Length',
]


class ValidationError(Exception):

    def __init__(self, message=''):
        super(ValidationError, self).__init__(message)
        self.error_response = {}


class NotSpecifiedValue(object):
    pass


class Validator(with_metaclass(abc.ABCMeta)):

    def __init__(self, *args, **kwargs):
        self._template = None
        for arg in args:
            if isinstance(arg, types.FunctionType):
                setattr(self, arg.__name__, types.MethodType(arg, self))

            elif isinstance(arg, (str, unicode)):
                self._template = arg

    def validate(self, value, field):
        self.value = value
        if not (self.specified_type() and self.on_missing() and self.on_blank()
            and self.on_value()):
            raise ValidationError(self.process_template(field))

        return self.value

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
    @abc.abstractmethod
    def default_template(self):
        """"""

    def process_template(self, field):
        template = self._template if self._template else self.default_template
        return template.format(*self.template_params())


class Required(Validator):

    default_template = 'Value is required.'

    def on_missing(self):
        return False if isinstance(self.value, NotSpecifiedValue) else True


class NotBlank(Validator):

    default_template = "Value couldn't be blank."

    def on_blank(self):
        if hasattr(self.value, 'strip'):
            self.value = self.value.strip()

        if self.value in ('', [], {}, None, set()):
            return False
        else:
            return True


class NotEmpty(Required, NotBlank):

    default_template = "Value couldn't be empty."


class String(Validator):

    def specified_type(self):
        if isinstance(self.value, (str, unicode)):
            return True
        else:
            return False


class HasLength(Validator):

    def specified_type(self):
        return True if hasattr(self.value, '__len__') else False


class PresetsBase(Validator):
    """ Base class for `IsIn` and `NotIn` validators.
    """
    def template_params(self):
        to_str = lambda x: str(x) if not isinstance(x, (unicode, str)) else x
        return ', '.join(map(to_str, self._presets)),

    def __call__(self, presets):
        instance = self.__class__(self._template)
        instance._presets = presets
        return instance


class IsIn(PresetsBase):

    default_template = 'Value not in presets: ({0}).'

    def on_value(self):
        return self.value in self._presets


class NotIn(PresetsBase):

    default_template = 'Value have not to be in presets: ({0}).'

    def on_value(self):
        return self.value not in self._presets


class RegexpValidator(String, with_metaclass(abc.ABCMeta)):

    def __init__(self, *args, **kwargs):
        super(RegexpValidator, self).__init__(args, kwargs)
        self._args = args
        self._kwargs = kwargs

        self.regex = re.compile(self.get_regexp_str(), re.IGNORECASE)

    @abc.abstractmethod
    def get_regexp_str(self):
        """"""

    def on_value(self):
        return True if self.regex.match(self.value) else False

    def __deepcopy__(self, memo):
        return self.__class__(*self._args, **self._kwargs)


class IsURL(RegexpValidator):

    default_template = 'Invalid URL.'

    def get_regexp_str(self):
        require_tld = self._kwargs.get('require_tld', True)
        tld_part = (require_tld and ur'\.[a-z]{2,10}' or u'')
        return (ur'^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})'
            ur'(:[0-9]+)?(\/.*)?$' % tld_part)


class Length(HasLength):

    default_template = 'Length must be between {0} and {1}.'

    def template_params(self):
        return str(self._min), str(self._max)

    def on_value(self):
        return self._max >= len(self.value) >= self._min

    def __call__(self, min=-1, max=sys.maxint):
        assert min == -1 or max == sys.maxint, ('`min` and `max` parameters '
            'must be specified.')
        assert min <= max, '`min` cannot be more than `max`.'
        instance = self.__class__(self._template)
        instance._min = min
        instance._max = max
        return instance


required = Required()
not_blank = NotBlank()
not_empty = NotEmpty()
is_in = IsIn()
not_in = NotIn()
is_url = IsURL()
length = Length()
