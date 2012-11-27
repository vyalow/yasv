import string
from urlparse import urlparse


__all__ = ['ValidationError', 'Validator', 'Required', 'IsURL', 'IsIn']


class ValidationError(Exception):

    def __init__(self, message=''):
        super(ValidationError, self).__init__(message)
        self.error_response = {}


class Validator(object):

    def __init__(self, template=None):
        self._template = template

    def validate(self, value):
        if not self.valid_condition(value):
            if self._template:
                raise ValidationError(
                    self._template.format(self.template_params()))
            else:
                raise ValidationError(
                    self.default_template.format(self.template_params()))

        return value


class Required(Validator):

    default_template = 'Empty value.'

    def valid_condition(self, value):
        if isinstance(value, (unicode, str)):
            return value.strip()
        else:
            return value

    def template_params(self):
        return ()


class IsIn(Validator):

    default_template = 'Value not in presets: "{0}".'

    def valid_condition(self, value):
        return value in self._presets

    def template_params(self):
        return (self._presets,)

    def __call__(self, presets):
        self._presets = presets
        return self


class IsURL(Validator):

    default_template = 'Invalid URL.'

    def valid_condition(self, value):
        parts = urlparse(value)
        cond1 = all([parts.scheme, parts.netloc])
        cond2 = set(parts.netloc) - set(string.letters + string.digits + '-.')
        cond3 = parts.scheme in ['http', 'https']
        return cond1 and not cond2 and cond3

    def template_params(self):
        return ()
