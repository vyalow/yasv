import abc
import string
from urlparse import urlparse

from yasv.compat import with_metaclass


__all__ = [
    'Required', 'required',
    'IsURL', 'is_url',
    'IsIn', 'is_in',
    'MinLen', 'min_len'
]


class ValidationError(Exception):

    def __init__(self, message=''):
        super(ValidationError, self).__init__(message)
        self.error_response = {}


class NotSpecifiedValue(object):
    pass


class Validator(with_metaclass(abc.ABCMeta)):

    def __init__(self, template=None):
        self._template = template

    def validate(self, value):
        self.value = value
        if not (self.on_missing() and self.on_blank() and self.on_value()):
            template = self._get_template()
            raise ValidationError(template.format(self.template_params()))

        return value

    def template_params(self):
        return ()

    @abc.abstractmethod
    def on_missing(self):
        """"""

    @abc.abstractmethod
    def on_blank(self):
        """"""

    @abc.abstractmethod
    def on_value(self):
        """"""

    @property
    @abc.abstractmethod
    def default_template(self):
        """"""

    def _get_template(self):
        return self._template if self._template else self.default_template


class Optional(Validator):

    def on_missing(self):
        return True

    def on_blank(self):
        return True

    def on_value(self):
        return True


class Required(Optional):

    default_template = 'Value is required.'

    def on_missing(self):
        return False if isinstance(self.value, NotSpecifiedValue) else True


class NotBlank(Optional):

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


class IsIn(Optional):

    default_template = 'Value not in presets: ({0}).'

    def on_value(self):
        return self.value in self._presets

    def template_params(self):
        to_str = lambda x: str(x) if not isinstance(x, (unicode, str)) else x
        return ', '.join(map(to_str, self._presets))

    def __call__(self, presets):
        instance = self.__class__(self._template)
        instance._presets = presets
        return instance


class IsURL(Optional):

    default_template = 'Invalid URL.'

    def on_value(self):
        if self.value:
            parts = urlparse(self.value)
            cond1 = all([parts.scheme, parts.netloc])
            cond2 = set(parts.netloc) - set(string.letters + string.digits + '-.')
            cond3 = parts.scheme in ['http', 'https']
            return cond1 and not cond2 and cond3


class MinLen(NotBlank):

    default_template = 'Shorter than min len: "{0}."'

    def template_params(self):
        return str(self._min_len)

    def on_value(self):
        try:
            return len(self.value) >= self._min_len
        except TypeError:
            return True

    def __call__(self, min_len):
        instance = self.__class__(self._template)
        instance._min_len = min_len
        return instance


required = Required()
not_blank = NotBlank()
not_empty = NotEmpty()
is_in = IsIn()
is_url = IsURL()
min_len = MinLen()
