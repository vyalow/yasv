from yasv.validators import ValidationError, Validator
from yasv.compat import with_metaclass, iteritems


__all__ = ['Schema', 'Field']


class Field(object):

    def __init__(self, *args):
        self.validators = []
        self.label = None
        self.data = None
        self.errors = []

        for arg in args:
            if isinstance(arg, (str, unicode)):
                self.label = arg
            elif isinstance(arg, Validator):
                self.validators.append(arg)


class SchemaMeta(type):
    """ The metaclass for `Schema` and any subclasses of `Schema`.

    `SchemaMeta`'s responsibility is to create the `_unbound_fields` dict, which
    is a dict of `Field` instances.
    The dict is created at the first instantiation of the schema.
    If any fields are added/removed from the schema, the dict is cleared to be
    re-generated on the next instantiaton.

    Any properties which begin with an underscore or are not `Field`
    instances are ignored by the metaclass.
    """
    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls._unbound_fields = None

    def __call__(cls, *args, **kwargs):
        """ Construct a new `Schema` instance, creating `_unbound_fields` on the
        class if it is empty.
        """
        if cls._unbound_fields is None:
            fields = {}
            for name in dir(cls):
                if not name.startswith('_'):
                    unbound_field = getattr(cls, name)
                    if isinstance(unbound_field, Field):
                        fields.update({name: unbound_field})
            cls._unbound_fields = fields
        return type.__call__(cls, *args, **kwargs)

    def __setattr__(cls, name, value):
        """ Add an attribute to the class, clearing `_unbound_fields` if needed.
        """
        if not name.startswith('_') and isinstance(value, Field):
            cls._unbound_fields = None
        type.__setattr__(cls, name, value)

    def __delattr__(cls, name):
        """ Remove an attribute from the class, clearing `_unbound_fields` if
        needed.
        """
        if not name.startswith('_'):
            cls._unbound_fields = None
        type.__delattr__(cls, name)


class Schema(with_metaclass(SchemaMeta)):

    def __init__(self, data):
        if isinstance(data, dict):
            for name, value in iteritems(data):
                if name in self._unbound_fields:
                    self._unbound_fields[name].data = value
        else:
            for name in dir(data):
                if not name.startswith('_') and not name.startswith('__'):
                    value = getattr(data, name)
                    if name in self._unbound_fields:
                        self._unbound_fields[name].data = value

    def is_valid(self):
        is_valid = True
        for name, field in iteritems(self._unbound_fields):
            for validator in field.validators:
                try:
                    field.data = validator.validate(field.data)
                except ValidationError, e:
                    is_valid = False
                    field.errors.append(e.message)

        return is_valid
