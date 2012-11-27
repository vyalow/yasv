import string
from urlparse import urlparse


__all__ = ['ValidationError', 'Validator', 'Required', 'IsURL', 'IsIn',
           'MinLen']


class ValidationError(Exception):

    def __init__(self, message=''):
        super(ValidationError, self).__init__(message)
        self.error_response = {}


class Validator(object):

    def __init__(self, template=None):
        self._template = template

    def validate(self, value, data):
        if not self.valid_condition(value):
            if self._template:
                raise ValidationError(
                    self._template.format(self.template_params()))
            else:
                raise ValidationError(
                    self.default_template.format(self.template_params()))

        return value

    def template_params(self):
        return ()


class Required(Validator):

    default_template = 'Empty value.'

    def valid_condition(self, value):
        if hasattr(value, 'strip'):
            return value.strip()
        else:
            return value


class IsIn(Validator):

    default_template = 'Value not in presets: ({0}).'

    def valid_condition(self, value):
        return value in self._presets

    def template_params(self):
        to_str = lambda x: str(x) if not isinstance(x, (unicode, str)) else x
        return ', '.join(map(to_str, self._presets))

    def __call__(self, presets):
        instance = self.__class__(self._template)
        instance._presets = presets
        return instance


class IsURL(Validator):

    default_template = 'Invalid URL.'

    def valid_condition(self, value):
        if value:
            parts = urlparse(value)
            cond1 = all([parts.scheme, parts.netloc])
            cond2 = set(parts.netloc) - set(string.letters + string.digits + '-.')
            cond3 = parts.scheme in ['http', 'https']
            return cond1 and not cond2 and cond3
        else:
            # here is True because field could be optional
            return True


class MinLen(Validator):

    default_template = 'Shorter than min len: "{0}."'

    def template_params(self):
        return str(self._min_len)

    def valid_condition(self, value):
        try:
            return len(value) >= self._min_len
        except TypeError:
            return True

    def __call__(self, min_len):
        instance = self.__class__(self._template)
        instance._min_len = min_len
        return instance
