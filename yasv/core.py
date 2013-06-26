from copy import deepcopy

from six import with_metaclass, iteritems, itervalues, string_types

from yasv.validators import ValidationError, Validator, NotSpecifiedValue


__all__ = ['Schema', 'Field']


class Field(object):

    def __init__(self, *args):
        """ Construct a new `Field` instance.

        Accepts a list of args. If arg is str or unicode - it sets as label.
        If arg is instance of `Validator` - it appends to a validators list.
        """
        self.validators = []
        self.label = None
        self.raw_data = NotSpecifiedValue()
        self.errors = []

        for arg in args:
            if isinstance(arg, string_types):
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
            assert fields, ('`Schema` subclasses have to define at least one '
                'unbound `Field` attribute.')
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
        """ Construct a new `Schema` instance.

        Accepts data as a dict or namedtuple or any object with attributes.
        Creates fields dict with data.
        """
        self._fields = {}
        for name, field in iteritems(self._unbound_fields):
            self._fields[name] = deepcopy(field)

        if isinstance(data, dict):
            for name, value in iteritems(data):
                self._add_data_to_field(name, value)
        else:
            for name in dir(data):
                if not name.startswith('_') and not name.startswith('__'):
                    try:
                        value = getattr(data, name)
                    except AttributeError:
                        pass
                    else:
                        self._add_data_to_field(name, value)

    def __getitem__(self, key):
        return self._fields[key]

    def __setitem__(self, key, value):
        self._fields[key] = value

    def __delitem__(self, key):
        del self._fields[key]

    def __contains__(self, item):
        return item in self._fields

    def __iter__(self):
        return iter(self._fields)

    def values(self):
        for value in itervalues(self._fields):
            yield value

    def items(self):
        for key, value in iteritems(self._fields):
            yield key, value

    def _add_data_to_field(self, name, value):
        if name in self:
            self[name].raw_data = value

    def is_valid(self):
        """ Validate field value.

        Constructs an errors list with error messages.
        Returns validation status.
        """
        is_valid = True
        for field in self.values():
            field.cleaned_data = field.raw_data

        for name, field in self.items():
            for validator in field.validators:
                try:
                    validator.validate(field, self)
                except ValidationError as e:
                    is_valid = False
                    field.errors.append(e.message)

        return is_valid

    def get_errors(self):
        """ Return a list of error messages.
        """
        return {name: field.errors for name, field in self.items()
                if field.errors}
