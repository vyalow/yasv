from six import with_metaclass, iteritems, itervalues, string_types

from yasv.validators import Validator
from yasv.errors import InvalidCleanedDataError, ValidationError


class Field(object):

    def __init__(self, *args, **kwargs):
        """ Construct a new `Field` instance.

        Accepts a list of args. If arg is str or unicode - it sets as label.
        If arg is instance of `Validator` - it appends to a validators list.
        """
        self._args = args
        self._kwargs = kwargs
        self.validators = []
        self._label = None
        self.raw_data = None
        self._cleaned_data = None
        self.errors = []
        self._is_valid = True
        self._is_validated = False
        self.name = ''

        for arg in args:
            if isinstance(arg, string_types):
                self._label = arg
            elif isinstance(arg, Validator):
                self.validators.append(arg)

    def __repr__(self):
        return '<yasv.core.Field object {0}>'.format(self.name)

    @property
    def cleaned_data(self):
        if not self._is_validated:
            self.validate()
        if self.is_valid:
            return self._cleaned_data
        else:
            raise InvalidCleanedDataError("Field is invalid. It doesn't have "
                                          "cleaned data", self.name, self.label)

    @cleaned_data.setter
    def cleaned_data(self, value):
        self._cleaned_data = value
        self._is_validated = True

    @property
    def label(self):
        return self._label if self._label else self.name

    @label.setter
    def label(self, val):
        self._label = val

    @property
    def is_valid(self):
        if not self._is_validated:
            self.validate()
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value):
        self._is_valid = value
        self._is_validated = True

    def validate(self):
        if not self._is_validated:
            self._is_validated = True
            for validator in self.validators:
                try:
                    validator.validate(self, self._schema)
                except ValidationError:
                    self._is_valid = False
                    # Do not run subsequent validators, because field is
                    # already invalid.
                    break

    def add_error(self, message):
        if message:
            self.errors.append(message)


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
        self._is_valid = True
        self._is_validated = False
        self._fields = {}
        for name, field in iteritems(self._unbound_fields):
            self._fields[name] = field.__class__(*field._args, **field._kwargs)
            self._fields[name]._schema = self
            self._fields[name].name = name

        if isinstance(data, dict):
            for name, value in iteritems(data):
                self._add_data_to_field(name, value)
        else:
            for name in dir(data):
                if not name.startswith('_'):
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
            self[name]._cleaned_data = value

    def validate(self):
        """ Validate fields values if they are not validated.
        Set schema validation status.
        """
        if not self._is_validated:
            for field in self.values():
                if not field.is_valid:
                    self._is_valid = False
            self._is_validated = True

    @property
    def is_valid(self):
        """ Return schema validation status. Run `validate` if needed.
        """
        if not self._is_validated:
            self.validate()
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value):
        self._is_valid = value

    def get_errors(self):
        """ Return a dict of field_name: [field_errors].
        """
        if not self._is_validated:
            self.validate()
        return {name: field.errors for name, field in self.items()
                if field.errors}
