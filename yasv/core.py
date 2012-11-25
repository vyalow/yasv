from yasv.validators import ValidationError, Validator


__all__ = ['Schema', 'Field']


class Field(object):

    def __init__(self, *args):
        self.validators = []
        self.label = None

        for arg in args:
            if isinstance(arg, (str, unicode)):
                self.label = arg
            elif isinstance(arg, Validator):
                self.validators.append(arg)


class Schema(object):

    def __init__(self, schema):
        self._schema = schema

    def validate(self, data):
        is_valid = True
        error_response = {}
        for schema_key, schema_field in self._schema.iteritems():
            value = data.get(schema_key)
            error_response.update({
                schema_key: {
                    'value': value,
                    'label': schema_field.label,
                    'errors': [],
                }
            })
            for validator in schema_field.validators:
                try:
                    value = validator.validate(value)
                except ValidationError, e:
                    is_valid = False
                    error_response[schema_key]['errors'].append(e.message)

            data[schema_key] = value

        if is_valid:
            return data
        else:
            e = ValidationError()
            e.error_response = error_response
            raise e
